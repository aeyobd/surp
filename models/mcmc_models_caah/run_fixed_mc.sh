#!/bin/bash
rm -rf *.csv
set -e
python ../mcmc_models_1d/bin_models.py $1
julia -t 4 run_fixed_fagb.jl "$@"
