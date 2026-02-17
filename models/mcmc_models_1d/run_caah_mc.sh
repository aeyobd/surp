#!/bin/bash
rm -rf *.csv
set -e
python bin_models.py $1
julia -t 4 run_caah_mc.jl "$@"
