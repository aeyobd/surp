#!/bin/bash

# if your system requires a specific python executable. 
PYTHON=python

function print_help {
    echo Usage: $0 modelpath
    echo
    echo Runs a VICE model in the directory modelpath.
    echo assumes that the parameterfiles params.toml and yield_params.toml 
    echo are present in the modelpath.
    echo Searches for the run.py script in the modelpath, or in the parent, or in the current 
    echo directory.
    echo Additionally runs visualize.py to create figures in the model directory.
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

