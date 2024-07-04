#!/bin/bash


function print_help {
    echo Runs a VICE model
    echo Usage: $0 MODEL_DIR ;
}


# Iterate over all the arguments
#
while getopts 'h' OPTION; do
    case "$OPTION" in
        h) print_help; exit 0 ;;
        \?) echo "Unknown option: -$OPTARG" >&2; exit 1;;
    esac
done

# Check if at least one positional argument is provided
if [ $(( $# - $OPTIND )) -lt 0 ]; then
    print_help
    exit 1
fi


SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
echo "Script dir: $SCRIPT_DIR"


MODEL_NAME=${@:$OPTIND:1}

if [[ ! -d "$MODEL_NAME" ]]; then
    echo "Error: not a valid model $MODEL_NAME"
    exit 1
fi



echo submitting job

nohup bash ./run_all.sh $MODEL_NAME > $MODEL_NAME/log.out &
