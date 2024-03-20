#!/bin/bash
#
#
function print_help {
    echo Submits a job to run a vice model
    echo Usage: $0 [-aph] MODEL_DIR ;
    echo -a: copy full vice outputs
    echo -p: make plots
    echo -m: specify memory
    echo -h: print this message 
}


# default args
COPY_VICE=false
MAKE_PLOTS=false
REQUESTED_MEMORY="4gb"

# Iterate over all the arguments
#
while getopts 'aphm:' OPTION; do
    case "$OPTION" in
        a) COPY_VICE=true ;;
        p) MAKE_PLOTS=true ;;
        m) REQUESTED_MEMORY=$OPTARG ;;
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
    echo "not a valid model $MODEL_NAME"
    exit 1
fi

NTHREADS=1

if [  "$COPY_VICE" = true ] ; then
    echo will copy full vice output
fi

if [  "$MAKE_PLOTS" = true ] ; then
    echo will make plots
fi


cd $MODEL_NAME

function confirm_and_remove_files {
    local pattern
    local existing_files=()
    for pattern in "$@"; do
        local matched_files=( $pattern )
        if [ ${#matched_files[@]} -gt 0 ]; then
            existing_files+=("${matched_files[@]}")
        fi
    done

    if [ ${#existing_files[@]} -eq 0 ]; then
        echo "No specified files exist, nothing to remove."
        return
    fi

    echo "The following files will be removed:"
    for file in "${existing_files[@]}"; do
        echo "$file"
    done

    read -p "Are you sure you want to remove these files? (y/N)  " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        for file in "${existing_files[@]}"; do
            rm -rf "$file"
        done
        echo "Files removed."
    else
        echo "File removal aborted."
        exit 1;
    fi
}

# Files to check before removing
files_to_remove=("*.out" "model.json" "stars.csv" "*.dat", "milkway.vice")
confirm_and_remove_files "${files_to_remove[@]}"

echo "Submitting Job" $MODEL_NAME
sbatch <<EOT
#!/bin/bash
#SBATCH --time=1:00:00
#SBATCH --ntasks=$NTHREADS
#SBATCH --cpus-per-task=1
#SBATCH --mem=$REQUESTED_MEMORY
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

python run.py

cp model.json \$SLURM_SUBMIT_DIR
cp stars.csv \$SLURM_SUBMIT_DIR

if [ "$COPY_VICE" = true ]; then
    cp -f *.dat \$SLURM_SUBMIT_DIR
    cp -rf milkyway.vice \$SLURM_SUBMIT_DIR
fi

scontrol show job=\$SLURM_JOB_ID

EOT
