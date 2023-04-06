#!/bin/bash

for f_agb in 0.2 # 0.4 0.1
do
  for beta in 0.001 # 0.002 0.0005
  do
    for model in "C11"  #"K10" "V13" "K16"
    do
      for eta in 1
      do
        bash osc/run.sh -f $f_agb -b $beta -m $model -e $eta
      done
    done
  done
done
