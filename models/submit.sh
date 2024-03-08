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
echo Cleaning old outputs
rm -f *.out
rm -rf *.vice
rm -f model.json stars.csv *.dat
ls


NTHREADS=$(jq -r ".n_threads" "params.json" )
NTHREADS=1

if [  "$COPY_VICE" = true ] ; then
    echo will copy full vice output
fi

if [  "$MAKE_PLOTS" = true ] ; then
    echo will make plots
fi



echo "Submitting Job" $MODEL_NAME
sbatch <<EOT
#!/bin/bash
#SBATCH --time=1:00:00
#SBATCH --ntasks=$NTHREADS
#SBATCH --cpus-per-task=1
#SBATCH --mem=4gb
#SBATCH --job-name=$MODEL_NAME
#SBATCH --mail-type=BEGIN,END,FAIL
#SBATCH --output=%j.out
#SBATCH --account=$SLURM_ACCOUNT


set -x
echo job \$SLURM_JOB_ID
echo \$TMPDIR
echo \$SLURM_SUBMIT_DIR
export OMP_NUM_THREADS=$NTHREADS

cp run.py \$TMPDIR
cp params.json \$TMPDIR
cp yield_params.json \$TMPDIR

cd \$TMPDIR

python run.py > log.out

ls
if [ "$COPY_VICE" = true ]; then
    cp -f *.dat \$SLURM_SUBMIT_DIR
    cp -rf milkyway.vice \$SLURM_SUBMIT_DIR
fi

python \$SLURM_SUBMIT_DIR/../vice_to_json.py milkyway.vice -o model.json -s stars.csv

cp model.json \$SLURM_SUBMIT_DIR
cp stars.csv \$SLURM_SUBMIT_DIR


# if [ "$MAKE_PLOTS" = true ]; then
#     python ../visualize_model.py model.json
# fi

scontrol show job=\$SLURM_JOB_ID

EOT
