using PythonCall
emcee = pyimport("emcee")


function sample_emcee(model, steps; nwalkers=nothing, progress=true, kwargs...)
    model_labels = bijector(model, Val(true))[2]

    # these are a named tuple
    variables = keys(model_labels) |> collect
    # add up number of indicies in bijection for dimensionality
    ndim = sum(length(vcat(idxs...)) for idxs in model_labels)
    
    if nwalkers === nothing
        nwalkers = 2*ndim
    end
    
    function py_log_prob(theta)
        vars = (; [k => theta[model_labels[k]...] for k in variables]...)
        lp = logprior(model, vars)
        if isfinite(lp)
            lp += loglikelihood(model, vars)
        end
            
        return lp
    end

    # sample from prior for initial conditions
    samples_prior = sample(model, Prior(), nwalkers)
    p0 = samples_prior.value[:, 1:ndim, 1].data

    # python run
    sammy = emcee.EnsembleSampler(nwalkers, ndim, py_log_prob)
    sammy.run_mcmc(p0, steps; progress=progress, kwargs...)

    #convert back to julia object
    chain = pyconvert(Array{Float64}, sammy.get_chain())
    chain = permutedims(chain, (1, 3, 2)) # emcee orderes differently
    varnames = samples_prior.name_map.parameters
    chain = Chains(chain, varnames)

    return chain
end
