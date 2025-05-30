#! /bin/bash

#=====================================================
#===== Modify the following options for your job =====
#=====    DON'T remove the #! /bin/bash lines    =====
#=====      DON'T comment #SBATCH lines          =====
#=====        of partition,account and           =====
#=====                qos                        =====
#=====================================================

# Specify the partition name from which resources will be allocated  
#SBATCH --partition=ali

# Specify which expriment group you belong to.
# This is for the accounting, so if you belong to many experiments,
# write the experiment which will pay for your resource consumption
#SBATCH --account=alicpt

# Specify which qos(job queue) the job is submitted to.
#SBATCH --qos=regular


# ====================================
#SBATCH --job-name=wym

#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=64
#SBATCH --mem=200GB
# SBATCH --exclude=aliws[021-040],aliws005
# SBATCH --mem-per-cpu=2000
# SBATCH --nodelist=aliws010

#SBATCH -o /afs/ihep.ac.cn/users/w/wangyiming25/tmp/slurmlogs/o%j.log
#SBATCH --error=/afs/ihep.ac.cn/users/w/wangyiming25/tmp/slurmlogs/e%j.log

#or use relative path(some example are listed)
# mpiexec python -u tod_gen4cc.py
# mpirun -np 7 ./cosmomc test.ini
# python as.py

date +%m-%d_%H-%M
# mpiexec python -u /afs/ihep.ac.cn/users/w/wangyiming25/work/dc2/pol_ILC/src/ILC/PIPELINE_ILC.py
# mrs_alm_inpainting -v -i 40 -l 5000 ./ps_cmb_noise.fits ./mask1dot8.fits ./inpaint_m_1dot8.fits
mrs_alm_inpainting -g 0.675 -v ./ps_cmb_noise.fits ./mask.fits ./inpaint_denoise.fits

date +%m-%d_%H-%M
DATE=$(date +%m%d%H%M)



