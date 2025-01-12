using CSV, DataFrames
using Turing
using LinearAlgebra: diagm
import TOML
using ArgParse
using Random


struct ConstDist  <: ContinuousUnivariateDistribution
    mean::Float64
end

function Base.rand(rng::AbstractRNG, d::ConstDist)
    return d.mean
end

Distributions.minimum(d::ConstDist) = d.mean
Distributions.maximum(d::ConstDist) = d.mean
Distributions.logpdf(d::ConstDist, x) = x == d.mean ? 0.0 : -Inf
Distributions.cdf(d::ConstDist, x) = x < d.mean ? 0.0 : 1.0
Distributions.sampler(d::ConstDist) = d
Distributions.insupport(d::ConstDist, x) = x == d.mean
Distributions.quantile(d::ConstDist, p) = d.mean


function get_args()
    s = ArgParseSettings(
        description = """runs a MCMC model from a binned multi-component multizone model
        created with bin_models.py""",
        version = "0.1.0",
    )

    @add_arg_table s begin
        "modelname"
            help="Input model name (a folder in this directory)"
            required = true
        "-n", "--num-steps"
            help = "The number of steps to take in the MCMC"
            arg_type = Float64
            default = 10_000
    end

    args = parse_args(s)

    args["num-steps"] = convert(Int, args["num-steps"])
    return args
end


function main()
    args = get_args()
    modelname = args["modelname"]

    @info "loading parameters and models"
    ah, afe = load_binned_models(modelname)

    params = TOML.parsefile(joinpath(modelname, "params.toml"))
    params = Dict(key => val for (key, val) in params if val isa Dict)
    all_labels, priors = make_labels_priors(params)
    println("labels = ", all_labels)
    println("priors = ", priors)

    @info "creating model"
    model = n_component_model(ah, afe, all_labels, priors)

    @info "running MCMC"
    chain = sample(model, NUTS(0.65), args["num-steps"])
    samples = DataFrame(chain)

    @info "writing output"
    is_const = [p isa ConstDist for p in priors]
    # give columns nicer names 
    #
    labels = all_labels[.!is_const]
    rename!(samples, ["params[$i]" => labels[i] for i in eachindex(labels)]...)

    outfile = joinpath(modelname, "mcmc_samples.csv")
    CSV.write(outfile, samples)

end

function make_distribution(kind, args)
    if kind == "Normal" && args[2] == 0.0
        return ConstDist(args[1])
    end

    dist = getproperty(Distributions, Symbol(kind))
    return dist(args...)
end

function make_labels_priors(params)
    labels = String[]
    priors = Distribution{Univariate, Continuous}[]

    for (key, val) in params
        prior = make_distribution(val["prior"], val["prior_args"])
        push!(labels, key)
        push!(priors, prior)
    end

    is_const = [p isa ConstDist for p in priors]
    idx = eachindex(is_const)
    idx = sort(idx, by = i -> !is_const[i])
    labels = labels[idx]
    priors = priors[idx]

    return labels, priors
end



"""
Loads the binned models from a given model directory
from the files `mg_fe_binned.csv` and `mg_h_binned.csv`
"""
function load_binned_models(modelname)
    dir = "$modelname"

    afe = CSV.read(dir * "/mg_fe_binned.csv", DataFrame)
    ah = CSV.read(dir * "/mg_h_binned.csv", DataFrame)

    disallowmissing!(ah)
    disallowmissing!(afe)
    return ah, afe
end



@model function n_component_model(models_ah, models_afe, labels, priors)
    # Create parameters based on the specified priors
    #
    is_const = [p isa ConstDist for p in priors]
    dc = sum(diff(is_const))
    if dc == 1
        @assert is_const[1] && !is_const[end] "all const parameters must be at the beginning of the parameter list."
    elseif dc > 1
        error("All const parameters must be at the beginning of the parameter list.")
    end
        

    params ~ arraydist(priors[.!is_const])

    const_params = [p.mean for p in priors[is_const]]
    all_params = vcat(const_params, params)
    
    # Compute model contributions for each dataset
    mu_ah = sum(p * models_ah[:, key] for (p, key) in zip(all_params, labels))
    mu_afe = sum(p * models_afe[:, key] for (p, key) in zip(all_params, labels))
    sem_ah = sum(p * models_ah[:, Symbol("$(key)_err")] ./ sqrt.(models_ah[:, Symbol("_counts")])  for (p, key) in zip(all_params, labels))
    sem_afe = sum(p * models_afe[:, Symbol("$(key)_err")] ./ sqrt.(models_afe[:, Symbol("_counts")]) for (p, key) in zip(all_params, labels))

    sigma_ah = models_ah.obs_err ./ sqrt.(models_ah.obs_counts)
    sigma_afe = models_afe.obs_err ./ sqrt.(models_afe.obs_counts)

    sigma2_ah = @. sigma_ah^2 + sem_ah^2 
    sigma2_afe = @. sigma_afe^2 + sem_afe^2

    # Data likelihoods
    models_ah.obs ~ MvNormal(mu_ah, diagm(sigma2_ah))
    models_afe.obs ~ MvNormal(mu_afe, diagm(sigma2_afe))
end

if abspath(PROGRAM_FILE) == @__FILE__
    main()
end
