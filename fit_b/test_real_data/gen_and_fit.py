import numpy as np
import healpy as hp
import pandas as pd
import matplotlib.pyplot as plt

from fit_b_v3 import Fit_on_B
from pathlib import Path

lmax = 2000
nside = 2048
npix = hp.nside2npix(nside)
beam = 11
rlz_idx=16

noise_seeds = np.load('./seeds_noise_2k.npy')
cmb_seeds = np.load('./seeds_cmb_2k.npy')

def gen_b_map():

    ps = np.load('../../fitdata/2048/PS/215/ps.npy')

    nstd = np.load('../../FGSim/NSTDNORTH/2048/215.npy')
    np.random.seed(seed=noise_seeds[rlz_idx])
    noise = nstd * np.random.normal(loc=0, scale=1, size=(3, npix))
    print(f"{np.std(noise[1])=}")

    # cmb_iqu = np.load(f'../../fitdata/2048/CMB/215/{rlz_idx}.npy')
    # cls = np.load('../../src/cmbsim/cmbdata/cmbcl.npy')
    cls = np.load('../../src/cmbsim/cmbdata/cmbcl_8k.npy')
    # cmb_iqu = hp.synfast(cls.T, nside=nside, fwhm=np.deg2rad(beam)/60, new=True, lmax=1999)
    np.random.seed(seed=cmb_seeds[rlz_idx])
    cmb_iqu = hp.synfast(cls.T, nside=nside, fwhm=np.deg2rad(beam)/60, new=True, lmax=3*nside-1)

    # l = np.arange(lmax+1)
    # cls_out = hp.anafast(cmb_iqu, lmax=lmax)

    # plt.loglog(l, l*(l+1)*cls_out[2])
    # plt.show()


    # pcn = ps + cmb_iqu
    # pcn = ps + noise

    m = noise + ps + cmb_iqu
    m_b = hp.alm2map(hp.map2alm(m)[2], nside=nside)

    # cn = noise + cmb_iqu
    # m_b_cn = hp.alm2map(hp.map2alm(cn)[2], nside=nside)

    # m = np.load('./1_8k.npy')
    # np.save('./1_6k_pcn.npy', m_b)
    # np.save('./1_6k_cn.npy', m_b_cn)
    return m_b

def main():
    m_b = gen_b_map()
    np.save('./data_for_test/map_from_gen.npy', m_b)

    df_mask = pd.read_csv('../../pp_P/mask/mask_csv/215.csv')
    df_ps = pd.read_csv('../../pp_P/mask/ps_csv/215.csv')

    lmax = 1999
    nside = 2048
    beam = 11
    freq = 215
    flux_idx = 11
    lon = df_mask.at[flux_idx, 'lon']
    print(f'{lon=}')
    lat = df_mask.at[flux_idx, 'lat']
    qflux = df_mask.at[flux_idx, 'qflux']
    uflux = df_mask.at[flux_idx, 'uflux']
    pflux = df_mask.at[flux_idx, 'pflux']


    # m_b = np.load('./1_6k_pcn.npy')
    obj = Fit_on_B(m_b, df_mask, df_ps, flux_idx, qflux, uflux, pflux, lmax, nside, beam, lon, lat, freq, r_fold=2.5, r_fold_rmv=5)
    obj.params_for_fitting()
    # obj.calc_inv_cov(mode='cn')
    obj.calc_inv_cov(mode='cn1')
    # obj.calc_inv_cov(mode='n1')

    # obj.fit_1_ps()
    # print(f'{obj.P=}, {obj.ps_2phi=}')
    obj.run_fit()

    # path_params = Path(f'./params/{flux_idx}/fit_1')
    # path_params.mkdir(parents=True, exist_ok=True)

    # np.save(path_params / Path(f'P_{rlz_idx}.npy'), obj.P)
    # np.save(path_params / Path(f'phi_{rlz_idx}.npy'), obj.ps_2phi)

    # path_params = Path(f'./params/{flux_idx}/fit_2')
    # path_params.mkdir(parents=True, exist_ok=True)

    # obj.fit_2_ps()
    # np.save(path_params / Path(f'P_{rlz_idx}.npy'), obj.P)
    # np.save(path_params / Path(f'phi_{rlz_idx}.npy'), obj.ps_2phi)

    # obj.params_for_testing()
    # obj.test_residual()


main()

