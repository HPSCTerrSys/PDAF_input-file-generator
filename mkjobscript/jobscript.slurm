#!/usr/bin/env bash
#SBATCH --job-name=eclm_pdaf_derusww
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=10
#SBATCH --account=jibg36
#SBATCH --partition=devel
#SBATCH --time=0:10:00
#SBATCH --output=logs/%j.%x.out
#SBATCH --error=logs/%j.%x.err

# Load environment
source loadenvs

# Run model
srun -n $SLURM_NTASKS ./tsmp-pdaf -n_modeltasks 10 -screen 3 -filtertype 2 -subtype 1 -delt_obs 1 -rms_obs 0.02 -obs_filename ./obs/SM_CLM
