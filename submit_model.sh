#!/bin/bash

for f_agb in 0.2 # 0.4 0.1
do
  for beta in 0 # 0.002 0.0005
  do
    for model in "C11"  "K10" "V13" "K16"
    do
      for eta in 1 # 0.3
      do
        echo "f_agb = $f_agb"
        echo "eta/eta_0 = $eta"
        echo "beta = $beta"
        echo "model = $model"

        bash osc/run.sh -f $f_agb -b $beta -m $model -e $eta -o
      done
    done
  done
done
