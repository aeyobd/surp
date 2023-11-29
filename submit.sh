#!/bin/bash

rm -f logs/$1.log
NTHREADS=$(jq -r ".n_threads" "params/$1.json" )
echo using $NTHREADS threads


# first argument is required, filename base
if [[ $# -lt 1 ]]; then
    echo "Usage: $0 <basename> [-a]"
    exit 1
fi

MODEL_NAME="$1"
shift

SLURM_COPY_VICE=
# Iterate over all the arguments
#
while [[ $# -gt 0 ]]; do
    case "$1" in
        -a)
            SURP_COPY_VICE=1
            shift 
            ;;
        *)
            # 
            echo "Unknown argument: $1"
            exit 1
            ;;
    esac
done



if [[ -n "$SURP_COPY_VICE" ]] ; then
    echo copying vice output too
fi


echo "Submitting Job" $MODEL_NAME
sbatch <<EOT
#!/bin/bash
#SBATCH --time=12:00:00
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=$NTHREADS
#SBATCH --mem=16gb
#SBATCH --job-name=$MODEL_NAME
#SBATCH --mail-type=BEGIN,END,FAIL
#SBATCH --output=logs/slurm-$MODEL_NAME.out
#SBATCH --account=$SLURM_ACCOUNT


set -xe
echo job \$SLURM_JOB_ID
export OMP_NUM_THREADS=$NTHREADS



python run.py \$TMPDIR ./params/$MODEL_NAME.json > logs/$MODEL_NAME

if [[ -n "$SURP_COPY_VICE" ]]; then
    cp \$TMPDIR/C11_f0.2*.dat ./out
    cp -r \$TMPDIR/$MODEL_NAME.vice ./out
fi

python json_outputs.py \$TMPDIR/$MODEL_NAME.vice

cp -r -u \$TMPDIR/$MODEL_NAME.json out
cp \$TMPDIR/$MODEL_NAME.csv out


scontrol show job=\$SLURM_JOB_ID

EOT
