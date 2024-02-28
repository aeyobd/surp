#!/bin/bash
#
#
function print_help {
    echo Submits a job to run a vice model
    echo Usage: $0 [-aph] MODEL_DIR ;
    echo -a: copy full vice outputs
    echo -p: make plots
    echo -h: print this message 
}


COPY_VICE=false
MAKE_PLOTS=false
# Iterate over all the arguments
#
while getopts 'aph' OPTION; do
    case "$OPTION" in
        a) COPY_VICE=true ;;
        p) MAKE_PLOTS=true ;;
        h) print_help; exit 0 ;;
        \?) echo "Unknown option: -$OPTARG" >%2; exit 1;;
    esac
done


# Check if at least one positional argument is provided
if [ $(( $# - $OPTIND )) -lt 0 ]; then
    print_help
    exit 1
fi


MODEL_NAME=${@:$OPTIND:1}

if [[ ! -d "$MODEL_NAME" ]]; then
    echo "not a valid model $MODEL_NAME"
    exit 1
fi




cd $MODEL_NAME


NTHREADS=$(jq -r ".n_threads" "params.json" )
echo using $NTHREADS threads

if [  "$COPY_VICE" = true ] ; then
    echo will copy full vice output
fi

if [  "$MAKE_PLOTS" = true ] ; then
    echo will make plots
fi



echo "Submitting Job" $MODEL_NAME
sbatch <<EOT
#!/bin/bash
#SBATCH --time=12:00:00
#SBATCH --ntasks=$NTHREADS
#SBATCH --cpus-per-task=1
#SBATCH --mem=4gb
#SBATCH --job-name=$MODEL_NAME
#SBATCH --mail-type=BEGIN,END,FAIL
#SBATCH --output=%j.out
#SBATCH --account=$SLURM_ACCOUNT


set -x
echo job \$SLURM_JOB_ID
export OMP_NUM_THREADS=$NTHREADS
OUT_DIR="\$TMPDIR/$MODEL_NAME"


mkdir \$OUT_DIR

python ../run.py \$OUT_DIR/milkyway.vice params.json > log.out

if [ "$COPY_VICE" = true ]; then
    cp -f \$OUT_DIR/*.dat .
    cp -rf \$OUT_DIR/milkyway.vice .
fi

python ../vice_to_json.py \$OUT_DIR/milkyway.vice -o model.json -s stars.csv


if [ "$MAKE_PLOTS" = true ]; then
    python ../visualize_model.py model.json
fi

scontrol show job=\$SLURM_JOB_ID

EOT
