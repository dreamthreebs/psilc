import numpy as np
import healpy as hp
import matplotlib.pyplot as plt
import pandas as pd
import pymaster as nmt

from pathlib import Path

lmax = 600
l = np.arange(lmax+1)
nside = 2048
rlz_idx=0
threshold = 3

df = pd.read_csv('../../../FGSim/FreqBand')
freq = df.at[0, 'freq']
beam = df.at[0, 'beam']
print(f'{freq=}, {beam=}')

bin_mask = np.load('../../../psfit/fitv4/fit_res/2048/ps_mask/no_edge_mask/C1_5.npy')
apo_mask = np.load('../../../psfit/fitv4/fit_res/2048/ps_mask/no_edge_mask/C1_5APO_5.npy')
ps_mask = np.load(f'../inpainting/mask/apo_ps_mask.npy')

noise_seeds = np.load('../../seeds_noise_2k.npy')
cmb_seeds = np.load('../../seeds_cmb_2k.npy')
fg_seeds = np.load('../../seeds_fg_2k.npy')

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

def calc_dl_from_scalar_map_nobeam(scalar_map, apo_mask, bin_dl, masked_on_input):
    scalar_field = nmt.NmtField(apo_mask, [scalar_map], masked_on_input=masked_on_input, lmax=lmax, lmax_mask=lmax)
    dl = nmt.compute_full_master(scalar_field, scalar_field, bin_dl)
    return dl[0]


def gen_fg_cl():
    cl_fg = np.load('../../Cl_fg/data_1010/cl_fg.npy')
    Cl_TT = cl_fg[0]
    Cl_EE = cl_fg[1]
    Cl_BB = cl_fg[2]
    Cl_TE = np.zeros_like(Cl_TT)
    return np.array([Cl_TT, Cl_EE, Cl_BB, Cl_TE])

def gen_map(rlz_idx):
    npix = hp.nside2npix(nside=nside)
    ps = np.load('../data/ps/ps.npy')

    nstd = np.load('../../../FGSim/NSTDNORTH/2048/30.npy')
    np.random.seed(seed=noise_seeds[rlz_idx])
    # noise = nstd * np.random.normal(loc=0, scale=1, size=(3, npix))
    noise = nstd * np.random.normal(loc=0, scale=1, size=(3,npix))
    print(f"{np.std(noise[1])=}")

    # cmb_iqu = np.load(f'../../fitdata/2048/CMB/215/{rlz_idx}.npy')
    # cls = np.load('../../src/cmbsim/cmbdata/cmbcl.npy')
    cls = np.load('../../../src/cmbsim/cmbdata/cmbcl_8k.npy')
    np.random.seed(seed=cmb_seeds[rlz_idx])
    # cmb_iqu = hp.synfast(cls.T, nside=nside, fwhm=np.deg2rad(beam)/60, new=True, lmax=1999)
    cmb_iqu = hp.synfast(cls.T, nside=nside, fwhm=np.deg2rad(beam)/60, new=True, lmax=3*nside-1)

    cls_fg = gen_fg_cl()
    np.random.seed(seed=fg_seeds[rlz_idx])
    fg = hp.synfast(cls_fg, nside=nside, fwhm=0, new=True, lmax=600)

    pcfn = noise + ps + cmb_iqu + fg
    cfn = noise + cmb_iqu + fg
    cf = cmb_iqu + fg
    n = noise

    # pcfn = noise
    # cfn = noise
    # cf = noise # n = noise

    return pcfn, cfn, cf, n


def cpr_spectrum_pcn_b(bin_mask, apo_mask):

    bl = hp.gauss_beam(fwhm=np.deg2rad(beam)/60, lmax=lmax, pol=True)[:,2]
    l_min_edges, l_max_edges = generate_bins(l_min_start=30, delta_l_min=30, l_max=lmax+1, fold=0.2)
    # delta_ell = 30
    # bin_dl = nmt.NmtBin.from_nside_linear(nside, nlb=delta_ell, is_Dell=True)
    # bin_dl = nmt.NmtBin.from_lmax_linear(lmax=lmax, nlb=30, is_Dell=True)
    bin_dl = nmt.NmtBin.from_edges(l_min_edges, l_max_edges, is_Dell=True)
    ell_arr = bin_dl.get_effective_ells()

    cf,_,_,_ = gen_map(rlz_idx=rlz_idx)

    m_inp_eb_b = cf[0]*bin_mask
    # m_inp_eb_b = hp.read_map(f'../inpainting/output/{rlz_idx}.fits') * bin_mask
    m_inp_eb_b_n = hp.alm2map(hp.almxfl(hp.map2alm(cf[0], lmax=lmax), fl=1/bl), nside=nside)*bin_mask

    dl_inp_eb_b = calc_dl_from_scalar_map(m_inp_eb_b, bl, apo_mask=apo_mask, bin_dl=bin_dl, masked_on_input=False)
    dl_inp_eb_b_n = calc_dl_from_scalar_map_nobeam(m_inp_eb_b_n, apo_mask=apo_mask, bin_dl=bin_dl, masked_on_input=False)

    print('begin calc dl...')

    path_dl_qu = Path(f'pcfn_dl/RMV/test_pcfn')
    path_dl_qu_n = Path(f'pcfn_dl/RMV/test_pcfn_no_beam')
    path_dl_qu.mkdir(parents=True, exist_ok=True)
    path_dl_qu_n.mkdir(parents=True, exist_ok=True)

    np.save(path_dl_qu / Path(f'{rlz_idx}.npy'), dl_inp_eb_b)
    np.save(path_dl_qu_n / Path(f'{rlz_idx}.npy'), dl_inp_eb_b_n)

def check_mask_dl():
    
    bl = hp.gauss_beam(fwhm=np.deg2rad(beam)/60, lmax=lmax, pol=True)[:,2]
    l_min_edges, l_max_edges = generate_bins(l_min_start=30, delta_l_min=30, l_max=lmax+1, fold=0.2)
    # delta_ell = 30
    # bin_dl = nmt.NmtBin.from_nside_linear(nside, nlb=delta_ell, is_Dell=True)
    # bin_dl = nmt.NmtBin.from_lmax_linear(lmax=lmax, nlb=30, is_Dell=True)
    bin_dl = nmt.NmtBin.from_edges(l_min_edges, l_max_edges, is_Dell=True)
    bin_dl_no_dell = nmt.NmtBin.from_edges(l_min_edges, l_max_edges)
    ell_arr = bin_dl.get_effective_ells()

    dl_mask = np.load('./pcfn_dl/RMV/test_pcfn/0.npy')
    dl_mask_no_beam = np.load('./pcfn_dl/RMV/test_pcfn_no_beam/0.npy')

    bin_bl = bin_dl_no_dell.bin_cell(bl)
    print(f'{bin_bl=}')

    plt.plot(ell_arr, dl_mask, label=f'dl pcfn ')
    plt.plot(ell_arr, dl_mask_no_beam, label=f'dl pcfn no beam')
    plt.plot(ell_arr, np.abs(dl_mask - dl_mask_no_beam)/dl_mask_no_beam, label=f'relative error')

    # plt.plot(ell_arr, dl_mask_no_beam/bin_bl**2, label=f'dl mask debeam')
    plt.legend()
    plt.loglog()
    plt.xlabel('$\\ell$')
    plt.ylabel('$D_\\ell$')
    plt.show()


def main():

    # cpr_spectrum_pcn_b(bin_mask=bin_mask, apo_mask=apo_mask)
    check_mask_dl()
    # cpr_spectrum_noise_bias_b()

    # calc_true_noise_bias_b()

    # test_c_b(bin_mask=bin_mask, apo_mask=apo_mask)

main()










