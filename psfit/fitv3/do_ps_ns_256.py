import numpy as np
import healpy as hp
import matplotlib.pyplot as plt
import pandas as pd
import time
import pickle
import os

from iminuit import Minuit
from iminuit.cost import LeastSquares
from numpy.polynomial.legendre import Legendre
from scipy.interpolate import CubicSpline

# from fit_ps_base import FitPointSource
# from fitv1 import FitPointSource
# from fitv2 import FitPointSource
# from discrete_fit1 import FitPointSource
from fit_base_256 import FitPointSource

def main():
    m = np.load('../../FGSim/FITDATA/256/PSNOISE/40.npy')[0]
    nstd = np.load('../../FGSim/NSTDNORTH/256/40.npy')[0]
    df_mask = pd.read_csv('../partial_sky_ps/ps_in_mask/mask40.csv')
    df_ps = pd.read_csv('../../test/ps_sort/sort_by_iflux/40.csv')

    lmax = 350
    nside = 256
    beam = 63
    bl = hp.gauss_beam(fwhm=np.deg2rad(beam)/60, lmax=lmax)
    cl_cmb = np.load('../../src/cmbsim/cmbdata/cmbcl.npy')[:lmax+1,0]
    cl_cmb = cl_cmb * bl**2

    chi2dof_list = []
    norm_beam_list = []
    norm_error_list = []
    fit_lon_list = []
    fit_lat_list = []
    num_ps_list = []


    for flux_idx in range(0,139):
        print(f'{flux_idx=}')
        lon = np.rad2deg(df_mask.at[flux_idx, 'lon'])
        lat = np.rad2deg(df_mask.at[flux_idx, 'lat'])
        iflux = df_mask.at[flux_idx, 'iflux']

        obj = FitPointSource(m=m, nstd=nstd, flux_idx=flux_idx, df_mask=df_mask, df_ps=df_ps, cl_cmb=None, lon=lon, lat=lat, iflux=iflux, lmax=lmax, nside=nside, radius_factor=1.0, beam=beam)

        # obj.see_true_map(m=m, lon=lon, lat=lat, nside=nside, beam=beam)
        # obj.find_nearby_ps_lon_lat()
        # obj.find_first_second_nearby_ps_lon_lat()
        # obj.fit_ps_ns(mode='10params')
        obj.calc_covariance_matrix(mode='noise', cmb_cov_fold='../cmb_cov_calc/cov')
        num_ps, chi2dof, norm_beam, norm_error, fit_lon, fit_lat =  obj.fit_all()
        # print(f'{norm_beam=}, {norm_error=}, {fit_lon=}, {fit_lat=}, {chi2dof=}')
        num_ps_list.append(num_ps)
        chi2dof_list.append(chi2dof)
        norm_beam_list.append(norm_beam)
        norm_error_list.append(norm_error)
        fit_lon_list.append(fit_lon)
        fit_lat_list.append(fit_lat)
    if not os.path.exists('./ps_ns_data_256'):
        os.mkdir('./ps_ns_data_256')
    np.save("./ps_ns_data_256/num_ps.npy", np.array(num_ps_list))
    np.save("./ps_ns_data_256/chi2dof.npy", np.array(chi2dof_list))
    np.save("./ps_ns_data_256/norm_beam.npy",np.array(norm_beam_list))
    np.save("./ps_ns_data_256/norm_error.npy",np.array(norm_error_list))
    np.save("./ps_ns_data_256/fit_lon.npy",np.array(fit_lon_list))
    np.save("./ps_ns_data_256/fit_lat.npy",np.array(fit_lat_list))

def calc_cov():
    m = np.load('../../FGSim/FITDATA/256/PSNOISE/40.npy')[0]
    nstd = np.load('../../FGSim/NSTDNORTH/256/40.npy')[0]
    df_mask = pd.read_csv('../partial_sky_ps/ps_in_mask/mask40.csv')
    df_ps = pd.read_csv('../../test/ps_sort/sort_by_iflux/40.csv')

    lmax = 350
    nside = 256
    beam = 63
    bl = hp.gauss_beam(fwhm=np.deg2rad(beam)/60, lmax=lmax)
    cl_cmb = np.load('../../src/cmbsim/cmbdata/cmbcl.npy')[:lmax+1,0]
    cl_cmb = cl_cmb * bl**2

    chi2dof_list = []
    norm_beam_list = []
    norm_error_list = []
    fit_lon_list = []
    fit_lat_list = []
    num_ps_list = []

    for flux_idx in range(0,139):
        print(f'{flux_idx=}')
        lon = np.rad2deg(df_mask.at[flux_idx, 'lon'])
        lat = np.rad2deg(df_mask.at[flux_idx, 'lat'])
        iflux = df_mask.at[flux_idx, 'iflux']

        obj = FitPointSource(m=m, nstd=nstd, flux_idx=flux_idx, df_mask=df_mask, df_ps=df_ps, cl_cmb=cl_cmb, lon=lon, lat=lat, iflux=iflux, lmax=lmax, nside=nside, radius_factor=1.0, beam=beam)

        obj.calc_C_theta(save_path='./cov_256')


if __name__ == '__main__':
    # main()
    calc_cov()



