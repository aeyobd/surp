using CSV, DataFrames
import CategoricalArrays: cut
using StatsBase
using OrderedCollections
using Turing

import NaNMath as nm
using LinearAlgebra: diagm


@model function n_component_model(x, y, y_e, x2, y2, y_e2, models, models2; m_h_0=mg_h_0)
    y0_cc ~ Normal(2, 1)
    α ~ Normal(2, 1)
    ζ ~ Normal(0, 1)

    Zc = y0_cc * models[:y0_cc] .+ α * models[:alpha] .+ ζ * models[:zeta_cc]

    mu = Zc_to_C_H.(Zc) .- x
    y1_pred = mu

    Zc2 = y0_cc * models2[:y0_cc] .+ α * models2[:alpha] .+ ζ * models2[:zeta_cc]
    mu2 = Zc_to_C_H.(Zc2) .- mg_h_0

    
    y ~ MvNormal(mu, diagm(y_e .^ 2))
    y2 ~ MvNormal(mu2,  diagm(y_e2 .^ 2))
end



function load_model(modelname)
    filename = "../$modelname/binned_ah.csv"
    df_ah = CSV.read(filename, DataFrame)

    filename = "../$modelname/binned_afe.csv"
    df_afe = CSV.read(filename, DataFrame)

    observed_ah = df_ah[:, "observed"]
    observed_afe = df_afe[:, "observed"]

    models_ah = Dict{String, Vector{Float64}}()
    models_afe = Dict{String, Vector{Float64}}()

    for col in names(df_ah)
        if col != "observed"
            models_ah[col] = df_ah[:, col]
            models_afe[col] = df_afe[:, col]
        end
    end

    return observed_ah, observed_afe, models_ah, models_afe
end



