#!/bin/bash

for f_agb in 0.2
do
  for beta in 0.4
  do
    for model in "cristallo11"
    do
      for eta in 1
      do
        echo "f_agb = $f_agb"
        echo "eta/eta_0 = $eta"
        echo "beta = $beta"
        echo "model = $model"

        sbatch gridrun.sh $f_agb $beta $model $eta
        echo "submitted"
      done
    done
  done
done