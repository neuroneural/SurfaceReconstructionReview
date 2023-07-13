#!/bin/bash
#SBATCH -n 1
#SBATCH -c 4
#SBATCH --mem=30g
#SBATCH -p qTRDGPU
#SBATCH -t 1-00:00
#SBATCH -J inters
#SBATCH -e jobs/error%A.err
#SBATCH -o jobs/out%A.out
#SBATCH -A psy53c17
#SBATCH --mail-type=ALL
#SBATCH --mail-user=washbee1@student.gsu.edu
#SBATCH --oversubscribe
#SBATCH --exclude=arctrdgn002,arctrddgx001

sleep 5s

line_pial=$(sed -n ${SLURM_ARRAY_TASK_ID}p lh_pial_sorted.txt)
echo "Line ${SLURM_ARRAY_TASK_ID}: $line_pial"

line_white=$(sed -n ${SLURM_ARRAY_TASK_ID}p lh_white_sorted.txt)
echo "Line ${SLURM_ARRAY_TASK_ID}: $line_white"

. /data/users2/washbee/anaconda3/bin/activate /data/users2/washbee/anaconda3/envs/meshlib
python /data/users2/washbee/speedrun/SurfaceReconstructionReview/meshlibanalysis/whitePialCollisions.py --file1 $line_pial --file2 $line_white

sleep 10s
