import numpy as np
import healpy as hp
import matplotlib.pyplot as plt
from ctypes import *
from pathlib import Path

beam = 11
flux_idx = 0

def signal_handler(sig, frame):
    print('Ctrl+C pressed in child, exiting...')
    sys.exit(0)

def Calc_CovMat(l_range, nside, pixind, opt='E', mskopt=True):
    l = l_range.astype(np.float64)
    nl = len(l)
    print(f'{nl=}')

    bl = hp.gauss_beam(fwhm=np.deg2rad(beam)/60, lmax=10000, pol=True)
    bl = bl[2:nl+2,:]
    print(f'{bl[0:10,0]=}')
    print(f'{bl[0:10,1]=}')
    print(f'{bl[0:10,2]=}')
    print(f'{bl[0:10,3]=}')
    cl = np.load('../../src/cmbsim/cmbdata/cmbcl.npy')

    # Cl_TT = cl[2:nl+2,0] * bl[:,0]**2
    # Cl_EE = cl[2:nl+2,1] * bl[:,1]**2
    # Cl_BB = cl[2:nl+2,2] * bl[:,2]**2
    # Cl_TE = cl[2:nl+2,3] * bl[:,3]**2
    
    map_depth = 0.17177432059087
    Cl_NN = (map_depth*np.ones(shape=(nl,)))**2 / 3437.748**2
    print(f'{Cl_NN.shape=}')

    # nCl = np.zeros_like(Cl_TT)
    nCl = np.zeros_like(Cl_NN)

    if opt=='E':
    	Cls = np.array([Cl, Cl, nCl, Cl, nCl]) # TT,EE,BB,TE,TB
    elif opt=='B':
    	Cls = np.array([Cl, nCl, Cl, nCl, Cl])
    elif opt=='T':
        Cls = np.array([Cl, nCl, nCl, nCl, nCl])
    elif opt=='all':
        # Cls = np.array([Cl_TT, Cl_EE, Cl_BB, Cl_TE, nCl]) # Cl_TB is zero
        Cls = np.array([Cl_BB, nCl, nCl, nCl, nCl]) # calc B map cov
    elif opt=='N':
        Cls = np.array([Cl_NN, nCl, nCl, nCl, nCl])

    if mskopt == True:
    	pixind = Mask_Operation(nside)
    	npix = len(pixind)
    else:
    	# npix = hp.nside2npix(nside)
    	# pixind = np.arange(npix)
        # pixind = np.load('./ipix_fit_qu.npy')
        pass

    # print('npix=', npix)
    npix = len(pixind)
    vecst = hp.pix2vec(nside, pixind)
    vecs = np.array(vecst).T
    covmat = np.zeros((3*npix, 3*npix), dtype=np.float64)

    # use the c package to calculate the Covmat
    lib = cdll.LoadLibrary('../CovMat.so')
    #lib = cdll.LoadLibrary('./util/CovMat.so')
    CovMat = lib.CovMat
    CovMat(c_void_p(vecs.ctypes.data), c_void_p(l.ctypes.data), c_void_p(Cls.ctypes.data), c_void_p(covmat.ctypes.data), c_int(npix), c_int(nl))
    # covert back to 2d
    covmat = covmat.reshape((3*npix, 3*npix))

    return covmat

def is_pos_def(M):
	eigvals = np.linalg.eigvals(M)
	plt.plot(eigvals)
	plt.show()
	print(np.min(eigvals))
	return np.all(eigvals>-1e-5)

def check_symmetric(m, rtol=1e-05, atol=1e-05):
	return np.allclose(m, m.T, rtol=rtol, atol=atol)

def ChooseMat(M, opt):
    if opt=='all':
        TT = M[0:len(M):3, 0:len(M):3]
        print(f'{TT.shape=}')
        MP = TT

    if opt=='QQ':
        MP = M[1:len(M)+1:3, 1:len(M)+1:3]
    if opt=='UU':
        MP = M[2:len(M)+2:3, 2:len(M)+2:3]
    return MP

def main_one_ps():
    nside = 2048
    l_range = np.arange(2,3*nside)
    mskopt = False
    pixind = np.load(f'./data/pix_idx.npy')
    CovMat = Calc_CovMat(l_range, nside, pixind=pixind, opt='N', mskopt=mskopt)
    print(f'{CovMat.shape=}')
    CovMatPol = ChooseMat(CovMat, opt='all')
    print(f'{CovMatPol.shape=}')

    path_cmb_cov = Path('./noise_b_cov')
    path_cmb_cov.mkdir(exist_ok=True, parents=True)
    np.save(path_cmb_cov / Path(f'{flux_idx}.npy'), CovMatPol)

    print(CovMat[:9,:9])
    print(check_symmetric(CovMatPol))
    print(is_pos_def(CovMatPol))

def main_all_ps():
    l_range = np.arange(2,2000)
    nside = 2048
    mskopt = False
    for flux_idx in range(276):
        pixind = np.load(f'./pix_idx/{flux_idx}.npy')
        CovMat = Calc_CovMat(l_range, nside, pixind=pixind, opt='all', mskopt=mskopt)
        print(f'{CovMat.shape=}')
        CovMatPol = ChooseMat(CovMat, opt='all')
        print(f'{CovMatPol.shape=}')

        path_cmb_cov = Path('./cmb_b_cov')
        path_cmb_cov.mkdir(exist_ok=True, parents=True)
        np.save(path_cmb_cov / Path(f'{flux_idx}.npy'), CovMatPol)

    # print(CovMat[:9,:9])
    # print(check_symmetric(CovMatPol))
    # print(is_pos_def(CovMatPol))


if __name__=='__main__':
    main_one_ps()
    # main_all_ps()



