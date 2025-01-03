import numpy as np
import healpy as hp
import matplotlib.pyplot as plt

from pathlib import Path
from eblc_base_slope import EBLeakageCorrection

nside = 512
npix = hp.nside2npix(nside=nside)
beam = 67
mask = np.load('../../src/mask/north/BINMASKG.npy')
# m = np.load('../../fitdata/synthesis_data/2048/CMBNOISE/270/1.npy')
rlz_idx = 0
cmb_seed = np.load('../seeds_cmb_2k.npy')
noise_seed = np.load('../seeds_noise_2k.npy')
fg_seed = np.load('../seeds_fg_2k.npy')

def gen_fg_cl():
    Cl_TT = np.load('../Cl_fg/data/cl_fg_TT.npy')
    Cl_EE = np.load('../Cl_fg/data/cl_fg_EE.npy')
    Cl_BB = np.load('../Cl_fg/data/cl_fg_BB.npy')
    Cl_TE = np.zeros_like(Cl_TT)
    return np.array([Cl_TT, Cl_EE, Cl_BB, Cl_TE])

def gen_map(lmax, component):

    if component == 'c':
        cls = np.load('../../src/cmbsim/cmbdata/cmbcl_8k.npy').T
        np.random.seed(seed=cmb_seed[rlz_idx])
        cmb_iqu = hp.synfast(cls=cls, nside=nside, fwhm=np.deg2rad(beam)/60, lmax=3*nside-1, new=True)
        return cmb_iqu

    elif component == 'cn':
        cls = np.load('../../src/cmbsim/cmbdata/cmbcl_8k.npy').T
        np.random.seed(seed=cmb_seed[rlz_idx])
        cmb_iqu = hp.synfast(cls=cls, nside=nside, fwhm=np.deg2rad(beam)/60, lmax=3*nside-1, new=True)

        nstd = np.load('../../FGSim/NSTDNORTH/512/30.npy')
        np.random.seed(seed=noise_seed[rlz_idx])
        noise = nstd * np.random.normal(loc=0, scale=1, size=(3, npix))
        return cmb_iqu + noise

    elif component == 'n':
        nstd = np.load('../../FGSim/NSTDNORTH/512/30.npy')
        np.random.seed(seed=noise_seed[rlz_idx])
        noise = nstd * np.random.normal(loc=0, scale=1, size=(3, npix))
        return noise

    elif component == 'f':
        cls_fg = gen_fg_cl()
        np.random.seed(seed=fg_seed[rlz_idx])
        m_fg = hp.synfast(cls=cls_fg, nside=nside, fwhm=0, new=True, lmax=600)
        return m_fg

    elif component == 'cfn':
        cls = np.load('../../src/cmbsim/cmbdata/cmbcl_8k.npy').T
        np.random.seed(seed=cmb_seed[rlz_idx])
        cmb_iqu = hp.synfast(cls=cls, nside=nside, fwhm=np.deg2rad(beam)/60, lmax=3*nside-1, new=True)

        nstd = np.load('../../FGSim/NSTDNORTH/512/30.npy')
        np.random.seed(seed=noise_seed[rlz_idx])
        noise = nstd * np.random.normal(loc=0, scale=1, size=(3, npix))

        cls_fg = gen_fg_cl()
        np.random.seed(seed=fg_seed[rlz_idx])
        m_fg = hp.synfast(cls=cls_fg, nside=nside, fwhm=0, new=True, lmax=600)
        return m_fg + noise + cmb_iqu


m = gen_map(lmax=1000, component='c')
m_b = hp.alm2map(hp.map2alm(m)[2], nside=nside) * mask

print(f'component=c')
print(f'method=cutqufitqu')
print(f'eblc lmax=600')

lmax = 600
obj = EBLeakageCorrection(m=m, lmax=lmax, nside=nside, mask=mask, post_mask=mask)
_,_, cln_b_2k = obj.run_eblc()
slope = obj.return_slope()
print(f'{slope=}')

print(f'eblc lmax=3*nside-1')
# lmax = 3*nside-1

# lmax = 600
# obj = EBLeakageCorrection(m=m, lmax=lmax, nside=nside, mask=mask, post_mask=mask, slope_in=2.26)
# _,_, cln_b_6k = obj.run_eblc()

# lmax = 600
# obj = EBLeakageCorrection(m=m, lmax=lmax, nside=nside, mask=mask, post_mask=mask, slope=2.46)
# _,_, cln_b_8k = obj.run_eblc()

# lmax = 600
# obj = EBLeakageCorrection(m=m, lmax=lmax, nside=nside, mask=mask, post_mask=mask, slope=2.66)
# _,_, cln_b_10k = obj.run_eblc()

# lmax = 600
# obj = EBLeakageCorrection(m=m, lmax=lmax, nside=nside, mask=mask, post_mask=mask, slope=2.86)
# _,_, cln_b_12k = obj.run_eblc()

# lmax = 600
# obj = EBLeakageCorrection(m=m, lmax=lmax, nside=nside, mask=mask, post_mask=mask, slope=3.06)
# _,_, cln_b_14k = obj.run_eblc()




# hp.orthview(cln_b_2k, rot=[100,50,0], title='eblc 2k')
# hp.orthview(cln_b_6k, rot=[100,50,0], title='eblc 6k')
# hp.orthview(cln_b_6k-cln_b_2k, rot=[100,50,0], title='res')
# plt.show()

# path_data = Path('./data/check_bias')
# path_data.mkdir(exist_ok=True, parents=True)

# np.save(path_data / Path('no_leakage.npy'), m_b)
# np.save(path_data / Path('eblc_cmb.npy'), cln_b_2k)
# np.save(path_data / Path('eblc_226.npy'), cln_b_6k)
# np.save(path_data / Path('eblc_246.npy'), cln_b_8k)
# np.save(path_data / Path('eblc_266.npy'), cln_b_10k)
# np.save(path_data / Path('eblc_286.npy'), cln_b_12k)
# np.save(path_data / Path('eblc_306.npy'), cln_b_14k)
