#!/bin/bash

if [ $# -lt 1 ]; then
    echo "Usage: $0 <model_dir> ..."
    exit 1
fi

if [ ! -d $1 ]; then
    echo "Error: no such directory $1"
    exit 1
fi

set -x
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

for arg in $@; do
    cd $SCRIPT_DIR

    if [ ! -d "$arg" ]; then
        echo "warning: no such directory $arg"
    else
        echo "cleaning $arg"
        cd "$arg"
        rm -f *.pdf
        rm -f model.json
        rm -f *.out *.err
        rm -f *.csv
        rm -f *.dat
        rm -f -r *.vice
    fi
done
