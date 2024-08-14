#!/bin/bash


# this is finicky on some systems...
PYTHON=python

function print_help {
    echo Usage: $0 modelpath runpath parampath yieldpath ;
    echo
    echo Runs a VICE model with the given parameters and yields. 
    echo modelpath: path to the directory containing the model
    echo runpath: path to the directory containing the run script
}


# Check if at least one positional argument is provided
if [ $(( $# - $OPTIND )) -lt 0 ]; then
    print_help
    exit 1
fi

MODEL_DIR=${@:$OPTIND:1}

set -x

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )

cd $MODEL_DIR

SCRIPTNAME="run.py"
if [ -f $SCRIPTNAME ]; then
    echo "Found $SCRIPTNAME"
elif [ -f ../$SCRIPTNAME ]; then
    SCRIPTNAME="../$SCRIPTNAME"
elif [ -f $SCRIPT_DIR/$SCRIPTNAME ]; then
    SCRIPTNAME="$SCRIPT_DIR/$SCRIPTNAME"
else
    echo "Error: $SCRIPTNAME not found"
    exit 1
fi

PARAMSPATH=params.toml
YIELDSPATH=yield_params.toml

$PYTHON $SCRIPTNAME $PARAMSPATH $YIELDSPATH

cd $SCRIPT_DIR

echo visualizing model >> log.out
$PYTHON visualize.py $MODEL_DIR -o . >> log.out

