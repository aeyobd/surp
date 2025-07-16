using CSV, DataFrames
using Turing
using LinearAlgebra: diagm
import TOML
using ArgParse
using Random


struct ConstDist  <: ContinuousUnivariateDistribution
    mean::Float64
end

include("run_2d_mc.jl")

function main()
    args = get_args()
    modelname = args["modelname"]

    @info "loading parameters and models"
    binned_model = load_binned_models(modelname)

    params = TOML.parsefile(joinpath(modelname, "params.toml"))
    params = Dict(key => val for (key, val) in params if val isa Dict)
    all_labels, priors, sigma_prior = make_labels_priors(params)

    @info "labels = $all_labels"
    @info "priors = $priors"

    @info "creating model"
    model = n_component_lin_model(binned_model, all_labels, priors, sigma_prior)

    @info "running MCMC"
    n_chains = ceil(Int, args["chains"] / args["threads"])

    chain = mapreduce(
        c ->sample(model, NUTS(0.65), MCMCThreads(), args["num-steps"], args["threads"]),
        chainscat, 1:n_chains)

    samples = DataFrame(chain)

    @info "writing output"
    is_const = [p isa ConstDist for p in priors]
    # give columns nicer names 
    #
    labels = all_labels[.!is_const]
    rename!(samples, ["params[$i]" => labels[i] for i in eachindex(labels)]...)

    outfile = joinpath(modelname, "mcmc_samples.csv")

    CSV.write(outfile, samples)
    if sigma_prior isa ConstDist
        push!(labels, "sigma_int")
    end

    summary = summarize_chain(chain, labels)
    summary_file = joinpath(modelname, "mcmc_summary.csv")
    CSV.write(summary_file, summary)
end



@model function n_component_lin_model(models, labels, priors, sigma_prior)
    # Create parameters based on the specified priors
    #
    is_const = [p isa ConstDist for p in priors]
    check_const_order(is_const)

    # only sample non-constant parameters.
    params ~ arraydist(priors[.!is_const])

    if sigma_prior isa ConstDist
        sigma_int = sigma_prior.mean
    else
        sigma_int ~ sigma_prior
    end

    const_params = [p.mean for p in priors[is_const]]
    all_params = vcat(const_params, params)
    
    # Compute model contributions for each dataset
    mu = sum(p * models[:, key] for (p, key) in zip(all_params, labels))
    # add standard deviations instead of variances.
    sigma_model = sum(p .* models[:, Symbol("$(key)_sem")] 
                      for (p, key) in zip(all_params, labels))

    sigma2_obs = models.obs_sem .^2 

    sigma2 = @. sigma2_obs + sigma_model^2 + sigma_int^2

    # Data likelihoods
    models.obs ~ MvNormal(mu, diagm(sigma2))
end


if abspath(PROGRAM_FILE) == @__FILE__
    main()
end
