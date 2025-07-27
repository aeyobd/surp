#!/bin/bash
rm -rf $1/*.csv
rm -rf $1/*.pdf
rm -rf $1/log.pdf

set -e
python bin_models.py $1 # just for reference
python bin_2d.py $1 

julia -t 4 run_2d_lin_mc.jl "$@"
