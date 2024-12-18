#!/bin/bash
#
#
function print_help {
    echo Submits a job to run a vice model
    echo Usage: $0 [-aph] MODEL_DIR ;
    echo -a: copy full vice outputs
    echo -m: specify memory
    echo -t: time limit 
    # echo -p: make plots
    echo -h: print this message 
}


# default args
COPY_VICE=false
MAKE_PLOTS=false
REQUESTED_MEMORY="4gb"
TIME_LIMIT="0:20:00"

# Iterate over all the arguments
#
while getopts 'aphm:t:' OPTION; do
    case "$OPTION" in
        a) COPY_VICE=true ;;
        # p) MAKE_PLOTS=true ;;
        m) REQUESTED_MEMORY=$OPTARG ;;
        t) TIME_LIMIT=$OPTARG ;;
        h) print_help; exit 0 ;;
        \?) echo "Unknown option: -$OPTARG" >&2; exit 1;;
    esac
done


# Check if at least one positional argument is provided
if [ $(( $# - $OPTIND )) -lt 0 ]; then
    print_help
    exit 1
fi


MODEL_NAME=${@:$OPTIND:1}

if [[ ! -d "$MODEL_NAME" ]]; then
    echo "Error: not a valid model $MODEL_NAME"
    exit 1
fi

NTHREADS=1

if [  "$COPY_VICE" = true ] ; then
    echo will copy full vice output
fi

SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
echo "Script dir: $SCRIPT_DIR"

cd $MODEL_NAME




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

# Files to check before removing
rm -rf *.out model.json stars.csv *.dat milkway.vice

echo "Submitting Job" $MODEL_NAME
bash <<EOT
#!/bin/bash
#SBATCH --time=$TIME_LIMIT
#SBATCH --ntasks=$NTHREADS
#SBATCH --cpus-per-task=1
#SBATCH --mem=$REQUESTED_MEMORY
#SBATCH --job-name=$MODEL_NAME
#SBATCH --mail-type=BEGIN,END,FAIL
#SBATCH --output=%j.out
#SBATCH --account=$SLURM_ACCOUNT


set -xe
echo job \$SLURM_JOB_ID
echo \$TMPDIR
echo \$SLURM_SUBMIT_DIR
export OMP_NUM_THREADS=$NTHREADS

cp $SCRIPTNAME \$TMPDIR
cd \$TMPDIR


python run.py \$SLURM_SUBMIT_DIR/params.toml \$SLURM_SUBMIT_DIR/yield_params.toml


cp model.json \$SLURM_SUBMIT_DIR
cp stars.csv \$SLURM_SUBMIT_DIR

python $SCRIPT_DIR/visualize.py .
cp *.pdf \$SLURM_SUBMIT_DIR

if [ "$COPY_VICE" = true ]; then
    cp -f *.dat \$SLURM_SUBMIT_DIR
    cp -rf milkyway.vice \$SLURM_SUBMIT_DIR
fi

scontrol show job=\$SLURM_JOB_ID

EOT

