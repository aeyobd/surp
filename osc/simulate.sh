#!/bin/bash

module load miniconda3/4.12.0-py39

OUT_NAME=$(python osc/args.py "$@")

echo $OUT_NAME

# written like this so we can substitute the 
# name into the file for easier understanding
echo "Submitting Job"
rm logs/$OUT_NAME.log


sbatch <<EOT
#!/bin/bash
#SBATCH --time=2:00:00
#SBATCH --ntasks=1
#SBATCH --mem=32gb
#SBATCH --job-name=$OUT_NAME
#SBATCH --mail-type=BEGIN,END,FAIL
#SBATCH --output=logs/$OUT_NAME.log
#SBATCH --account=PAS2232


set -x

cd $SLURM_SUBMIT_DIR
module load miniconda3/4.12.0-py39


python \$SLURM_SUBMIT_DIR/osc/simulate.py \$TMPDIR/ "\$@"
python \$SLURM_SUBMIT_DIR/osc/json_outputs.py \$TMPDIR/

cp -r -u \$TMPDIR/*.json \$SLURM_SUBMIT_DIR/output

scontrol show job=\$SLURM_JOB_ID

EOT
