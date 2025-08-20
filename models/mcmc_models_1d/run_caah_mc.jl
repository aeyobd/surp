using CSV, DataFrames
using Turing
using LinearAlgebra: diagm
import TOML
using ArgParse

include("emcee_utils.jl")
include("run_binned_mc.jl")


function main()
    args = get_args()
    modelname = args["modelname"]

    @info "loading parameters and models"
    ah, _ = load_binned_models(modelname)

    params = TOML.parsefile(joinpath(modelname, "params.toml"))
    labels, priors = make_labels_priors(params)

    @info "creating model"
    model = caah_model(ah, labels, priors)

    @info "running MCMC"
    n_chains = ceil(Int, args["chains"] / args["threads"])

    chain = mapreduce(
        c ->sample(model, NUTS(0.65), MCMCThreads(), args["num-steps"], args["threads"]),
        chainscat, 1:n_chains)

    samples = DataFrame(chain)
    @info "writing output"
    # give columns nicer names 

    is_const = [p isa ConstDist for p in priors]

    rename!(samples, ["sampled_params[$i]" => labels[.!is_const][i] for i in eachindex(labels[.!is_const])]...)

    outfile = joinpath(modelname, "mcmc_samples.csv")
    CSV.write(outfile, samples)

    summary = summarize_chain(chain, labels[.!is_const])
    summary_file = joinpath(modelname, "mcmc_summary.csv")
    CSV.write(summary_file, summary)
end


@model function caah_model(models_ah, labels, priors)
    # Create parameters based on the specified priors
    is_const = [p isa ConstDist for p in priors]
    check_const_order(is_const)

    sampled_params ~ arraydist(priors[.!is_const])

    const_params = [p.mean for p in priors[is_const]]
    params = vcat(const_params, sampled_params)

    
    # Compute model contributions for each dataset
    mu_ah = sum(p * models_ah[:, key] for (p, key) in zip(params, labels))
    sigma2_model = sum(p .^ 2 * models_ah[:, Symbol("$(key)_err")] .^2 ./ models_ah[:, Symbol("_counts")]  for (p, key) in zip(params, labels))

    sigma2_ah = models_ah.obs_err .^ 2 ./ models_ah.obs_counts

    sigma2_tot = @. sigma2_ah + sigma2_model

    # Data likelihoods
    models_ah.obs ~ MvNormal(mu_ah, diagm(sigma2_ah))
end



function check_const_order(is_const)
    dc = sum(diff(is_const))
    if dc == 1
        @assert is_const[1] && !is_const[end] "all const parameters must be at the beginning of the parameter list."
    elseif dc > 1
        error("All const parameters must be at the beginning of the parameter list.")
    end
end


function summarize_chain(chain, labels; p=0.16)
    df = DataFrame(chain)
    summary = DataFrame(Turing.summarize(chain))

    Nr = size(summary, 1)
    meds = zeros(Nr)
    err_low = zeros(Nr)
    err_high = zeros(Nr)
    
    for i in 1:Nr
        sym = summary[i, :parameters]
        meds[i] = median(df[!, sym])
        err_low[i] = meds[i] - quantile(df[!, sym], p)
        err_high[i] = quantile(df[!, sym], 1-p) - meds[i]
    end

    summary[!, :median] = meds
    summary[!, :err_low] = err_low
    summary[!, :err_high] = err_high
    summary[!, :parameters] = labels

    # reorder columns
    select!(summary, :parameters, :median, :err_low, :err_high, Not([:parameters, :median, :err_low, :err_high]))
    return summary
end


if abspath(PROGRAM_FILE) == @__FILE__
    main()
end
