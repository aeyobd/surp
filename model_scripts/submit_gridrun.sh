#!/bin/bash

for f_agb in 0.2 0.5
do
  for beta in 0 0.3
  do
    for model in "cristallo11" "karakas16"
    do
      for eta in 1 0.3
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
