#!/bin/bash

for f_agb in 0.2
do
  for beta in 0.4
  do
    for model in "cristallo11" # "karakas10" "ventura13" "karakas16"
    do
      for eta in 0.3
      do
        echo "f_agb = $f_agb"
        echo "eta/eta_0 = $eta"
        echo "beta = $beta"
        echo "model = $model"

        sbatch gridrun.sh -f $f_agb -b $beta -m $model -e $eta -l -i 0.8
        echo "submitted"
      done
    done
  done
done