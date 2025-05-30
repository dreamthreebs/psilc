import numpy as np
import healpy as hp
import matplotlib.pyplot as plt
import pandas as pd
import time
import pickle
import os,sys
import logging
import ipdb

from pathlib import Path
from iminuit import Minuit
from iminuit.cost import LeastSquares
from fit_qu import FitPolPS

# logging.basicConfig(level=logging.WARNING, format='%(asctime)s - %(levelname)s -%(name)s - %(message)s')
logging.basicConfig(level=logging.WARNING)
# logging.basicConfig(level=logging.INFO, format='%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
# logger.setLevel(logging.INFO)

rlz_idx=0
nside = 2048
lmax = 3 * nside - 1
npix = hp.nside2npix(nside)
beam = 67

noise_seed = np.load('../benchmark_215/seeds_noise_2k.npy')
cmb_seed = np.load('../benchmark_215/seeds_cmb_2k.npy')

def gen_map():

    ps = np.load('./data/ps/ps.npy')

    nstd = np.load('../../FGSim/NSTDNORTH/2048/30.npy')
    np.random.seed(seed=noise_seed[rlz_idx])
    # noise = nstd * np.random.normal(loc=0, scale=1, size=(3, npix))
    noise = nstd * np.random.normal(loc=0, scale=1, size=(3, npix))
    print(f"{np.std(noise[1])=}")

    # cmb_iqu = np.load(f'../../fitdata/2048/CMB/215/{rlz_idx}.npy')
    # cls = np.load('../../src/cmbsim/cmbdata/cmbcl.npy')
    cls = np.load('../../src/cmbsim/cmbdata/cmbcl_8k.npy')
    np.random.seed(seed=cmb_seed[rlz_idx])
    # cmb_iqu = hp.synfast(cls.T, nside=nside, fwhm=np.deg2rad(beam)/60, new=True, lmax=1999)
    cmb_iqu = hp.synfast(cls.T, nside=nside, fwhm=np.deg2rad(beam)/60, new=True, lmax=3*nside-1)

    # l = np.arange(lmax+1)
    # cls_out = hp.anafast(cmb_iqu, lmax=lmax)


    m = noise + ps + cmb_iqu
    # cn = noise + cmb_iqu

    # m = np.load('./1_8k.npy')
    # np.save('./1_6k_pcn.npy', m)
    # np.save('./1_6k_cn.npy', cn)
    return m

def calc_inv():
    freq = 30
    lmax = 1999
    nside = 2048
    beam = 67
    nstd = np.load(f'../../FGSim/NSTDNORTH/2048/{freq}.npy')
    nstd_q = nstd[1].copy()
    nstd_u = nstd[2].copy()

    time0 = time.perf_counter()
    # m = np.load(f'../../fitdata/synthesis_data/2048/PSNOISE/{freq}/0.npy')
    # m = np.load(f'../../fitdata/synthesis_data/2048/PSCMBNOISE/{freq}/3.npy')
    m = gen_map()
    # np.save('./data/pcn.npy', m)
    # m = np.load('./data/pcn.npy')

    m_q = m[1].copy()
    m_u = m[2].copy()
    logger.debug(f'{sys.getrefcount(m_q)-1=}')

    logger.info(f'time for fitting = {time.perf_counter()-time0}')

    df_mask = pd.read_csv('./mask/30.csv')
    print(f'{df_mask=}')
    df_ps = pd.read_csv('../../pp_P/mask/ps_csv/30.csv')

    logger.debug(f'{sys.getrefcount(m_q)-1=}')
    flux_idx=0
    obj = FitPolPS(m_q=m_q, m_u=m_u, freq=freq, nstd_q=nstd_q, nstd_u=nstd_u, flux_idx=flux_idx, df_mask=df_mask, df_ps=df_ps, lmax=lmax, nside=nside, radius_factor=1.5, beam=beam, epsilon=0.00001)

    logger.debug(f'{sys.getrefcount(m_q)-1=}')

    # obj.calc_definite_fixed_fg_cov()
    # obj.calc_covariance_matrix(mode='cmb+noise+fg')

    obj.calc_definite_fixed_cmb_cov()
    obj.calc_covariance_matrix(mode='cmb+noise')
    # obj.fit_all(cov_mode='cmb+noise')

    # obj.calc_covariance_matrix(mode='noise')
    # obj.fit_all(cov_mode='noise')

    # obj.fit_all(cov_mode='noise', mode='check_sigma')

calc_inv()







