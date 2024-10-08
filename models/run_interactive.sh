#!/bin/bash
# a short script to run a model in the background

function print_help {
    echo Runs a VICE model
    echo Usage: $0 MODEL_DIR ;
}


# Check if at least one positional argument is provided
if [ $(( $# - $OPTIND )) -lt 0 ]; then
    echo "Requires one argument"
    print_help
    exit 1
fi


MODEL_NAME=${@:$OPTIND:1}

# check if model exists
if [[ ! -d "$MODEL_NAME" ]]; then
    echo "Error: not a valid model $MODEL_NAME"
    print_help
    exit 1
fi

echo removing files in model
#rm -rf $MODEL_NAME/milkyway.vice
rm -f $MODEL_NAME/model.json $MODEL_NAME/err.out $MODEL_NAME/log.out
rm -f $MODEL_NAME/stars.csv $MODEL_NAME/*.pdf


echo submitting job $MODEL_NAME
bash ./run.sh $MODEL_NAME > $MODEL_NAME/log.out 2> $MODEL_NAME/err.out &

