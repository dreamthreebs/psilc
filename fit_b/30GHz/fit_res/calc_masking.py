import numpy as np
import healpy as hp
import matplotlib.pyplot as plt
import pandas as pd
import pymaster as nmt
import os,sys

from pathlib import Path
config_dir = Path(__file__).parent.parent
print(f'{config_dir=}')
sys.path.insert(0, str(config_dir))
from config import freq, lmax, nside, beam

l = np.arange(lmax+1)
rlz_idx=0
threshold = 3

df = pd.read_csv('../../../FGSim/FreqBand')
print(f'{freq=}, {beam=}')

bin_mask = np.load('../../../psfit/fitv4/fit_res/2048/ps_mask/new_mask/BIN_C1_3_C1_3.npy')
apo_mask = np.load('../../../psfit/fitv4/fit_res/2048/ps_mask/new_mask/apo_C1_3_apo_3_apo_3.npy')
ps_mask = np.load(f'../inpainting/mask_bias/mask.npy')
# hp.orthview(ps_mask, rot=[100,50,0], half_sky=True)
# plt.show()

noise_seeds = np.load('../../seeds_noise_2k.npy')
cmb_seeds = np.load('../../seeds_cmb_2k.npy')
fg_seeds = np.load('../../seeds_fg_2k.npy')

def generate_bins(l_min_start=30, delta_l_min=30, l_max=1500, fold=0.3, l_threshold=None):
    bins_edges = []
    l_min = l_min_start  # starting l_min

    # Fixed binning until l_threshold if provided
    if l_threshold is not None:
        while l_min < l_threshold:
            l_next = l_min + delta_l_min
            if l_next > l_threshold:
                break
            bins_edges.append(l_min)
            l_min = l_next

    # Transition to dynamic binning
    while l_min < l_max:
        delta_l = max(delta_l_min, int(fold * l_min))
        l_next = l_min + delta_l
        bins_edges.append(l_min)
        l_min = l_next

    # Adding l_max to ensure the last bin goes up to l_max
    bins_edges.append(l_max)
    return bins_edges[:-1], bins_edges[1:]

def calc_dl_from_pol_map(m_q, m_u, bl, apo_mask, bin_dl, masked_on_input, purify_b):
    f2p = nmt.NmtField(apo_mask, [m_q, m_u], beam=bl, masked_on_input=masked_on_input, purify_b=purify_b, lmax=lmax, lmax_mask=lmax)
    w22p = nmt.NmtWorkspace.from_fields(f2p, f2p, bin_dl)
    # dl = nmt.workspaces.compute_full_master(pol_field, pol_field, b=bin_dl)
    dl = w22p.decouple_cell(nmt.compute_coupled_cell(f2p, f2p))[3]
    return dl

def calc_dl_from_scalar_map(scalar_map, bl, apo_mask, bin_dl, masked_on_input):
    scalar_field = nmt.NmtField(apo_mask, [scalar_map], beam=bl, masked_on_input=masked_on_input, lmax=lmax, lmax_mask=lmax)
    dl = nmt.compute_full_master(scalar_field, scalar_field, bin_dl)
    return dl[0]

def cpr_spectrum_pcn_b(bin_mask, apo_mask):

    bl = hp.gauss_beam(fwhm=np.deg2rad(beam)/60, lmax=lmax, pol=True)[:,2]
    # l_min_edges, l_max_edges = generate_bins(l_min_start=10, delta_l_min=30, l_max=lmax+1, fold=0.2)
    l_min_edges, l_max_edges = generate_bins(l_min_start=42, delta_l_min=40, l_max=lmax+1, fold=0.1, l_threshold=400)
    # delta_ell = 30
    # bin_dl = nmt.NmtBin.from_nside_linear(nside, nlb=delta_ell, is_Dell=True)
    # bin_dl = nmt.NmtBin.from_lmax_linear(lmax=lmax, nlb=40, is_Dell=True)
    bin_dl = nmt.NmtBin.from_edges(l_min_edges, l_max_edges, is_Dell=True)
    ell_arr = bin_dl.get_effective_ells()

    mask_b = ps_mask * apo_mask
    # hp.orthview(mask_b, rot=[100,50,0], half_sky=True)
    # plt.show()

    m_mask_std = hp.read_map(f'../inpainting/input_std_3nside/{rlz_idx}.fits') * bin_mask
    m_mask_n = hp.read_map(f'../inpainting/input_n_3nside/{rlz_idx}.fits') * bin_mask

    dl_mask_std = calc_dl_from_scalar_map(m_mask_std, bl, apo_mask=mask_b, bin_dl=bin_dl, masked_on_input=False)
    dl_mask_n = calc_dl_from_scalar_map(m_mask_n, bl, apo_mask=mask_b, bin_dl=bin_dl, masked_on_input=False)

    print('begin calc dl...')

    path_dl_std = Path(f'pcfn_dl4/MASK_3NSIDE/STD')
    path_dl_n = Path(f'pcfn_dl4/MASK_3NSIDE/noise')
    path_dl_std.mkdir(parents=True, exist_ok=True)
    path_dl_n.mkdir(parents=True, exist_ok=True)

    np.save(path_dl_std / Path(f'{rlz_idx}.npy'), dl_mask_std)
    np.save(path_dl_n / Path(f'{rlz_idx}.npy'), dl_mask_n)


def main():
    cpr_spectrum_pcn_b(bin_mask=bin_mask, apo_mask=apo_mask)
    # pass

main()











