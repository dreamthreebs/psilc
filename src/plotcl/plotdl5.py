import numpy as np
import healpy as hp
import matplotlib.pyplot as plt
import pymaster as nmt

plt.rcParams['lines.markersize'] = 5


def calc_dl_from_scalar_map(scalar_map, bl, apo_mask):
    scalar_field = nmt.NmtField(apo_mask, [scalar_map], beam=bl, masked_on_input=False)
    dl = nmt.compute_full_master(scalar_field, scalar_field, bin_dl)
    return dl[0]


if __name__ == '__main__':
    lmax=500
    l = np.arange(lmax+1)
    nside=512
    iqutrue = np.load('../../FGSim/CMB/270.npy')
    mtrue = hp.alm2map(hp.map2alm(iqutrue, lmax=lmax)[2], nside=nside)
    cl = hp.anafast(mtrue, lmax=lmax)
    full_mask = np.ones_like(mtrue)
    # smcmb = np.load('../../data/cutqufitb/smcmb/data.npy')[0]

    mpilc = np.load('../../data/band5smooth4/simpilc/pilc_map.npy')
    mhilc = np.load('../../data/band5smooth4/simhilc/hilc_map.npy')
    mnilc = np.load('../../data/band5smooth4/simnilc/nilc_map0.npy')
    
    mpfgres = np.load('../../data/band5smooth4/simpilc/pilc_fgres_map.npy')
    mhfgres = np.load('../../data/band5smooth4/simhilc/hilc_fgres_map.npy')
    mnfgres = np.load('../../data/band5smooth4/simnilc/nilc_fgres_map0.npy')

    mpnoiseres = np.load('../../data/band5smooth4/simpilc/pilc_noise_res_map.npy')
    mhnoiseres = np.load('../../data/band5smooth4/simhilc/hilc_noise_res_map.npy')
    mnnoiseres = np.load('../../data/band5smooth4/simnilc/nilc_noise_res_map0.npy')

    apo_mask = np.load('../mask/north_smooth/APOMASKC1_5.npy')
    bl = hp.gauss_beam(np.deg2rad(63)/60, lmax=2000, pol=True)[:,2]
    bl_true = hp.gauss_beam(np.deg2rad(9)/60, lmax=2000, pol=True)[:,2]
    bin_dl = nmt.NmtBin.from_edges([20,50,100,150,200,250],[50,100,150,200,250,300], is_Dell=True)
    ell_arr = bin_dl.get_effective_ells()
    
    # dl_smcmb = calc_dl_from_scalar_map(smcmb, bl, apo_mask=apo_mask)

    dl_true = calc_dl_from_scalar_map(mtrue, bl_true, apo_mask=apo_mask)
    dl_pilc = calc_dl_from_scalar_map(mpilc, bl, apo_mask=apo_mask)
    dl_hilc = calc_dl_from_scalar_map(mhilc, bl, apo_mask=apo_mask)
    dl_nilc = calc_dl_from_scalar_map(mnilc, bl, apo_mask=apo_mask)

    dl_pfgres = calc_dl_from_scalar_map(mpfgres, bl, apo_mask=apo_mask)
    dl_hfgres = calc_dl_from_scalar_map(mhfgres, bl, apo_mask=apo_mask)
    dl_nfgres = calc_dl_from_scalar_map(mnfgres, bl, apo_mask=apo_mask)

    dl_pnoiseres = calc_dl_from_scalar_map(mpnoiseres, bl, apo_mask=apo_mask)
    dl_hnoiseres = calc_dl_from_scalar_map(mhnoiseres, bl, apo_mask=apo_mask)
    dl_nnoiseres = calc_dl_from_scalar_map(mnnoiseres, bl, apo_mask=apo_mask)


    # plt.plot(l*(l+1)*cl/(2*np.pi)/bl[:lmax+1]**2, label='dl')

    # plt.plot(ell_arr, dl_smcmb, label='smcmb')
    plt.plot(ell_arr, dl_true, label='input', marker='o')
    plt.plot(ell_arr, dl_pilc-dl_pnoiseres, label='pilc', marker='s')
    plt.plot(ell_arr, dl_hilc-dl_hnoiseres, label='hilc', marker='^')
    plt.plot(ell_arr, dl_nilc-dl_nnoiseres, label='nilc', marker='D')

    plt.plot(ell_arr, dl_pfgres, label='pilcfgres', marker='s')
    plt.plot(ell_arr, dl_hfgres, label='hilcfgres', marker='^')
    plt.plot(ell_arr, dl_nfgres, label='nilcfgres', marker='D')

    plt.ylim(1e-6,1e-1)
    plt.xlim(0,500)
    plt.xlabel('$\\ell$')
    plt.ylabel('$D_\\ell$')

    plt.legend()
    plt.semilogy()
    plt.show()


