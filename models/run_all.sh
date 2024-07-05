# this is finicky on some systems...
PYTHON=python


function print_help {
    echo Runs a VICE model
    echo Usage: $0 modelpath runpath parampath yieldpath ;
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

# Files to check before removing
# rm -rf *.out model.json stars.csv *.dat milkway.vice

$PYTHON $SCRIPTNAME $PARAMSPATH $YIELDSPATH

cd $SCRIPT_DIR

echo visualizing model >> log.out
$PYTHON visualize.py $MODEL_DIR -o . >> log.out

