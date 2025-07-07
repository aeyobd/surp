using CSV, DataFrames
using Turing
using LinearAlgebra: diagm
import TOML
using ArgParse

include("emcee_utils.jl")

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
        "-e", "--ensemble"
            help = "Use emcee's ensemble sampler"
            action = "store_true"
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
    ah, _ = load_binned_models(modelname)

    params = TOML.parsefile(joinpath(modelname, "params.toml"))
    labels, priors = make_labels_priors(params)

    @info "creating model"
    model = n_component_model(ah, labels, priors)

    @info "running MCMC"
    if args["ensemble"]
        chain = sample_emcee(model, args["num-steps"])
    else
        @info "running MCMC"
        n_chains = ceil(Int, args["chains"] / args["threads"])

        chain = mapreduce(
            c ->sample(model, NUTS(0.65), MCMCThreads(), args["num-steps"], args["threads"]),
            chainscat, 1:n_chains)
    end

    samples = DataFrame(chain)
    @info "writing output"
    # give columns nicer names 
    rename!(samples, ["params[$i]" => labels[i] for i in eachindex(labels)]...)

    outfile = joinpath(modelname, "mcmc_samples.csv")
    CSV.write(outfile, samples)

end

function make_distribution(kind, args)
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



@model function n_component_model(models_ah, labels, priors)
    # Create parameters based on the specified priors
    params ~ arraydist(priors)
    
    # Compute model contributions for each dataset
    mu_ah = sum(p * models_ah[:, key] for (p, key) in zip(params, labels))
    sem_ah = sum(p * models_ah[:, Symbol("$(key)_err")] ./ sqrt.(models_ah[:, Symbol("_counts")])  for (p, key) in zip(params, labels))

    sigma_ah = models_ah.obs_err ./ sqrt.(models_ah.obs_counts)

    sigma2_ah = @. sigma_ah^2 + sem_ah^2 

    # Data likelihoods
    models_ah.obs ~ MvNormal(mu_ah, diagm(sigma2_ah))
end

if abspath(PROGRAM_FILE) == @__FILE__
    main()
end
