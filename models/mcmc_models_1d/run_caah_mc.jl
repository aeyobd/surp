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
    rename!(samples, ["params[$i]" => labels[i] for i in eachindex(labels)]...)

    outfile = joinpath(modelname, "mcmc_samples.csv")
    CSV.write(outfile, samples)

end


@model function caah_model(models_ah, labels, priors)
    # Create parameters based on the specified priors
    params ~ arraydist(priors)
    
    # Compute model contributions for each dataset
    mu_ah = sum(p * models_ah[:, key] for (p, key) in zip(params, labels))
    sigma2_model = sum(p .^ 2 * models_ah[:, Symbol("$(key)_err")] .^2 ./ models_ah[:, Symbol("_counts")]  for (p, key) in zip(params, labels))

    sigma2_ah = models_ah.obs_err .^ 2 ./ models_ah.obs_counts

    sigma2_tot = @. sigma2_ah + sigma2_model

    # Data likelihoods
    models_ah.obs ~ MvNormal(mu_ah, diagm(sigma2_ah))
end

if abspath(PROGRAM_FILE) == @__FILE__
    main()
end
