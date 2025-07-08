using CSV, DataFrames
using Turing
using LinearAlgebra: diagm
import TOML
using ArgParse
using Random


struct ConstDist  <: ContinuousUnivariateDistribution
    mean::Float64
end

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
            default = 3_000
        "-t", "--threads"
            help = "Number of threads"
            arg_type = Int
            default = 4
        "-c", "--chains"
            help = "Total number of chains"
            arg_type = Int
            default = 16
    end

    args = parse_args(s)

    args["num-steps"] = convert(Int, args["num-steps"])
    return args
end


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
    model = n_component_model(binned_model, all_labels, priors, sigma_prior)

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

end


function make_distribution(kind, args)
    if kind == "Normal" && args[2] == 0.0
        return ConstDist(args[1])
    elseif kind == "TruncNormal"
        low = args[3]
        high = args[4]
        dist = Normal(args[1:2]...)
        return truncated(dist, low, high)
    end


    dist = getproperty(Distributions, Symbol(kind))
    return dist(args...)
end


function make_labels_priors(params)
    labels = String[]
    priors = Distribution{Univariate, Continuous}[]
    sigma_prior = ConstDist(0.0)

    for (key, val) in params
        prior = make_distribution(val["prior"], val["prior_args"])
        if key == "sigma_int"
            sigma_prior = prior
            @info "sigma prior: $prior" 
        else
            push!(labels, key)
            push!(priors, prior)
        end
    end

    is_const = [p isa ConstDist for p in priors]
    idx = eachindex(is_const)
    idx = sort(idx, by = i -> !is_const[i])
    labels = labels[idx]
    priors = priors[idx]

    return labels, priors, sigma_prior
end



"""
Loads the binned models from a given model directory
from the files `mg_fe_binned.csv` and `mg_h_binned.csv`
"""
function load_binned_models(modelname)
    dir = "$modelname"

    afe = CSV.read(dir * "/2d_binned.csv", DataFrame)

    disallowmissing!(afe)
    return afe
end



@model function n_component_model(models, labels, priors, sigma_prior)
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

    if sigma_prior isa ConstDist
        sigma_int = sigma_prior.mean
    else
        sigma_int ~ sigma_prior
    end

    const_params = [p.mean for p in priors[is_const]]
    all_params = vcat(const_params, params)
    
    # Compute model contributions for each dataset
    mu = sum(p * models[:, key] for (p, key) in zip(all_params, labels))
    # linear variance added since not independent!
    sigma_model = sum(abs.(p) .* models[:, Symbol("$(key)_err")] ./ sqrt.(models[:, Symbol("_counts")])  for (p, key) in zip(all_params, labels))

    sigma2_obs = @. models.obs_err^2 ./ models.obs_counts


    if any(mu .< 0) || any(sigma_model .<= 0)
        Turing.@addlogprob! -Inf
        return nothing
    end

    log_sigma2_obs = sigma2_obs ./ models.obs .^ 2
    log_sigma_model = sigma_model ./ mu
    log_sigma2 = @. sigma_int^2 + log_sigma2_obs + log_sigma_model^2

    # Data likelihoods
    log_mu = log.(mu)
    models.obs ~ MvLogNormal(log_mu, diagm(log_sigma2))
end

if abspath(PROGRAM_FILE) == @__FILE__
    main()
end
