#!/bin/bash
python bin_models.py $1
julia run_binned_mc.jl "$@"
