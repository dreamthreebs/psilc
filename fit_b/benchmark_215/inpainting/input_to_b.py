import numpy as np
import healpy as hp
import matplotlib.pyplot as plt

from pathlib import Path
from eblc_base import EBLeakageCorrection

rlz_idx=0
nside = 2048
mask = hp.read_map(f'./mask/mask_1.fits')

noise_seed = np.load('../../seeds_noise_2k.npy')
npix = hp.nside2npix(nside)

def gen_map():

    # ps = np.load('../data/ps/ps.npy')

    nstd = np.load('../../../FGSim/NSTDNORTH/2048/215.npy')
    np.random.seed(seed=noise_seed[rlz_idx])
    # noise = nstd * np.random.normal(loc=0, scale=1, size=(3, npix))
    noise = nstd * np.random.normal(loc=0, scale=1, size=(3, npix))
    print(f"{np.std(noise[1])=}")

    # # cmb_iqu = np.load(f'../../fitdata/2048/CMB/215/{rlz_idx}.npy')
    # # cls = np.load('../../src/cmbsim/cmbdata/cmbcl.npy')
    # cls = np.load('../../../src/cmbsim/cmbdata/cmbcl_8k.npy')
    # np.random.seed(seed=cmb_seed[rlz_idx])
    # # cmb_iqu = hp.synfast(cls.T, nside=nside, fwhm=np.deg2rad(beam)/60, new=True, lmax=1999)
    # cmb_iqu = hp.synfast(cls.T, nside=nside, fwhm=np.deg2rad(beam)/60, new=True, lmax=3*nside-1)

    # l = np.arange(lmax+1)
    # cls_out = hp.anafast(cmb_iqu, lmax=lmax)


    # m = noise + ps + cmb_iqu
    m = noise
    # cn = noise + cmb_iqu

    # m = np.load('./1_8k.npy')
    # np.save('./1_6k_pcn.npy', m)
    # np.save('./1_6k_cn.npy', cn)
    return m
m = gen_map()

m_q = m[1]
m_u = m[2]
m_t = m[0]

obj = EBLeakageCorrection(np.array([m_t, m_q, m_u]), lmax=3*nside-1, nside=nside, mask=mask, post_mask=mask)
_,_,cln_b = obj.run_eblc()

path_b = Path('./input_n')
path_b.mkdir(exist_ok=True, parents=True)
hp.write_map(path_b / Path(f'{rlz_idx}.fits'), cln_b, overwrite=True)



