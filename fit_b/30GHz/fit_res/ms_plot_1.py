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
inp_list = []

def calc_lmax(beam):
    lmax_eff = 2 * np.pi / np.deg2rad(beam) * 60
    print(f'{lmax_eff=}')
    return int(lmax_eff) + 1

def find_left_nearest_index_np(arr, target):
    # Find the indices of values less than or equal to the target
    valid_indices = np.where(arr <= target)[0]

    # If there are no valid indices, handle the case (e.g., return None)
    if valid_indices.size == 0:
        return None

    # Get the index of the largest value less than or equal to the target
    nearest_index = valid_indices[-1]  # The largest valid index
    return nearest_index + 1

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

# l_min_edges, l_max_edges = generate_bins(l_min_start=30, delta_l_min=30, l_max=lmax+1, fold=0.2)
# bin_dl = nmt.NmtBin.from_edges(l_min_edges, l_max_edges, is_Dell=True)
bin_dl = nmt.NmtBin.from_lmax_linear(lmax=lmax, nlb=40, is_Dell=True)
ell_arr = bin_dl.get_effective_ells()
print(f'{ell_arr.shape=}')
print(f'{ell_arr=}')

def mean_and_std(sim_mode):
    for rlz_idx in range(1,200):
        print(f'{rlz_idx=}')

        n_qu = np.load(f'./pcfn_dl3/{sim_mode}/n/{rlz_idx}.npy')
        pcfn = np.load(f'./pcfn_dl3/{sim_mode}/pcfn/{rlz_idx}.npy') - n_qu
        cfn = np.load(f'./pcfn_dl3/{sim_mode}/cfn/{rlz_idx}.npy') - n_qu
        cf = np.load(f'./pcfn_dl3/{sim_mode}/cf/{rlz_idx}.npy')

        n_rmv = np.load(f'./pcfn_dl3/RMV/n/{rlz_idx}.npy')
        rmv_qu = np.load(f'./pcfn_dl3/RMV/{sim_mode}/{rlz_idx}.npy') - n_rmv

        n_ps_mask = np.load(f'./pcfn_dl3/PS_MASK/{sim_mode}/n/{rlz_idx}.npy')
        ps_mask = np.load(f'./pcfn_dl3/PS_MASK/{sim_mode}/pcfn/{rlz_idx}.npy') - n_ps_mask

        n_inp = np.load(f'./pcfn_dl3/INP/noise/{rlz_idx}.npy')
        inp = np.load(f'./pcfn_dl3/INP/{sim_mode}/{rlz_idx}.npy') - n_inp

        # plt.loglog(ell_arr, pcfn, label='pcfn')
        # plt.loglog(ell_arr, cfn, label='cfn')
        # plt.loglog(ell_arr, cf, label='cf')
        # plt.loglog(ell_arr, rmv_qu, label='rmv_qu')
        # plt.loglog(ell_arr, n_qu, label='n_qu')
        # plt.loglog(ell_arr, n_rmv, label='n_rmv')
        # plt.loglog(ell_arr, n_ps_mask, label='n_ps_mask')
        # plt.loglog(ell_arr, n_inp, label='n_inp')
        # plt.loglog(ell_arr, inp, label='inp')
        # plt.loglog(ell_arr, ps_mask, label='ps_mask')

        # plt.legend()
        # plt.show()

        cf_list.append(cf)
        cfn_list.append(cfn)
        pcfn_list.append(pcfn)

        rmv_list.append(rmv_qu)
        ps_mask_list.append(ps_mask)
        inp_list.append(inp)


    pcfn_mean = np.mean(pcfn_list, axis=0)
    cfn_mean = np.mean(cfn_list, axis=0)
    cf_mean = np.mean(cf_list, axis=0)

    rmv_mean = np.mean(rmv_list, axis=0)
    ps_mask_mean = np.mean(ps_mask_list, axis=0)
    inp_mean = np.mean(inp_list, axis=0)

    pcfn_std = np.std(pcfn_list, axis=0)
    cfn_std = np.std(cfn_list, axis=0)
    cf_std = np.std(cf_list, axis=0)

    rmv_std = np.std(rmv_list, axis=0)
    ps_mask_std = np.std(ps_mask_list, axis=0)
    inp_std = np.std(inp_list, axis=0)

    return pcfn_mean, cfn_mean, cf_mean, rmv_mean, ps_mask_mean, inp_mean, pcfn_std, cfn_std, cf_std, rmv_std, ps_mask_std, inp_std


