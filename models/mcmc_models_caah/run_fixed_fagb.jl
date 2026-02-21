using CSV, DataFrames
using Turing
using LinearAlgebra: diagm
import TOML
using ArgParse

include("../mcmc_models_1d/emcee_utils.jl")
include("../mcmc_models_1d/run_binned_mc.jl")

# This model samples all parameters except 
# alpha, which is set based on the specified fraction
# of agb contribution, using the y0 parameters

function main()
    args = get_args()
    modelname = args["modelname"]

    @info "loading parameters and models"
    ah, _ = load_binned_models(modelname)

    params = TOML.parsefile(joinpath(modelname, "params.toml"))
    labels, priors, y0s, f_agb, y0_agb = make_labels_priors(params)

    @info "creating model"
    model = caah_model(ah, labels, priors, y0s, f_agb, y0_agb)

    @info "running MCMC"
    n_chains = ceil(Int, args["chains"] / args["threads"])

    chain = mapreduce(
        c ->sample(model, NUTS(0.65), MCMCThreads(), args["num-steps"], args["threads"]),
        chainscat, 1:n_chains)

    samples = DataFrame(chain)
    @info "writing output"
    # give columns nicer names 

    outfile = joinpath(modelname, "mcmc_samples.csv")
    CSV.write(outfile, samples)

    summary = summarize_chain(chain, [labels..., "alpha"])
    summary_file = joinpath(modelname, "mcmc_summary.csv")
    CSV.write(summary_file, summary)
end


function make_labels_priors(params)
    labels = String[]
    priors = Distribution{Univariate, Continuous}[]
    y0s = Float64[]
    y0_agb = NaN
    f_agb = NaN

    for (key, val) in params

        if key == "alpha"
            f_agb = params[key]["f_agb"]
            y0_agb = params[key]["y0"]
        else
            prior = make_distribution(val["prior"], val["prior_args"])
            push!(labels, key)
            push!(priors, prior)
            push!(y0s, params[key]["y0"])
        end
    end

    return labels, priors, y0s, f_agb, y0_agb
end




@model function caah_model(models_ah, labels, priors, y0s, 
        f_agb::Real, y0_agb::Real)
    sampled_params ~ arraydist(priors)

    y_cc = sum(y0s .* sampled_params)
    y_agb = f_agb * y_cc / (1 - f_agb)
    alpha := y_agb / y0_agb

    allparams = vcat(sampled_params, alpha)
    alllabels = vcat(labels, "alpha")

    
    # Compute model contributions for each dataset
    mu_ah = sum(p * models_ah[:, key] for (p, key) in zip(allparams, alllabels))
    std_var = [models_ah[:, Symbol("$(key)_err")] .^2 ./ models_ah[:, Symbol("_counts")]   for key in alllabels]

    sigma2_model = sum(allparams .^ 2 .* std_var)

    sigma2_ah = models_ah.obs_err .^ 2 ./ models_ah.obs_counts

    sigma2_tot = @. sigma2_ah + sigma2_model

    # Data likelihoods
    models_ah.obs ~ MvNormal(mu_ah, diagm(sigma2_ah))
end




if abspath(PROGRAM_FILE) == @__FILE__
    main()
end
