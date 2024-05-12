#!/bin/sh
#

./make_params.py -F -f 0.1
./make_params.py -F -f 0.2
./make_params.py -F -f 0.3

./make_params.py -F -z 0.0008
./make_params.py -F -z 0.0016
./make_params.py -F -z 0.0024

./make_params.py -F --m_factor 1.5 -f 0.1
./make_params.py -F -i 1.2 -f 0.3
./make_params.py -F -R exp

./make_params.py -F -s lateburst
./make_params.py -F -e 2

