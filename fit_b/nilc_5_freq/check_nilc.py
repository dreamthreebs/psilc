import numpy as np
import healpy as hp
import matplotlib.pyplot as plt
import pymaster as nmt

from pathlib import Path

beam = 17
lmax = 1500

rlz_idx = 0

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

def calc_dl_from_scalar_map(scalar_map, bl, apo_mask, bin_dl, masked_on_input):
    scalar_field = nmt.NmtField(apo_mask, [scalar_map], beam=bl, masked_on_input=masked_on_input, lmax=lmax, lmax_mask=lmax)
    dl = nmt.compute_full_master(scalar_field, scalar_field, bin_dl)
    return dl[0]

def calc_dl():
    bl = hp.gauss_beam(fwhm=np.deg2rad(beam)/60, lmax=lmax, pol=True)[:,2]
    l_min_edges, l_max_edges = generate_bins(l_min_start=30, delta_l_min=30, l_max=lmax+1, fold=0.2)
    # delta_ell = 30
    # bin_dl = nmt.NmtBin.from_nside_linear(nside, nlb=delta_ell, is_Dell=True)
    # bin_dl = nmt.NmtBin.from_lmax_linear(lmax=lmax, nlb=30, is_Dell=True)
    bin_dl = nmt.NmtBin.from_edges(l_min_edges, l_max_edges, is_Dell=True)
    ell_arr = bin_dl.get_effective_ells()

    apo_mask = np.load(f'../../psfit/fitv4/fit_res/2048/ps_mask/no_edge_mask/C1_5APO_3APO_5APO_3.npy')


    # m = np.load(f'./data/mean/pcfn/{rlz_idx}.npy')

    def _calc_dl(sim_mode, method):
        _map = np.load(f'./data/{sim_mode}/{method}/{rlz_idx}.npy')
        n_map = np.load(f'./data/{sim_mode}/n_{method}/{rlz_idx}.npy')

        dl = calc_dl_from_scalar_map(scalar_map=_map, bl=bl, apo_mask=apo_mask, bin_dl=bin_dl, masked_on_input=False)
        dl_n = calc_dl_from_scalar_map(scalar_map=n_map, bl=bl, apo_mask=apo_mask, bin_dl=bin_dl, masked_on_input=False)
        path_dl = Path(f'./dl_res/{sim_mode}/{method}')
        path_dl.mkdir(exist_ok=True, parents=True)
        path_dl_n = Path(f'./dl_res/{sim_mode}/n_{method}')
        path_dl_n.mkdir(exist_ok=True, parents=True)
        np.save(path_dl / Path(f'{rlz_idx}.npy'), dl)
        np.save(path_dl_n / Path(f'{rlz_idx}.npy'), dl_n)
        print(f'dl {sim_mode} {method} is ok')

    _calc_dl(sim_mode='mean', method='pcfn')
    _calc_dl(sim_mode='mean', method='cfn')
    _calc_dl(sim_mode='mean', method='rmv')
    _calc_dl(sim_mode='mean', method='inp')
    _calc_dl(sim_mode='std', method='pcfn')
    _calc_dl(sim_mode='std', method='cfn')
    _calc_dl(sim_mode='std', method='rmv')
    _calc_dl(sim_mode='std', method='inp')

def calc_dl1():
    bl = hp.gauss_beam(fwhm=np.deg2rad(beam)/60, lmax=lmax, pol=True)[:,2]
    l_min_edges, l_max_edges = generate_bins(l_min_start=30, delta_l_min=30, l_max=lmax+1, fold=0.2)
    # delta_ell = 30
    # bin_dl = nmt.NmtBin.from_nside_linear(nside, nlb=delta_ell, is_Dell=True)
    # bin_dl = nmt.NmtBin.from_lmax_linear(lmax=lmax, nlb=30, is_Dell=True)
    bin_dl = nmt.NmtBin.from_edges(l_min_edges, l_max_edges, is_Dell=True)
    ell_arr = bin_dl.get_effective_ells()

    apo_mask = np.load(f'../../psfit/fitv4/fit_res/2048/ps_mask/no_edge_mask/C1_5APO_3APO_5APO_3.npy')


    # m = np.load(f'./data/mean/pcfn/{rlz_idx}.npy')

    def _calc_dl(sim_mode, method):
        _map = np.load(f'./data1/{sim_mode}/{method}/{rlz_idx}.npy')

        dl = calc_dl_from_scalar_map(scalar_map=_map, bl=bl, apo_mask=apo_mask, bin_dl=bin_dl, masked_on_input=False)
        path_dl = Path(f'./dl_res1/{sim_mode}/{method}')
        path_dl.mkdir(exist_ok=True, parents=True)
        np.save(path_dl / Path(f'{rlz_idx}.npy'), dl)

        if method == 'cf':
            pass
        else:
            n_map = np.load(f'./data1/{sim_mode}/n_{method}/{rlz_idx}.npy')
            dl_n = calc_dl_from_scalar_map(scalar_map=n_map, bl=bl, apo_mask=apo_mask, bin_dl=bin_dl, masked_on_input=False)
            path_dl_n = Path(f'./dl_res1/{sim_mode}/n_{method}')
            path_dl_n.mkdir(exist_ok=True, parents=True)
            np.save(path_dl_n / Path(f'{rlz_idx}.npy'), dl_n)
        print(f'dl {sim_mode} {method} is ok')

    # _calc_dl(sim_mode='mean', method='pcfn')
    # _calc_dl(sim_mode='mean', method='cfn')
    # _calc_dl(sim_mode='mean', method='rmv')
    # _calc_dl(sim_mode='mean', method='inp')
    _calc_dl(sim_mode='std', method='pcfn')
    _calc_dl(sim_mode='std', method='cfn')
    _calc_dl(sim_mode='std', method='rmv')
    _calc_dl(sim_mode='std', method='cf')
    # _calc_dl(sim_mode='std', method='inp')

def calc_dl2():
    bl = hp.gauss_beam(fwhm=np.deg2rad(beam)/60, lmax=lmax, pol=True)[:,2]
    l_min_edges, l_max_edges = generate_bins(l_min_start=10, delta_l_min=30, l_max=lmax+1, fold=0.2)
    # delta_ell = 30
    # bin_dl = nmt.NmtBin.from_nside_linear(nside, nlb=delta_ell, is_Dell=True)
    # bin_dl = nmt.NmtBin.from_lmax_linear(lmax=lmax, nlb=30, is_Dell=True)
    bin_dl = nmt.NmtBin.from_edges(l_min_edges, l_max_edges, is_Dell=True)
    ell_arr = bin_dl.get_effective_ells()

    apo_mask = np.load(f'../../psfit/fitv4/fit_res/2048/ps_mask/no_edge_mask/C1_5APO_3APO_5APO_3.npy')


    # m = np.load(f'./data/mean/pcfn/{rlz_idx}.npy')

    def _calc_dl(sim_mode, method):
        _map = np.load(f'./data1/{sim_mode}/{method}/{rlz_idx}.npy')

        dl = calc_dl_from_scalar_map(scalar_map=_map, bl=bl, apo_mask=apo_mask, bin_dl=bin_dl, masked_on_input=False)
        path_dl = Path(f'./dl_res2/{sim_mode}/{method}')
        path_dl.mkdir(exist_ok=True, parents=True)
        np.save(path_dl / Path(f'{rlz_idx}.npy'), dl)

        if method == 'cf':
            pass
        else:
            n_map = np.load(f'./data1/{sim_mode}/n_{method}/{rlz_idx}.npy')
            dl_n = calc_dl_from_scalar_map(scalar_map=n_map, bl=bl, apo_mask=apo_mask, bin_dl=bin_dl, masked_on_input=False)
            path_dl_n = Path(f'./dl_res2/{sim_mode}/n_{method}')
            path_dl_n.mkdir(exist_ok=True, parents=True)
            np.save(path_dl_n / Path(f'{rlz_idx}.npy'), dl_n)
        print(f'dl {sim_mode} {method} is ok')

    # _calc_dl(sim_mode='mean', method='pcfn')
    # _calc_dl(sim_mode='mean', method='cfn')
    # _calc_dl(sim_mode='mean', method='rmv')
    # _calc_dl(sim_mode='mean', method='inp')
    _calc_dl(sim_mode='std', method='pcfn')
    _calc_dl(sim_mode='std', method='cfn')
    _calc_dl(sim_mode='std', method='rmv')
    _calc_dl(sim_mode='std', method='cf')
    # _calc_dl(sim_mode='std', method='inp')

def calc_dl3():
    bl = hp.gauss_beam(fwhm=np.deg2rad(beam)/60, lmax=lmax, pol=True)[:,2]
    # l_min_edges, l_max_edges = generate_bins(l_min_start=10, delta_l_min=30, l_max=lmax+1, fold=0.2)
    # delta_ell = 30
    # bin_dl = nmt.NmtBin.from_nside_linear(nside, nlb=delta_ell, is_Dell=True)
    bin_dl = nmt.NmtBin.from_lmax_linear(lmax=lmax, nlb=40, is_Dell=True)
    # bin_dl = nmt.NmtBin.from_edges(l_min_edges, l_max_edges, is_Dell=True)
    ell_arr = bin_dl.get_effective_ells()

    apo_mask = np.load(f'../../psfit/fitv4/fit_res/2048/ps_mask/new_mask/apo_C1_3_apo_3_apo_3.npy')


    # m = np.load(f'./data/mean/pcfn/{rlz_idx}.npy')

    def _calc_dl(sim_mode, method):
        _map = np.load(f'./data2/{sim_mode}/{method}/{rlz_idx}.npy')

        dl = calc_dl_from_scalar_map(scalar_map=_map, bl=bl, apo_mask=apo_mask, bin_dl=bin_dl, masked_on_input=False)
        path_dl = Path(f'./dl_res3/{sim_mode}/{method}')
        path_dl.mkdir(exist_ok=True, parents=True)
        np.save(path_dl / Path(f'{rlz_idx}.npy'), dl)

        if method == 'cf':
            pass
        else:
            n_map = np.load(f'./data2/{sim_mode}/n_{method}/{rlz_idx}.npy')
            dl_n = calc_dl_from_scalar_map(scalar_map=n_map, bl=bl, apo_mask=apo_mask, bin_dl=bin_dl, masked_on_input=False)
            path_dl_n = Path(f'./dl_res3/{sim_mode}/n_{method}')
            path_dl_n.mkdir(exist_ok=True, parents=True)
            np.save(path_dl_n / Path(f'{rlz_idx}.npy'), dl_n)
        print(f'dl {sim_mode} {method} is ok')

    # _calc_dl(sim_mode='mean', method='pcfn')
    # _calc_dl(sim_mode='mean', method='cfn')
    # _calc_dl(sim_mode='mean', method='rmv')
    # _calc_dl(sim_mode='mean', method='inp')

    # _calc_dl(sim_mode='std', method='pcfn')
    # _calc_dl(sim_mode='std', method='cfn')
    # _calc_dl(sim_mode='std', method='rmv')
    # _calc_dl(sim_mode='std', method='cf')

    _calc_dl(sim_mode='std', method='inp')



def get_mean_std():
    bl = hp.gauss_beam(fwhm=np.deg2rad(beam)/60, lmax=lmax, pol=True)[:,2]
    l_min_edges, l_max_edges = generate_bins(l_min_start=30, delta_l_min=30, l_max=lmax+1, fold=0.2)
    # delta_ell = 30
    # bin_dl = nmt.NmtBin.from_nside_linear(nside, nlb=delta_ell, is_Dell=True)
    # bin_dl = nmt.NmtBin.from_lmax_linear(lmax=lmax, nlb=30, is_Dell=True)
    bin_dl = nmt.NmtBin.from_edges(l_min_edges, l_max_edges, is_Dell=True)
    ell_arr = bin_dl.get_effective_ells()
    cl = np.load(f'../../src/cmbsim/cmbdata/cmbcl_8k.npy')[:lmax+1,2]
    print(f'{cl.shape=}')
    l = np.arange(len(cl))


    pcfn_mean = np.mean([np.load(f'./dl_res/std/pcfn/{rlz_idx}.npy') - np.load(f'./dl_res/std/n_pcfn/{rlz_idx}.npy') for rlz_idx in np.arange(1,200)], axis=0)
    pcfn_std = np.std([np.load(f'./dl_res/std/pcfn/{rlz_idx}.npy') - np.load(f'./dl_res/std/n_pcfn/{rlz_idx}.npy') for rlz_idx in np.arange(1,200)], axis=0)
    cfn_mean = np.mean([np.load(f'./dl_res/std/cfn/{rlz_idx}.npy') - np.load(f'./dl_res/std/n_cfn/{rlz_idx}.npy') for rlz_idx in np.arange(1,200)], axis=0)
    cfn_std = np.std([np.load(f'./dl_res/std/cfn/{rlz_idx}.npy') - np.load(f'./dl_res/std/n_cfn/{rlz_idx}.npy') for rlz_idx in np.arange(1,200)], axis=0)
    rmv_mean = np.mean([np.load(f'./dl_res/std/rmv/{rlz_idx}.npy') - np.load(f'./dl_res/std/n_rmv/{rlz_idx}.npy') for rlz_idx in np.arange(1,200)], axis=0)
    rmv_std = np.std([np.load(f'./dl_res/std/rmv/{rlz_idx}.npy') - np.load(f'./dl_res/std/n_rmv/{rlz_idx}.npy') for rlz_idx in np.arange(1,200)], axis=0)
    inp_mean = np.mean([np.load(f'./dl_res/std/inp/{rlz_idx}.npy') - np.load(f'./dl_res/std/n_inp/{rlz_idx}.npy') for rlz_idx in np.arange(1,200)], axis=0)
    inp_std = np.std([np.load(f'./dl_res/std/inp/{rlz_idx}.npy') - np.load(f'./dl_res/std/n_inp/{rlz_idx}.npy') for rlz_idx in np.arange(1,200)], axis=0)
    print(f'mean std over')

    fig, ax = plt.subplots()
    
    # Set y-axis to logarithmic scale
    ax.set_yscale('log')
    ax.set_xscale('log')
    
    # Error bars (only in y, in log scale)
    ax.errorbar(ell_arr, pcfn_mean, yerr=pcfn_std, fmt='.', capsize=5, label='PS + CMB + FG + NOISE')
    ax.errorbar(ell_arr+1.2, cfn_mean, yerr=cfn_std, fmt='.', capsize=5, label='CMB + FG + NOISE')
    ax.errorbar(ell_arr+2.4, rmv_mean, yerr=rmv_std, fmt='.', capsize=5, label='Template Fitting method')
    ax.errorbar(ell_arr+3.6, inp_mean, yerr=inp_std, fmt='.', capsize=5, label='Recycling + inpaint on B')
    ax.loglog(l, l*(l+1)*cl/(2*np.pi), label='cmb input')
    
    # Add labels, legend, and title
    ax.set_xlabel('$\\ell$')
    ax.set_ylabel('$D_\\ell^{BB} [\mu K^2]$')
    # ax.set_xlim(2,lmax_eff)
    # ax.set_ylim(1e-2,5e0)
    ax.set_title('Debiased power spectra and standard deviation')
    ax.legend()
    plt.show()

def plot_ms():
    bl = hp.gauss_beam(fwhm=np.deg2rad(beam)/60, lmax=lmax, pol=True)[:,2]
    l_min_edges, l_max_edges = generate_bins(l_min_start=30, delta_l_min=30, l_max=lmax+1, fold=0.2)
    # delta_ell = 30
    # bin_dl = nmt.NmtBin.from_nside_linear(nside, nlb=delta_ell, is_Dell=True)
    # bin_dl = nmt.NmtBin.from_lmax_linear(lmax=lmax, nlb=30, is_Dell=True)
    bin_dl = nmt.NmtBin.from_edges(l_min_edges, l_max_edges, is_Dell=True)
    ell_arr = bin_dl.get_effective_ells()
    cl = np.load(f'../../src/cmbsim/cmbdata/cmbcl_8k.npy')[:lmax+1,2]
    print(f'{cl.shape=}')
    l = np.arange(len(cl))

    pcfn_mean = np.mean([np.load(f'./dl_res/std/pcfn/{rlz_idx}.npy') - np.load(f'./dl_res/std/n_pcfn/{rlz_idx}.npy') for rlz_idx in np.arange(1,200)], axis=0)
    pcfn_std = np.std([np.load(f'./dl_res/std/pcfn/{rlz_idx}.npy') - np.load(f'./dl_res/std/n_pcfn/{rlz_idx}.npy') for rlz_idx in np.arange(1,200)], axis=0)
    cfn_mean = np.mean([np.load(f'./dl_res/std/cfn/{rlz_idx}.npy') - np.load(f'./dl_res/std/n_cfn/{rlz_idx}.npy') for rlz_idx in np.arange(1,200)], axis=0)
    cfn_std = np.std([np.load(f'./dl_res/std/cfn/{rlz_idx}.npy') - np.load(f'./dl_res/std/n_cfn/{rlz_idx}.npy') for rlz_idx in np.arange(1,200)], axis=0)
    rmv_mean = np.mean([np.load(f'./dl_res/std/rmv/{rlz_idx}.npy') - np.load(f'./dl_res/std/n_rmv/{rlz_idx}.npy') for rlz_idx in np.arange(1,200)], axis=0)
    rmv_std = np.std([np.load(f'./dl_res/std/rmv/{rlz_idx}.npy') - np.load(f'./dl_res/std/n_rmv/{rlz_idx}.npy') for rlz_idx in np.arange(1,200)], axis=0)
    inp_mean = np.mean([np.load(f'./dl_res/std/inp/{rlz_idx}.npy') - np.load(f'./dl_res/std/n_inp/{rlz_idx}.npy') for rlz_idx in np.arange(1,200)], axis=0)
    inp_std = np.std([np.load(f'./dl_res/std/inp/{rlz_idx}.npy') - np.load(f'./dl_res/std/n_inp/{rlz_idx}.npy') for rlz_idx in np.arange(1,200)], axis=0)
    print(f'mean std over')
    fid_mean = np.mean([np.load(f'./dl_res/fid_cmb/{rlz_idx}.npy') for rlz_idx in np.arange(1,200)], axis=0)
    fid_std = np.std([np.load(f'./dl_res/fid_cmb/{rlz_idx}.npy') for rlz_idx in np.arange(1,200)], axis=0)

    # Create figure with 2 subplots (main and subfigure), sharing the x-axis
    fig, (ax_main, ax_sub) = plt.subplots(2, 1, figsize=(10, 8), sharex=True, gridspec_kw={'height_ratios': [2, 1]})

    s = 5
    lmax_ell_arr = len(ell_arr)
    dl_in = bin_dl.bin_cell(cls_in=cl)

    # Set the y-axis to logarithmic scale for both the main plot and subfigure
    ax_main.set_yscale('log')
    ax_sub.set_yscale('log')

    # Plot mean values in the main axis (no error bars here)
    ax_main.scatter(ell_arr, pcfn_mean[:lmax_ell_arr], s=s, label='PS + CMB + FG + NOISE')
    ax_main.scatter(ell_arr, cfn_mean[:lmax_ell_arr], s=s, label='CMB + FG + NOISE')
    ax_main.scatter(ell_arr, rmv_mean[:lmax_ell_arr], s=s, label='Template Fitting method')
    ax_main.scatter(ell_arr, inp_mean[:lmax_ell_arr], s=s, label='Recycling + Inpaint on B')
    ax_main.scatter(ell_arr, fid_mean[:lmax_ell_arr], s=s, label='Fiducial CMB')
    ax_main.loglog(l, l*(l+1)*cl/(2*np.pi), label='cmb input')
    ax_main.scatter(ell_arr, dl_in,s=s, label='bin dl')

    # Set labels and title for the main plot
    ax_main.set_ylabel('$D_\\ell^{BB} [\mu K^2]$')
    # ax_main.set_xlim(2, lmax_eff)
    # ax_main.set_ylim(, lmax_eff)
    ax_main.set_title('Debiased power spectra')
    ax_main.legend()

    # Plot standard deviation in the subfigure (using scatter with no error bars)
    ax_sub.scatter(ell_arr, pcfn_std[:lmax_ell_arr], s=s, label='PS + CMB + FG + NOISE')
    ax_sub.scatter(ell_arr, cfn_std[:lmax_ell_arr], s=s, label='CMB + FG + NOISE')
    ax_sub.scatter(ell_arr, rmv_std[:lmax_ell_arr], s=s, label='Template Fitting method')
    ax_sub.scatter(ell_arr, inp_std[:lmax_ell_arr], s=s, label='Recycling + Inpaint on B')
    ax_sub.scatter(ell_arr, fid_std[:lmax_ell_arr], s=s, label='Fiducial CMB')

    # Set labels for the subfigure (only xlabel here)
    ax_sub.set_xlabel('$\\ell$')
    ax_sub.set_ylabel('Standard Deviation')
    # ax_sub.set_ylim(5e-4, 3e-2)

    # Adjust layout for better spacing
    plt.tight_layout()
    plt.subplots_adjust(hspace=0)


    # Show plot
    plt.show()

def plot_ms1():
    bl = hp.gauss_beam(fwhm=np.deg2rad(beam)/60, lmax=lmax, pol=True)[:,2]
    l_min_edges, l_max_edges = generate_bins(l_min_start=30, delta_l_min=30, l_max=lmax+1, fold=0.2)
    # delta_ell = 30
    # bin_dl = nmt.NmtBin.from_nside_linear(nside, nlb=delta_ell, is_Dell=True)
    # bin_dl = nmt.NmtBin.from_lmax_linear(lmax=lmax, nlb=30, is_Dell=True)
    bin_dl = nmt.NmtBin.from_edges(l_min_edges, l_max_edges, is_Dell=True)
    ell_arr = bin_dl.get_effective_ells()
    cl = np.load(f'../../src/cmbsim/cmbdata/cmbcl_8k.npy')[:lmax+1,2]
    print(f'{cl.shape=}')
    l = np.arange(len(cl))

    pcfn_mean = np.mean([np.load(f'./dl_res1/std/pcfn/{rlz_idx}.npy') - np.load(f'./dl_res1/std/n_pcfn/{rlz_idx}.npy') for rlz_idx in np.arange(1,200)], axis=0)
    n_mean = np.mean([np.load(f'./dl_res1/std/n_pcfn/{rlz_idx}.npy') for rlz_idx in np.arange(1,200)], axis=0)
    pcfn_std = np.std([np.load(f'./dl_res1/std/pcfn/{rlz_idx}.npy') - np.load(f'./dl_res1/std/n_pcfn/{rlz_idx}.npy') for rlz_idx in np.arange(1,200)], axis=0)
    cfn_mean = np.mean([np.load(f'./dl_res1/std/cfn/{rlz_idx}.npy') - np.load(f'./dl_res1/std/n_cfn/{rlz_idx}.npy') for rlz_idx in np.arange(1,200)], axis=0)
    cfn_std = np.std([np.load(f'./dl_res1/std/cfn/{rlz_idx}.npy') - np.load(f'./dl_res1/std/n_cfn/{rlz_idx}.npy') for rlz_idx in np.arange(1,200)], axis=0)
    rmv_mean = np.mean([np.load(f'./dl_res1/std/rmv/{rlz_idx}.npy') - np.load(f'./dl_res1/std/n_rmv/{rlz_idx}.npy') for rlz_idx in np.arange(1,200)], axis=0)
    rmv_std = np.std([np.load(f'./dl_res1/std/rmv/{rlz_idx}.npy') - np.load(f'./dl_res1/std/n_rmv/{rlz_idx}.npy') for rlz_idx in np.arange(1,200)], axis=0)
    inp_mean = np.mean([np.load(f'./dl_res/std/inp/{rlz_idx}.npy') - np.load(f'./dl_res/std/n_inp/{rlz_idx}.npy') for rlz_idx in np.arange(1,200)], axis=0)
    inp_std = np.std([np.load(f'./dl_res/std/inp/{rlz_idx}.npy') - np.load(f'./dl_res/std/n_inp/{rlz_idx}.npy') for rlz_idx in np.arange(1,200)], axis=0)
    print(f'mean std over')
    fid_mean = np.mean([np.load(f'./dl_res/fid_cmb/{rlz_idx}.npy') for rlz_idx in np.arange(1,200)], axis=0)
    fid_std = np.std([np.load(f'./dl_res/fid_cmb/{rlz_idx}.npy') for rlz_idx in np.arange(1,200)], axis=0)
    ps_mean = np.mean([np.load(f'./dl_res/fid_ps_cmb/{rlz_idx}.npy') for rlz_idx in np.arange(1,200)], axis=0)
    cf_mean = np.mean([np.load(f'./dl_res1/std/cf/{rlz_idx}.npy') for rlz_idx in np.arange(1,200)], axis=0)

    # Create figure with 2 subplots (main and subfigure), sharing the x-axis
    fig, (ax_main, ax_sub) = plt.subplots(2, 1, figsize=(10, 8), sharex=True, gridspec_kw={'height_ratios': [2, 1]})

    s = 5
    lmax_ell_arr = len(ell_arr)
    dl_in = bin_dl.bin_cell(cls_in=cl)

    # Set the y-axis to logarithmic scale for both the main plot and subfigure
    ax_main.set_yscale('log')
    ax_sub.set_yscale('log')

    # Plot mean values in the main axis (no error bars here)
    ax_main.scatter(ell_arr, pcfn_mean[:lmax_ell_arr], s=s, label='PS + CMB + FG + NOISE')
    ax_main.scatter(ell_arr, cfn_mean[:lmax_ell_arr], s=s, label='CMB + FG + NOISE')
    ax_main.scatter(ell_arr, rmv_mean[:lmax_ell_arr], s=s, label='Template Fitting method')
    ax_main.scatter(ell_arr, inp_mean[:lmax_ell_arr], s=s, label='Recycling + Inpaint on B')
    ax_main.scatter(ell_arr, fid_mean[:lmax_ell_arr], s=s, label='Fiducial CMB')
    # ax_main.scatter(ell_arr, n_mean[:lmax_ell_arr], s=s, label='Noise bias')
    # ax_main.scatter(ell_arr, ps_mean[:lmax_ell_arr] - fid_mean[:lmax_ell_arr], s=s, label='Point source at 155GHz')
    # ax_main.scatter(ell_arr, cf_mean[:lmax_ell_arr], s=s, label='cf mean')
    # ax_main.loglog(l, l*(l+1)*cl/(2*np.pi), label='cmb input')
    ax_main.scatter(ell_arr, dl_in,s=s, label='bin dl')

    # Set labels and title for the main plot
    ax_main.set_ylabel('$D_\\ell^{BB} [\mu K^2]$')
    # ax_main.set_xlim(2, lmax_eff)
    # ax_main.set_ylim(, lmax_eff)
    ax_main.set_title('Debiased power spectra')
    ax_main.legend()

    # Plot standard deviation in the subfigure (using scatter with no error bars)
    ax_sub.scatter(ell_arr, pcfn_std[:lmax_ell_arr], s=s, label='PS + CMB + FG + NOISE')
    ax_sub.scatter(ell_arr, cfn_std[:lmax_ell_arr], s=s, label='CMB + FG + NOISE')
    ax_sub.scatter(ell_arr, rmv_std[:lmax_ell_arr], s=s, label='Template Fitting method')
    ax_sub.scatter(ell_arr, inp_std[:lmax_ell_arr], s=s, label='Recycling + Inpaint on B')
    ax_sub.scatter(ell_arr, fid_std[:lmax_ell_arr], s=s, label='Fiducial CMB')

    # Set labels for the subfigure (only xlabel here)
    ax_sub.set_xlabel('$\\ell$')
    ax_sub.set_ylabel('Standard Deviation')
    # ax_sub.set_ylim(5e-4, 3e-2)

    # Adjust layout for better spacing
    plt.tight_layout()
    plt.subplots_adjust(hspace=0)

    # plt.savefig(f'/afs/ihep.ac.cn/users/w/wangyiming25/tmp/20250120/nilc_res.png', dpi=300)

    # Show plot
    plt.show()

def plot_ms2():
    bl = hp.gauss_beam(fwhm=np.deg2rad(beam)/60, lmax=lmax, pol=True)[:,2]
    l_min_edges, l_max_edges = generate_bins(l_min_start=30, delta_l_min=30, l_max=lmax+1, fold=0.2)
    # delta_ell = 30
    # bin_dl = nmt.NmtBin.from_nside_linear(nside, nlb=delta_ell, is_Dell=True)
    # bin_dl = nmt.NmtBin.from_lmax_linear(lmax=lmax, nlb=30, is_Dell=True)
    bin_dl = nmt.NmtBin.from_edges(l_min_edges, l_max_edges, is_Dell=True)
    ell_arr = bin_dl.get_effective_ells()
    cl = np.load(f'../../src/cmbsim/cmbdata/cmbcl_8k.npy')[:lmax+1,2]
    print(f'{cl.shape=}')
    l = np.arange(len(cl))

    pcfn_mean = np.mean([np.load(f'./dl_res1/std/pcfn/{rlz_idx}.npy') - np.load(f'./dl_res1/std/n_pcfn/{rlz_idx}.npy') for rlz_idx in np.arange(1,200)], axis=0)
    n_mean = np.mean([np.load(f'./dl_res1/std/n_pcfn/{rlz_idx}.npy') for rlz_idx in np.arange(1,200)], axis=0)
    pcfn_std = np.std([np.load(f'./dl_res1/std/pcfn/{rlz_idx}.npy') - np.load(f'./dl_res1/std/n_pcfn/{rlz_idx}.npy') for rlz_idx in np.arange(1,200)], axis=0)
    cfn_mean = np.mean([np.load(f'./dl_res1/std/cfn/{rlz_idx}.npy') - np.load(f'./dl_res1/std/n_cfn/{rlz_idx}.npy') for rlz_idx in np.arange(1,200)], axis=0)
    cfn_std = np.std([np.load(f'./dl_res1/std/cfn/{rlz_idx}.npy') - np.load(f'./dl_res1/std/n_cfn/{rlz_idx}.npy') for rlz_idx in np.arange(1,200)], axis=0)
    rmv_mean = np.mean([np.load(f'./dl_res1/std/rmv/{rlz_idx}.npy') - np.load(f'./dl_res1/std/n_rmv/{rlz_idx}.npy') for rlz_idx in np.arange(1,200)], axis=0)
    rmv_std = np.std([np.load(f'./dl_res1/std/rmv/{rlz_idx}.npy') - np.load(f'./dl_res1/std/n_rmv/{rlz_idx}.npy') for rlz_idx in np.arange(1,200)], axis=0)
    inp_mean = np.mean([np.load(f'./dl_res/std/inp/{rlz_idx}.npy') - np.load(f'./dl_res/std/n_inp/{rlz_idx}.npy') for rlz_idx in np.arange(1,200)], axis=0)
    inp_std = np.std([np.load(f'./dl_res/std/inp/{rlz_idx}.npy') - np.load(f'./dl_res/std/n_inp/{rlz_idx}.npy') for rlz_idx in np.arange(1,200)], axis=0)
    print(f'mean std over')
    fid_mean = np.mean([np.load(f'./dl_res/fid_cmb/{rlz_idx}.npy') for rlz_idx in np.arange(1,200)], axis=0)
    fid_std = np.std([np.load(f'./dl_res/fid_cmb/{rlz_idx}.npy') for rlz_idx in np.arange(1,200)], axis=0)
    ps_mean = np.mean([np.load(f'./dl_res/fid_ps_cmb/{rlz_idx}.npy') for rlz_idx in np.arange(1,200)], axis=0)
    cf_mean = np.mean([np.load(f'./dl_res1/std/cf/{rlz_idx}.npy') for rlz_idx in np.arange(1,200)], axis=0)

    bias_std_2_pcfn = np.sqrt((pcfn_mean-fid_mean)**2 + pcfn_std**2)
    bias_std_2_cfn = np.sqrt((cfn_mean-fid_mean)**2 + cfn_std**2)
    bias_std_2_rmv = np.sqrt((rmv_mean-fid_mean)**2 + rmv_std**2)
    bias_std_2_inp= np.sqrt((inp_mean-fid_mean)**2 + inp_std**2)

    # Create figure with 2 subplots (main and subfigure), sharing the x-axis
    fig, (ax_main, ax_sub) = plt.subplots(2, 1, figsize=(10, 8), sharex=True, gridspec_kw={'height_ratios': [2, 1]})

    s = 3
    lmax_ell_arr = len(ell_arr)
    dl_in = bin_dl.bin_cell(cls_in=cl)

    # Set the y-axis to logarithmic scale for both the main plot and subfigure
    ax_main.set_yscale('log')
    ax_sub.set_yscale('log')

    # Plot mean values in the main axis (no error bars here)

    ax_main.errorbar(ell_arr, fid_mean[:lmax_ell_arr], yerr=fid_std[:lmax_ell_arr], fmt='.', capsize=s, label='Fiducial CMB', color='black')
    ax_main.errorbar(ell_arr+5.0, pcfn_mean[:lmax_ell_arr], yerr=pcfn_std[:lmax_ell_arr], fmt='.', capsize=s, label='PS + CMB + FG + NOISE')
    ax_main.errorbar(ell_arr+10.0, cfn_mean[:lmax_ell_arr], yerr=cfn_std[:lmax_ell_arr], fmt='.', capsize=s, label='CMB + FG + NOISE')
    ax_main.errorbar(ell_arr+15.0, rmv_mean[:lmax_ell_arr], yerr=rmv_std[:lmax_ell_arr], fmt='.', capsize=s, label='Template fitting method')
    ax_main.errorbar(ell_arr+20.0, inp_mean[:lmax_ell_arr], yerr=inp_std[:lmax_ell_arr], fmt='.', capsize=s, label='Recycling + Inpainting on B')

    # Set labels and title for the main plot
    ax_main.set_ylabel('$D_\\ell^{BB} [\mu K^2]$')
    # ax_main.set_xlim(2, lmax_eff)
    # ax_main.set_ylim(, lmax_eff)
    ax_main.set_title('Debiased power spectra')
    ax_main.legend()


    # Plot standard deviation in the subfigure (using scatter with no error bars)
    ax_sub.scatter(ell_arr+5.0, bias_std_2_pcfn[:lmax_ell_arr], s=s, label='PS + CMB + FG + NOISE')
    ax_sub.scatter(ell_arr+10.0, bias_std_2_cfn[:lmax_ell_arr], s=s, label='CMB + FG + NOISE')
    ax_sub.scatter(ell_arr+15.0, bias_std_2_rmv[:lmax_ell_arr], s=s, label='Template Fitting method')
    ax_sub.scatter(ell_arr+20.0, bias_std_2_inp[:lmax_ell_arr], s=s, label='Recycling + Inpaint on B')

    # Set labels for the subfigure (only xlabel here)
    ax_sub.set_xlabel('$\\ell$')
    ax_sub.set_ylabel('Sqrt of (bias^2 + std^2)')
    # ax_sub.set_ylim(5e-4, 3e-2)

    # Adjust layout for better spacing
    plt.tight_layout()
    plt.subplots_adjust(hspace=0)

    # plt.savefig(f'/afs/ihep.ac.cn/users/w/wangyiming25/tmp/20250120/nilc_res.png', dpi=300)

    # Show plot
    plt.show()

def plot_ms3():
    bl = hp.gauss_beam(fwhm=np.deg2rad(beam)/60, lmax=lmax, pol=True)[:,2]
    l_min_edges, l_max_edges = generate_bins(l_min_start=10, delta_l_min=30, l_max=lmax+1, fold=0.2)
    # delta_ell = 30
    # bin_dl = nmt.NmtBin.from_nside_linear(nside, nlb=delta_ell, is_Dell=True)
    # bin_dl = nmt.NmtBin.from_lmax_linear(lmax=lmax, nlb=30, is_Dell=True)
    bin_dl = nmt.NmtBin.from_edges(l_min_edges, l_max_edges, is_Dell=True)
    ell_arr = bin_dl.get_effective_ells()
    cl = np.load(f'../../src/cmbsim/cmbdata/cmbcl_8k.npy')[:lmax+1,2]
    print(f'{cl.shape=}')
    l = np.arange(len(cl))

    pcfn_mean = np.mean([np.load(f'./dl_res2/std/pcfn/{rlz_idx}.npy') - np.load(f'./dl_res2/std/n_pcfn/{rlz_idx}.npy') for rlz_idx in np.arange(1,200)], axis=0)
    n_mean = np.mean([np.load(f'./dl_res2/std/n_pcfn/{rlz_idx}.npy') for rlz_idx in np.arange(1,200)], axis=0)
    pcfn_std = np.std([np.load(f'./dl_res2/std/pcfn/{rlz_idx}.npy') - np.load(f'./dl_res2/std/n_pcfn/{rlz_idx}.npy') for rlz_idx in np.arange(1,200)], axis=0)
    cfn_mean = np.mean([np.load(f'./dl_res2/std/cfn/{rlz_idx}.npy') - np.load(f'./dl_res2/std/n_cfn/{rlz_idx}.npy') for rlz_idx in np.arange(1,200)], axis=0)
    cfn_std = np.std([np.load(f'./dl_res2/std/cfn/{rlz_idx}.npy') - np.load(f'./dl_res2/std/n_cfn/{rlz_idx}.npy') for rlz_idx in np.arange(1,200)], axis=0)
    rmv_mean = np.mean([np.load(f'./dl_res2/std/rmv/{rlz_idx}.npy') - np.load(f'./dl_res2/std/n_rmv/{rlz_idx}.npy') for rlz_idx in np.arange(1,200)], axis=0)
    rmv_std = np.std([np.load(f'./dl_res2/std/rmv/{rlz_idx}.npy') - np.load(f'./dl_res2/std/n_rmv/{rlz_idx}.npy') for rlz_idx in np.arange(1,200)], axis=0)
    inp_mean = np.mean([np.load(f'./dl_res/std/inp/{rlz_idx}.npy') - np.load(f'./dl_res/std/n_inp/{rlz_idx}.npy') for rlz_idx in np.arange(1,200)], axis=0)
    inp_std = np.std([np.load(f'./dl_res/std/inp/{rlz_idx}.npy') - np.load(f'./dl_res/std/n_inp/{rlz_idx}.npy') for rlz_idx in np.arange(1,200)], axis=0)
    print(f'mean std over')
    fid_mean = np.mean([np.load(f'./dl_res/fid_cmb/{rlz_idx}.npy') for rlz_idx in np.arange(1,200)], axis=0)
    fid_std = np.std([np.load(f'./dl_res/fid_cmb/{rlz_idx}.npy') for rlz_idx in np.arange(1,200)], axis=0)
    ps_mean = np.mean([np.load(f'./dl_res/fid_ps_cmb/{rlz_idx}.npy') for rlz_idx in np.arange(1,200)], axis=0)
    cf_mean = np.mean([np.load(f'./dl_res2/std/cf/{rlz_idx}.npy') for rlz_idx in np.arange(1,200)], axis=0)

    # bias_std_2_pcfn = np.sqrt((pcfn_mean-fid_mean)**2 + pcfn_std**2)
    # bias_std_2_cfn = np.sqrt((cfn_mean-fid_mean)**2 + cfn_std**2)
    # bias_std_2_rmv = np.sqrt((rmv_mean-fid_mean)**2 + rmv_std**2)
    # bias_std_2_inp= np.sqrt((inp_mean-fid_mean)**2 + inp_std**2)

    # Create figure with 2 subplots (main and subfigure), sharing the x-axis
    fig, (ax_main, ax_sub) = plt.subplots(2, 1, figsize=(10, 8), sharex=True, gridspec_kw={'height_ratios': [2, 1]})

    s = 3
    lmax_ell_arr = len(ell_arr)
    dl_in = bin_dl.bin_cell(cls_in=cl)

    # Set the y-axis to logarithmic scale for both the main plot and subfigure
    ax_main.set_yscale('log')
    ax_sub.set_yscale('log')

    # Plot mean values in the main axis (no error bars here)

    # ax_main.errorbar(ell_arr, fid_mean[:lmax_ell_arr], yerr=fid_std[:lmax_ell_arr], fmt='.', capsize=s, label='Fiducial CMB', color='black')
    ax_main.errorbar(ell_arr+5.0, pcfn_mean[:lmax_ell_arr], yerr=pcfn_std[:lmax_ell_arr], fmt='.', capsize=s, label='PS + CMB + FG + NOISE')
    ax_main.errorbar(ell_arr+10.0, cfn_mean[:lmax_ell_arr], yerr=cfn_std[:lmax_ell_arr], fmt='.', capsize=s, label='CMB + FG + NOISE')
    ax_main.errorbar(ell_arr+15.0, rmv_mean[:lmax_ell_arr], yerr=rmv_std[:lmax_ell_arr], fmt='.', capsize=s, label='Template fitting method')
    # ax_main.errorbar(ell_arr+20.0, inp_mean[:lmax_ell_arr], yerr=inp_std[:lmax_ell_arr], fmt='.', capsize=s, label='Recycling + Inpainting on B')

    # Set labels and title for the main plot
    ax_main.set_ylabel('$D_\\ell^{BB} [\mu K^2]$')
    # ax_main.set_xlim(2, lmax_eff)
    # ax_main.set_ylim(, lmax_eff)
    ax_main.set_title('Debiased power spectra')
    ax_main.legend()


    # Plot standard deviation in the subfigure (using scatter with no error bars)
    # ax_sub.scatter(ell_arr+5.0, bias_std_2_pcfn[:lmax_ell_arr], s=s, label='PS + CMB + FG + NOISE')
    # ax_sub.scatter(ell_arr+10.0, bias_std_2_cfn[:lmax_ell_arr], s=s, label='CMB + FG + NOISE')
    # ax_sub.scatter(ell_arr+15.0, bias_std_2_rmv[:lmax_ell_arr], s=s, label='Template Fitting method')
    # ax_sub.scatter(ell_arr+20.0, bias_std_2_inp[:lmax_ell_arr], s=s, label='Recycling + Inpaint on B')

    # Set labels for the subfigure (only xlabel here)
    ax_sub.set_xlabel('$\\ell$')
    ax_sub.set_ylabel('Sqrt of (bias^2 + std^2)')
    # ax_sub.set_ylim(5e-4, 3e-2)

    # Adjust layout for better spacing
    plt.tight_layout()
    plt.subplots_adjust(hspace=0)

    # plt.savefig(f'/afs/ihep.ac.cn/users/w/wangyiming25/tmp/20250120/nilc_res.png', dpi=300)

    # Show plot
    plt.show()

def plot_ms4():
    bl = hp.gauss_beam(fwhm=np.deg2rad(beam)/60, lmax=lmax, pol=True)[:,2]
    l_min_edges, l_max_edges = generate_bins(l_min_start=10, delta_l_min=30, l_max=lmax+1, fold=0.2)
    # delta_ell = 30
    # bin_dl = nmt.NmtBin.from_nside_linear(nside, nlb=delta_ell, is_Dell=True)
    bin_dl = nmt.NmtBin.from_lmax_linear(lmax=lmax, nlb=40, is_Dell=True)
    # bin_dl = nmt.NmtBin.from_edges(l_min_edges, l_max_edges, is_Dell=True)
    ell_arr = bin_dl.get_effective_ells()
    cl = np.load(f'../../src/cmbsim/cmbdata/cmbcl_8k.npy')[:lmax+1,2]
    print(f'{cl.shape=}')
    l = np.arange(len(cl))

    pcfn_mean = np.mean([np.load(f'./dl_res3/std/pcfn/{rlz_idx}.npy') - np.load(f'./dl_res3/std/n_pcfn/{rlz_idx}.npy') for rlz_idx in np.arange(1,200)], axis=0)
    n_mean = np.mean([np.load(f'./dl_res3/std/n_pcfn/{rlz_idx}.npy') for rlz_idx in np.arange(1,200)], axis=0)
    pcfn_std = np.std([np.load(f'./dl_res3/std/pcfn/{rlz_idx}.npy') - np.load(f'./dl_res3/std/n_pcfn/{rlz_idx}.npy') for rlz_idx in np.arange(1,200)], axis=0)
    cfn_mean = np.mean([np.load(f'./dl_res3/std/cfn/{rlz_idx}.npy') - np.load(f'./dl_res3/std/n_cfn/{rlz_idx}.npy') for rlz_idx in np.arange(1,200)], axis=0)
    cfn_std = np.std([np.load(f'./dl_res3/std/cfn/{rlz_idx}.npy') - np.load(f'./dl_res3/std/n_cfn/{rlz_idx}.npy') for rlz_idx in np.arange(1,200)], axis=0)
    rmv_mean = np.mean([np.load(f'./dl_res3/std/rmv/{rlz_idx}.npy') - np.load(f'./dl_res3/std/n_rmv/{rlz_idx}.npy') for rlz_idx in np.arange(1,200)], axis=0)
    rmv_std = np.std([np.load(f'./dl_res3/std/rmv/{rlz_idx}.npy') - np.load(f'./dl_res3/std/n_rmv/{rlz_idx}.npy') for rlz_idx in np.arange(1,200)], axis=0)
    inp_mean = np.mean([np.load(f'./dl_res3/std/inp/{rlz_idx}.npy') - np.load(f'./dl_res3/std/n_inp/{rlz_idx}.npy') for rlz_idx in np.arange(1,200)], axis=0)
    inp_std = np.std([np.load(f'./dl_res3/std/inp/{rlz_idx}.npy') - np.load(f'./dl_res3/std/n_inp/{rlz_idx}.npy') for rlz_idx in np.arange(1,200)], axis=0)
    print(f'mean std over')
    fid_mean = np.mean([np.load(f'./dl_res3/fid_cmb/{rlz_idx}.npy') for rlz_idx in np.arange(1,200)], axis=0)
    fid_std = np.std([np.load(f'./dl_res3/fid_cmb/{rlz_idx}.npy') for rlz_idx in np.arange(1,200)], axis=0)
    ps_mean = np.mean([np.load(f'./dl_res/fid_ps_cmb/{rlz_idx}.npy') for rlz_idx in np.arange(1,200)], axis=0)
    cf_mean = np.mean([np.load(f'./dl_res3/std/cf/{rlz_idx}.npy') for rlz_idx in np.arange(1,200)], axis=0)

    bias_std_2_pcfn = np.sqrt((pcfn_mean-fid_mean)**2 + pcfn_std**2)
    bias_std_2_cfn = np.sqrt((cfn_mean-fid_mean)**2 + cfn_std**2)
    bias_std_2_rmv = np.sqrt((rmv_mean-fid_mean)**2 + rmv_std**2)
    bias_std_2_inp= np.sqrt((inp_mean-fid_mean)**2 + inp_std**2)

    # Create figure with 2 subplots (main and subfigure), sharing the x-axis
    fig, (ax_main, ax_sub) = plt.subplots(2, 1, figsize=(10, 8), sharex=True, gridspec_kw={'height_ratios': [2, 1]})

    s = 3
    lmax_ell_arr = len(ell_arr)
    dl_in = bin_dl.bin_cell(cls_in=cl)

    # Set the y-axis to logarithmic scale for both the main plot and subfigure
    ax_main.set_yscale('log')
    ax_sub.set_yscale('log')
    # ax_main.set_xscale('log')
    # ax_sub.set_xscale('log')


    # Plot mean values in the main axis (no error bars here)
    mk_s = 5

    ax_main.errorbar(ell_arr, fid_mean[:lmax_ell_arr], yerr=fid_std[:lmax_ell_arr], fmt='.', capsize=s, label='Fiducial CMB', color='black', markersize=mk_s)
    ax_main.errorbar(ell_arr+5.0, pcfn_mean[:lmax_ell_arr], yerr=pcfn_std[:lmax_ell_arr], fmt='.', capsize=s, label='PS + CMB + FG + NOISE', markersize=mk_s)
    ax_main.errorbar(ell_arr+10.0, cfn_mean[:lmax_ell_arr], yerr=cfn_std[:lmax_ell_arr], fmt='.', capsize=s, label='CMB + FG + NOISE', markersize=mk_s)
    ax_main.errorbar(ell_arr+15.0, rmv_mean[:lmax_ell_arr], yerr=rmv_std[:lmax_ell_arr], fmt='.', capsize=s, label='Template fitting method', markersize=mk_s)
    ax_main.errorbar(ell_arr+20.0, inp_mean[:lmax_ell_arr], yerr=inp_std[:lmax_ell_arr], fmt='.', capsize=s, label='Recycling + Inpainting on B', markersize=mk_s)

    # Set labels and title for the main plot
    ax_main.set_ylabel('$D_\\ell^{BB} [\mu K^2]$')
    ax_main.set_xlim(50, 1290)
    ax_main.set_ylim(9e-4, 2e-1)
    ax_main.set_title('Debiased power spectra')
    ax_main.legend()


    # Plot standard deviation in the subfigure (using scatter with no error bars)

    ax_sub.scatter(ell_arr, fid_std[:lmax_ell_arr], s=s, label='Fiducial CMB', color='black', marker='.')
    ax_sub.scatter(ell_arr+5.0, bias_std_2_pcfn[:lmax_ell_arr], s=s, label='PS + CMB + FG + NOISE', marker='.')
    ax_sub.scatter(ell_arr+10.0, bias_std_2_cfn[:lmax_ell_arr], s=s, label='CMB + FG + NOISE', marker='.')
    ax_sub.scatter(ell_arr+15.0, bias_std_2_rmv[:lmax_ell_arr], s=s, label='Template Fitting method', marker='.')
    ax_sub.scatter(ell_arr+20.0, bias_std_2_inp[:lmax_ell_arr], s=s, label='Recycling + Inpaint on B', marker='.')

    # Set labels for the subfigure (only xlabel here)
    ax_sub.set_xlabel('$\\ell$')
    ax_sub.set_ylabel('Sqrt of (bias^2 + std^2)')
    # ax_sub.set_ylim(5e-4, 3e-2)
    # ax_sub.set_ylim(5e-4, 3e-2)

    # Adjust layout for better spacing
    plt.tight_layout()
    plt.subplots_adjust(hspace=0)

    plt.savefig(f'/afs/ihep.ac.cn/users/w/wangyiming25/tmp/20250131/nilc_res.png', dpi=300)

    # Show plot
    plt.show()


def get_ps_power():
    pass


def from_cl_to_bandpower():
    pass

# calc_dl()
# calc_dl1()
# calc_dl2()
# calc_dl3()
# get_mean_std()
# plot_ms()
# plot_ms1()
# plot_ms2()
# plot_ms3()
plot_ms4()

