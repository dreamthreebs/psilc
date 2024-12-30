import numpy as np
import healpy as hp
import matplotlib.pyplot as plt
import pandas as pd
import pymaster as nmt
import glob
import os,sys

from pathlib import Path
config_dir = Path(__file__).parent.parent
print(f'{config_dir=}')
sys.path.insert(0, str(config_dir))
from config import freq, lmax, nside, beam

l = np.arange(lmax+1)

df = pd.read_csv('../../../FGSim/FreqBand')
print(f'{freq=}, {beam=}')

cf_list = []
cfn_list = []
pcfn_list = []

rmv_list = []
ps_mask_list = []
sim_mode = 'MEAN'

def generate_bins(l_min_start=30, delta_l_min=30, l_max=1500, fold=0.3):
    bins_edges = []
    l_min = l_min_start  # starting l_min

    while l_min < l_max:
        delta_l = max(delta_l_min, int(fold * l_min))
        l_next = l_min + delta_l
        bins_edges.append(l_min)
        l_min = l_next

    # Adding l_max to ensure the last bin goes up to l_max
    bins_edges.append(l_max)
    return bins_edges[:-1], bins_edges[1:]

l_min_edges, l_max_edges = generate_bins(l_min_start=30, delta_l_min=30, l_max=lmax+1, fold=0.2)
bin_dl = nmt.NmtBin.from_edges(l_min_edges, l_max_edges, is_Dell=True)
ell_arr = bin_dl.get_effective_ells()
print(f'{ell_arr=}')

def mean_and_std(sim_mode):
    for rlz_idx in range(1,200):
        n_qu = np.load(f'./pcfn_dl/{sim_mode}/n/{rlz_idx}.npy')
        pcfn = np.load(f'./pcfn_dl/{sim_mode}/pcfn/{rlz_idx}.npy') - n_qu
        cfn = np.load(f'./pcfn_dl/{sim_mode}/cfn/{rlz_idx}.npy') - n_qu
        cf = np.load(f'./pcfn_dl/{sim_mode}/cf/{rlz_idx}.npy')

        n_rmv = np.load(f'./pcfn_dl/RMV/n/{rlz_idx}.npy')
        rmv_qu = np.load(f'./pcfn_dl/RMV/{sim_mode}/{rlz_idx}.npy') - n_rmv

        n_ps_mask = np.load(f'./pcfn_dl/PS_MASK/{sim_mode}/n/{rlz_idx}.npy')
        ps_mask = np.load(f'./pcfn_dl/PS_MASK/{sim_mode}/pcfn/{rlz_idx}.npy') - n_rmv

        # plt.loglog(pcfn, label='pcfn')
        # plt.loglog(cfn, label='cfn')
        # plt.loglog(cf, label='cf')
        # plt.loglog(rmv_qu, label='rmv_qu')
        # plt.loglog(n_qu, label='n_qu')
        # plt.loglog(n_rmv, label='n_rmv')
        # plt.loglog(n_ps_mask, label='n_ps_mask')
        # plt.legend()
        # plt.show()

        cf_list.append(cf)
        cfn_list.append(cfn)
        pcfn_list.append(pcfn)

        rmv_list.append(rmv_qu)
        ps_mask_list.append(ps_mask)


    pcfn_mean = np.mean(pcfn_list, axis=0)
    cfn_mean = np.mean(cfn_list, axis=0)
    cf_mean = np.mean(cf_list, axis=0)

    rmv_mean = np.mean(rmv_list, axis=0)
    ps_mask_mean = np.mean(ps_mask_list, axis=0)

    pcfn_std = np.std(pcfn_list, axis=0)
    cfn_std = np.std(cfn_list, axis=0)
    cf_std = np.std(cf_list, axis=0)

    rmv_std = np.std(rmv_list, axis=0)
    ps_mask_std = np.std(ps_mask_list, axis=0)
    return pcfn_mean, cfn_mean, cf_mean, rmv_mean, ps_mask_mean, pcfn_std, cfn_std, cf_std, rmv_std, ps_mask_std

pcfn_mean, cfn_mean, cf_mean, rmv_mean, ps_mask_mean, _, _, _, _, _ = mean_and_std(sim_mode='MEAN')

plt.figure(1)
plt.scatter(ell_arr, pcfn_mean, label='pcfn', marker='.')
plt.scatter(ell_arr, cfn_mean, label='cfn', marker='.')
plt.scatter(ell_arr, cf_mean, label='cf', marker='.')
plt.scatter(ell_arr, rmv_mean, label='rmv', marker='.')
plt.scatter(ell_arr, ps_mask_mean, label='ps_mask', marker='.')
plt.xlabel('$\\ell$')
plt.ylabel('$D_\\ell^{BB} [\mu K^2]$')

plt.loglog()
plt.legend()
plt.title('mean')

_, _, _, _, _, pcfn_std, cfn_std, cf_std, rmv_std, ps_mask_std = mean_and_std(sim_mode='STD')

plt.figure(2)
plt.scatter(ell_arr, pcfn_std, label='pcfn', marker='.')
plt.scatter(ell_arr, cfn_std, label='cfn', marker='.')
plt.scatter(ell_arr, cf_std, label='cf', marker='.')
plt.scatter(ell_arr, rmv_std, label='rmv', marker='.')
plt.scatter(ell_arr, ps_mask_std, label='ps_mask', marker='.')
plt.xlabel('$\\ell$')
plt.ylabel('$D_\\ell^{BB} [\mu K^2]$')

plt.loglog()
plt.legend()
plt.title('standard deviation')
plt.show()

# Create figure and axis
fig, ax = plt.subplots()

# Set y-axis to logarithmic scale
ax.set_yscale('log')

# Error bars (only in y, in log scale)
ax.errorbar(ell_arr, pcfn_mean, yerr=pcfn_std, fmt='.', capsize=5, label='PS + CMB + FG + NOISE')
ax.errorbar(ell_arr+1.2, cfn_mean, yerr=cfn_std, fmt='.', capsize=5, label='CMB + FG + NOISE')
ax.errorbar(ell_arr+2.4, rmv_mean, yerr=rmv_std, fmt='.', capsize=5, label='Template Fitting method')
# ax.errorbar(ell_arr+3.6, ps_mask_mean, yerr=ps_mask_std, fmt='.', capsize=5, label='ps_mask')

# Add labels, legend, and title
ax.set_xlabel('$\\ell$')
ax.set_ylabel('$D_\\ell^{BB} [\mu K^2]$')
ax.set_xlim(2,300)
ax.set_ylim(1e-2,5e0)
ax.set_title('Debiased power spectra and standard deviation')
ax.legend()

path_fig = Path('/afs/ihep.ac.cn/users/w/wangyiming25/tmp/20241230')
path_fig.mkdir(exist_ok=True, parents=True)
plt.savefig(path_fig / Path(f'{freq}GHz.png'), dpi=300)

# Show plot
plt.show()

