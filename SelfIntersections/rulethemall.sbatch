#!/bin/bash
#SBATCH -n 1
#SBATCH -c 4
#SBATCH --mem=10g
#SBATCH -p qTRDGPU
#SBATCH -t 4-00:00
#SBATCH -J rthemall
#SBATCH -e jobs/error%A.err
#SBATCH -o jobs/out%A.out
#SBATCH -A psy53c17
#SBATCH --mail-type=ALL
#SBATCH --mail-user=washbee1@student.gsu.edu
#SBATCH --oversubscribe
#SBATCH --exclude=arctrdgn002,arctrddgx001

. /data/users2/washbee/anaconda3/bin/activate /data/users2/washbee/anaconda3/envs/meshlib

line_pial=$(sed -n ${SLURM_ARRAY_TASK_ID}p ../lh_pial_sorted.txt)
echo "Line ${SLURM_ARRAY_TASK_ID}: $line_pial"

python dispatch_slurms.py line_pial
