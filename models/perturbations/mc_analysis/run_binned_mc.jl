using CSV, DataFrames
using Turing
using LinearAlgebra: diagm
import TOML


function main()
    if length(ARGS) < 1
        println("Usage: julia run_binned_mc.jl <modelname>")
        return
    end

    modelname = ARGS[1]

    @info "loading models"
    ah, afe = load_binned_models(modelname)

    @info "parsing parameters"
    params = TOML.parsefile(joinpath(modelname, "params.toml"))

    
    labels = String[]
    priors = Distribution{Univariate, Continuous}[]

    for (key, val) in params
        push!(labels, key)
        prior = make_distribution(val["prior"], val["prior_args"])

        push!(priors, prior)
    end

    println(priors)

    @info "creating model"
    model = n_component_model(ah, afe, labels, priors)

    @info "running MCMC"
    chain = sample(model, NUTS(0.65), 10_000)
    samples = DataFrame(chain)

    rename!(samples, ["params[$i]" => labels[i] for i in eachindex(labels)]...)

    outfile = joinpath(modelname, "mcmc_samples.csv")
    @info "writing output"
    CSV.write(outfile, samples)

    @info "done"
end

function make_distribution(kind, args)
    dist = getproperty(Distributions, Symbol(kind))

    return dist(args...)
end


"""
Loads the binned models from a given model directory
from the files `mg_fe_binned.csv` and `mg_h_binned.csv`
"""
function load_binned_models(modelname)
    dir = "$modelname"

    afe = CSV.read(dir * "/mg_fe_binned.csv", DataFrame)
    ah = CSV.read(dir * "/mg_h_binned.csv", DataFrame)

    return ah, afe
end



# Helper function to compute model contribution
function compute_model_contribution(params, model)
    return sum(p * model[key] for (p, key) in zip(params, keys(model)))
end


@model function n_component_model(models_ah, models_afe, labels, priors)
    # Create parameters based on the specified priors
    params ~ arraydist(priors)
    
    # Compute model contributions for each dataset
    mu_ah = sum(p * models_ah[:, key] for (p, key) in zip(params, labels))
    mu_afe = sum(p * models_afe[:, key] for (p, key) in zip(params, labels))
    
    # Data likelihoods
    models_ah.obs ~ MvNormal(mu_ah, diagm(models_ah.obs_err .^ 2))
    models_afe.obs ~ MvNormal(mu_afe, diagm(models_afe.obs_err .^ 2))
end

if abspath(PROGRAM_FILE) == @__FILE__
    main()
end
