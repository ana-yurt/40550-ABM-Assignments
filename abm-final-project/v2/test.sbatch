#!/bin/bash
#SBATCH --job-name=ethnic-abm
#SBATCH --output=batch_log_%j.out
#SBATCH --error=batch_err_%j.err
#SBATCH --time=10:00:00
#SBATCH --account=ssd
#SBATCH --partition=ssd
#SBATCH --nodes=1
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=2
#SBATCH --mem=10G  

module load python
source activate myenv

echo "Starting job"
python test.py
echo "Finished job"