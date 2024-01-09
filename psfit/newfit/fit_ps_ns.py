import numpy as np
import healpy as hp
import matplotlib.pyplot as plt
import pandas as pd
import time
import pickle

from iminuit import Minuit
from iminuit.cost import LeastSquares
from numpy.polynomial.legendre import Legendre
from scipy.interpolate import CubicSpline

class FitPointSource:
    def __init__(self, m, nstd, flux_idx, df_mask, df_ps, cl_cmb, lon, lat, iflux, lmax, nside, radius_factor, beam, sigma_threshold=5):
        self.m = m # sky maps (npix,)
        self.input_lon = lon # input longitude in degrees
        self.input_lat = lat # input latitude in degrees
        ipix = hp.ang2pix(nside=nside, theta=lon, phi=lat, lonlat=True)
        lon, lat = hp.pix2ang(nside=nside, ipix=ipix, lonlat=True)
        self.lon = lon
        self.lat = lat
        print(f'{lon=}')
        print(f'{lat=}')
        self.iflux = iflux # temperature flux in muK_CMB
        self.df_mask = df_mask # pandas data frame of point sources in mask
        self.flux_idx = flux_idx # index in df_mask
        self.df_ps = df_ps # pandas data frame of all point sources
        self.nstd = nstd # noise standard deviation
        self.cl_cmb = cl_cmb # power spectrum of CMB
        self.lmax = lmax # maximum multipole
        self.nside = nside # resolution of healpy maps
        self.radius_factor = radius_factor # disc radius of fitting region
        self.sigma_threshold = sigma_threshold # judge if a signal is a point source
        self.beam = beam # arcmin

        self.ini_norm_beam = self.flux2norm_beam(self.iflux)

        self.n_pts = 0 # count number for counting
        self.n_call = 0.0 # count number of function calls

        self.sigma = np.deg2rad(beam) / 60 / (np.sqrt(8 * np.log(2)))

    def flux2norm_beam(self, flux):
        # from mJy to muK_CMB to norm_beam
        coeffmJy2norm = 2.1198465131100624e-05
        return coeffmJy2norm * flux

    def input_lonlat2pix_lonlat(self, input_lon, input_lat):
        ipix = hp.ang2pix(nside=self.nside, theta=input_lon, phi=input_lat, lonlat=True)
        out_lon, out_lat = hp.pix2ang(nside=self.nside, ipix=ipix, lonlat=True)
        return out_lon, out_lat

    def see_true_map(self, m, lon, lat, nside, beam):
        radiops = hp.read_map('/sharefs/alicpt/users/zrzhang/allFreqPSMOutput/skyinbands/AliCPT_uKCMB/40GHz/strongradiops_map_40GHz.fits', field=0)
        irps = hp.read_map('/sharefs/alicpt/users/zrzhang/allFreqPSMOutput/skyinbands/AliCPT_uKCMB/40GHz/strongirps_map_40GHz.fits', field=0)

        hp.gnomview(irps, rot=[lon, lat, 0], xsize=300, ysize=300, reso=1, title='irps')
        hp.gnomview(radiops, rot=[lon, lat, 0], xsize=300, ysize=300, reso=1, title='radiops')
        hp.gnomview(m, rot=[lon, lat, 0], xsize=300, ysize=300)
        plt.show()

        vec = hp.ang2vec(theta=lon, phi=lat, lonlat=True)
        ipix_disc = hp.query_disc(nside=nside, vec=vec, radius=np.deg2rad(beam)/60)

        mask = np.ones(hp.nside2npix(nside))
        mask[ipix_disc] = 0

        hp.gnomview(mask, rot=[lon, lat, 0])
        plt.show()

    def find_nearby_ps(self, num_ps=1, threshold_factor=2.2):
        dir_0 = (self.lon, self.lat)
        arr_1 = self.df_ps.loc[:, 'Unnamed: 0']
        print(f'{arr_1.shape=}')
        bool_arr = self.df_ps.loc[:, 'Unnamed: 0'] != self.df_mask.at[self.flux_idx, 'Unnamed: 0']
        print(f'{bool_arr.shape=}')
        lon_other = np.rad2deg(self.df_ps.loc[bool_arr, 'lon'])
        lat_other = np.rad2deg(self.df_ps.loc[bool_arr, 'lat'])
        dir_other = (lon_other, lat_other)
        ang = np.rad2deg(hp.rotator.angdist(dir1=dir_0, dir2=dir_other, lonlat=True))
        print(f'{ang.shape=}')
        threshold = threshold_factor * self.beam / 60
        print(f'{ang=}')
    
        index_near = np.nonzero(np.where((ang < threshold), ang, 0))
        ang_near = ang[index_near]
        print(f'{index_near=}')
        print(f'{ang_near=}')

        # if index_near[0].size == 0:
        #     raise ValueError('This is a single point source, please check! 4 parameter fit should get good fitting result')
        print(f'number of ir, radio ps = {index_near[0].size}')

        lon_list = []
        lat_list = []
        iflux_list = []
        for i in range(min(num_ps, len(index_near[0]))):
            index = index_near[0][i]
            if index < self.df_mask.at[self.flux_idx, 'Unnamed: 0']:
                lon = np.rad2deg(self.df_ps.at[index, 'lon'])
                lat = np.rad2deg(self.df_ps.at[index, 'lat'])
                iflux = self.flux2norm_beam(self.df_ps.at[index, 'iflux'])
            else:
                lon = np.rad2deg(self.df_ps.at[index + 1, 'lon'])
                lat = np.rad2deg(self.df_ps.at[index + 1, 'lat'])
                iflux = self.flux2norm_beam(self.df_ps.at[index + 1, 'iflux'])
            lon, lat = self.input_lonlat2pix_lonlat(lon, lat)
            lon_list.append(lon)
            lat_list.append(lat)
            iflux_list.append(iflux)

        print(f'{iflux_list=}')
    
        ##Optional visualization code commented out
        #hp.gnomview(self.m, rot=[self.lon,self.lat,0])
        #for lon, lat in zip(lon_list, lat_list):
        #    hp.projscatter(lon, lat, lonlat=True)
        #plt.show()
    
        # return tuple(iflux_list + lon_list + lat_list)
        iflux_arr = np.array(iflux_list)
        num_ps = np.count_nonzero(np.where(iflux_arr > self.flux2norm_beam(flux=100), iflux_arr, 0))
        print(f'there are {num_ps} ps > 100 mJy')

        return num_ps, tuple(sum(zip(iflux_list, lon_list, lat_list), ()))

    def fit_ps_ns(self, mode:str='pipeline'):
        def lsq_2_params(norm_beam, const):

            theta = hp.rotator.angdist(dir1=ctr0_vec, dir2=vec_around)

            def model():
                return norm_beam / (2 * np.pi * self.sigma**2) * np.exp(- (theta)**2 / (2 * self.sigma**2)) + const

            y_model = model()
            y_data = self.m[ipix_fit]
            y_err = self.nstd[ipix_fit]

            z = (y_data - y_model) / y_err
            return np.sum(z**2)

        def lsq_params(*args):
            # args is expected to be in the format:
            # norm_beam1, ctr1_lon_shift, ctr1_lat_shift, ..., norm_beamN, ctrN_lon_shift, ctrN_lat_shift, const
        
            num_ps = (len(args) - 1) // 3  # Determine the number of point sources based on the number of arguments
        
            # Extract const
            const = args[-1]
        
            # Process each point source
            thetas = []
            for i in range(num_ps):
                norm_beam, lon_shift, lat_shift = args[i*3:i*3+3]
                # print(f'{lon_shift=},{lat_shift}')
                lon = self.fit_lon[i] + lon_shift
                lat = self.fit_lat[i] + lat_shift
                # print(f'{lon=},{lat=}')
                ctr_vec = np.array(hp.ang2vec(theta=lon, phi=lat, lonlat=True))
        
                theta = hp.rotator.angdist(dir1=ctr_vec, dir2=vec_around)
                thetas.append(norm_beam / (2 * np.pi * self.sigma**2) * np.exp(- (theta)**2 / (2 * self.sigma**2)))
        
            def model():
                return sum(thetas) + const
        
            y_model = model()
            y_data = self.m[ipix_fit]
            y_err = self.nstd[ipix_fit]
        
            z = (y_data - y_model) / y_err
            return np.sum(z**2)

        ctr0_pix = hp.ang2pix(nside=self.nside, theta=self.lon, phi=self.lat, lonlat=True)
        ctr0_vec = np.array(hp.pix2vec(nside=self.nside, ipix=ctr0_pix)).astype(np.float64)

        ipix_fit = hp.query_disc(nside=self.nside, vec=ctr0_vec, radius=self.radius_factor * np.deg2rad(self.beam) / 60)
        vec_around = np.array(hp.pix2vec(nside=self.nside, ipix=ipix_fit.astype(int))).astype(np.float64)
        # print(f'{ipix_fit.shape=}')
        self.ndof = len(ipix_fit)

        num_ps, near = self.find_nearby_ps(num_ps=10)
        print(f'{num_ps=}, {near=}')

        true_norm_beam = self.flux2norm_beam(self.iflux)


        def fit_2_params():
            obj_minuit = Minuit(lsq_2_params, norm_beam=self.ini_norm_beam, const=0.0)
            obj_minuit.limits = [(0,1),  (-100,100)]
            print(obj_minuit.migrad())
            # for p in obj_minuit.params:
                # print(repr(p))

            chi2dof = obj_minuit.fval / self.ndof
            str_chi2 = f"𝜒²/ndof = {obj_minuit.fval:.2f} / {self.ndof} = {chi2dof}"
            print(str_chi2)

            if obj_minuit.fmin.hesse_failed:
                raise ValueError('hesse failed!')
            else:
                return chi2dof, obj_minuit.values['norm_beam'],obj_minuit.errors['norm_beam'], self.lon, self.lat


        def fit_4_params():
            params = (self.ini_norm_beam, 0.0, 0.0, 0.0)
            self.fit_lon = (self.lon,)
            self.fit_lat = (self.lat,)
            print(f'{self.fit_lon=}')

            obj_minuit = Minuit(lsq_params, name=("norm_beam1","ctr1_lon_shift","ctr1_lat_shift","const"), *params)
            obj_minuit.limits = [(0,1.0), (-0.01, 0.01), (-0.01,0.01), (-100,100)]
            print(obj_minuit.migrad())
            print(obj_minuit.hesse())
            # for p in obj_minuit.params:
                # print(repr(p))

            chi2dof = obj_minuit.fval / self.ndof
            str_chi2 = f"𝜒²/ndof = {obj_minuit.fval:.2f} / {self.ndof} = {chi2dof}"
            print(str_chi2)

            if obj_minuit.fmin.hesse_failed:
                raise ValueError('hesse failed!')

            print(f'4 parameter fitting is enough, hesse ok')
            fit_lon = self.lon + obj_minuit.values['ctr1_lon_shift']
            fit_lat = self.lat + obj_minuit.values['ctr1_lat_shift']
            return chi2dof, obj_minuit.values['norm_beam1'],obj_minuit.errors['norm_beam1'], fit_lon, fit_lat

        def fit_7_params():
            num_ps, (self.ctr2_iflux, self.ctr2_lon, self.ctr2_lat) = self.find_nearby_ps(num_ps=1)

            params = (self.ini_norm_beam, 0.0, 0.0, self.ctr2_iflux, 0, 0,0)
            self.fit_lon = (self.lon, self.ctr2_lon)
            self.fit_lat = (self.lat, self.ctr2_lat)
            obj_minuit = Minuit(lsq_params, name=("norm_beam1","ctr1_lon_shift","ctr1_lat_shift","norm_beam2","ctr2_lon_shift","ctr2_lat_shift","const"), *params)

            obj_minuit.limits = [(0,1), (-0.01,0.01), (-0.01,0.01),(0,1),(-0.01,0.01),(-0.01,0.01), (-100,100)]
            print(obj_minuit.migrad())
            print(obj_minuit.hesse())
            # for p in obj_minuit.params:
                # print(repr(p))

            chi2dof = obj_minuit.fval / self.ndof
            str_chi2 = f"𝜒²/ndof = {obj_minuit.fval:.2f} / {self.ndof} = {chi2dof}"
            print(str_chi2)

            if obj_minuit.fmin.hesse_failed:
                raise ValueError('hesse failed!')

            print(f'7 parameter fitting is enough, hesse ok')
            fit_lon = self.lon + obj_minuit.values['ctr1_lon_shift']
            fit_lat = self.lat + obj_minuit.values['ctr1_lat_shift']

            return chi2dof, obj_minuit.values['norm_beam1'],obj_minuit.errors['norm_beam1'], fit_lon, fit_lat


        def fit_10_params():
            num_ps, (self.ctr2_iflux, self.ctr2_lon, self.ctr2_lat, self.ctr3_iflux, self.ctr3_lon, self.ctr3_lat) = self.find_nearby_ps(num_ps=2)

            params = (self.ini_norm_beam, 0, 0, self.ctr2_iflux, 0, 0, self.ctr3_iflux, 0, 0, 0)
            self.fit_lon = (self.lon, self.ctr2_lon, self.ctr3_lon)
            self.fit_lat = (self.lat, self.ctr2_lat, self.ctr3_lat)
            obj_minuit = Minuit(lsq_params, name=("norm_beam1","ctr1_lon_shift","ctr1_lat_shift","norm_beam2","ctr2_lon_shift","ctr2_lat_shift","norm_beam3","ctr3_lon_shift","ctr3_lat_shift","const"), *params)

            shift_limit = 0.01
            obj_minuit.limits = [(0,1),(-shift_limit,shift_limit),(-shift_limit,shift_limit),(0,1),(-shift_limit,shift_limit),(-shift_limit,shift_limit),(0,1),(-shift_limit,shift_limit),(-shift_limit,shift_limit), (-100,100)]
            # obj_minuit.errors = (1e-3, 0.01, 0.01, 1e-3, 0.01, 0.01, 1e-3, 0.01, 0.01, 0.1)
            print(obj_minuit.migrad())
            print(obj_minuit.hesse())
            # for p in obj_minuit.params:
                # print(repr(p))

            chi2dof = obj_minuit.fval / self.ndof
            str_chi2 = f"𝜒²/ndof = {obj_minuit.fval:.2f} / {self.ndof} = {chi2dof}"
            print(str_chi2)

            if obj_minuit.fmin.hesse_failed:
                raise ValueError('hesse failed!')

            print(f'10 parameter fitting is enough, hesse ok')
            fit_lon = self.lon + obj_minuit.values['ctr1_lon_shift']
            fit_lat = self.lat + obj_minuit.values['ctr1_lat_shift']
            return chi2dof, obj_minuit.values['norm_beam1'],obj_minuit.errors['norm_beam1'], fit_lon, fit_lat

        def fit_13_params():
            num_ps, (self.ctr2_iflux, self.ctr2_lon, self.ctr2_lat, self.ctr3_iflux, self.ctr3_lon, self.ctr3_lat, self.ctr4_iflux, self.ctr4_lon, self.ctr4_lat) = self.find_nearby_ps(num_ps=3)
            params = (self.ini_norm_beam, 0, 0, self.ctr2_iflux, 0, 0, self.ctr3_iflux, 0, 0, self.ctr4_iflux, 0, 0, 0)

            self.fit_lon = (self.lon, self.ctr2_lon, self.ctr3_lon, self.ctr4_lon)
            self.fit_lat = (self.lat, self.ctr2_lat, self.ctr3_lat, self.ctr4_lat)
            obj_minuit = Minuit(lsq_params, name=("norm_beam1","ctr1_lon_shift","ctr1_lat_shift","norm_beam2","ctr2_lon_shift","ctr2_lat_shift","norm_beam3","ctr3_lon_shift","ctr3_lat_shift","norm_beam4","ctr4_lon_shift","ctr4_lat_shift","const"), *params)

            # obj_minuit.limits = [(0,1),(-0.3,0.3),(-0.3,0.3),(0,1),(-0.4,0.4),(-0.4,0.4),(0,1),(-0.5,0.5),(-0.5,0.5), (0,1),(-0.5,0.5),(-0.5,0.5), (-100,100)]

            shift_limit = 0.01
            obj_minuit.limits = [(0,1),(-shift_limit,shift_limit),(-shift_limit,shift_limit),(0,1),(-shift_limit,shift_limit),(-shift_limit,shift_limit),(0,1),(-shift_limit,shift_limit),(-shift_limit,shift_limit), (0,1),(-shift_limit, shift_limit),(-shift_limit, shift_limit), (-100,100)]
            print(obj_minuit.migrad())
            print(obj_minuit.hesse())
            # for p in obj_minuit.params:
                # print(repr(p))

            chi2dof = obj_minuit.fval / self.ndof
            str_chi2 = f"𝜒²/ndof = {obj_minuit.fval:.2f} / {self.ndof} = {chi2dof}"
            print(str_chi2)

            is_ps = obj_minuit.values['norm_beam1'] > self.sigma_threshold * obj_minuit.errors['norm_beam1']

            if obj_minuit.fmin.hesse_failed:
                raise ValueError('hesse failed!')

            print(f'13 parameter fitting is enough, hesse ok')
            fit_lon = self.lon + obj_minuit.values['ctr1_lon_shift']
            fit_lat = self.lat + obj_minuit.values['ctr1_lat_shift']

            return chi2dof, obj_minuit.values['norm_beam1'],obj_minuit.errors['norm_beam1'], fit_lon, fit_lat

        def fit_16_params():
            num_ps, (self.ctr2_iflux, self.ctr2_lon, self.ctr2_lat, self.ctr3_iflux, self.ctr3_lon, self.ctr3_lat, self.ctr4_iflux, self.ctr4_lon, self.ctr4_lat, self.ctr5_iflux, self.ctr5_lon, self.ctr5_lat) = self.find_nearby_ps(num_ps=4)

            params = (self.ini_norm_beam, 0, 0, self.ctr2_iflux, 0, 0, self.ctr3_iflux, 0, 0, self.ctr4_iflux, 0, 0, self.ctr5_iflux,0,0,0)
            self.fit_lon = (self.lon, self.ctr2_lon, self.ctr3_lon, self.ctr4_lon, self.ctr5_lon)
            self.fit_lat = (self.lat, self.ctr2_lat, self.ctr3_lat, self.ctr4_lat, self.ctr5_lat)
            obj_minuit = Minuit(lsq_params, name=("norm_beam1","ctr1_lon_shift","ctr1_lat_shift","norm_beam2","ctr2_lon_shift","ctr2_lat_shift","norm_beam3","ctr3_lon_shift","ctr3_lat_shift","norm_beam4","ctr4_lon_shift","ctr4_lat_shift","norm_beam5","ctr5_lon_shift","ctr5_lat_shift","const"), *params)

            # obj_minuit.limits = [(0,1),(-0.3,0.3),(-0.3,0.3),(0,1),(-0.3,0.3),(-0.3,0.3),(0,1),(-0.5,0.5),(-0.5,0.5), (0,1),(-0.3,0.3),(-0.3,0.3),(0,1),(-0.5,0.5),(-0.5,0.5),(-100,100)]

            shift_limit = 0.01
            obj_minuit.limits = [(0,1),(-shift_limit,shift_limit),(-shift_limit,shift_limit),(0,1),(-shift_limit,shift_limit),(-shift_limit,shift_limit),(0,1),(-shift_limit,shift_limit),(-shift_limit,shift_limit), (0,1),(-shift_limit, shift_limit),(-shift_limit, shift_limit),(0,1),(-shift_limit, shift_limit),(-shift_limit, shift_limit), (-100,100)]
            obj_minuit.migrad()
            obj_minuit.hesse()
            for p in obj_minuit.params:
                print(repr(p))

            chi2dof = obj_minuit.fval / self.ndof
            str_chi2 = f"𝜒²/ndof = {obj_minuit.fval:.2f} / {self.ndof} = {chi2dof}"
            print(str_chi2)

            if obj_minuit.fmin.hesse_failed:
                raise ValueError('hesse failed!')

            print(f'16 parameter fitting is enough, hesse ok')
            fit_lon = self.lon + obj_minuit.values['ctr1_lon_shift']
            fit_lat = self.lon + obj_minuit.values['ctr1_lat_shift']

            return chi2dof, obj_minuit.values['norm_beam1'], obj_minuit.errors['norm_beam1'], fit_lon, fit_lat

        print(f'begin point source fitting, first do 2 parameter fit...')
        chi2dof, fit_norm, norm_error, fit_lon, fit_lat = fit_2_params()
        if fit_norm < self.sigma_threshold * norm_error:
            print('there is no point sources.')

        if mode == 'streamline':
            chi2dof, fit_norm, norm_error, fit_lon, fit_lat = fit_4_params()
            if chi2dof < 1.06:
                return fit_norm, norm_error, fit_lon, fit_lat
            else:
                chi2dof, fit_norm, norm_error, fit_lon, fit_lat = fit_7_params()
                if chi2dof < 1.06:
                    return fit_norm, norm_error, fit_lon, fit_lat
                else:
                    chi2dof, fit_norm, norm_error, fit_lon, fit_lat = fit_10_params()
                    if chi2dof < 1.06:
                        return fit_norm, norm_error, fit_lon, fit_lat
                    else:
                        chi2dof, fit_norm, norm_error, fit_lon, fit_lat = fit_13_params()
                        if chi2dof < 1.06:
                            return fit_norm, norm_error, fit_lon, fit_lat
                        else:
                            print('Cannot fit good!!!')
                            return fit_norm, norm_error, fit_lon, fit_lat

        if mode == 'pipeline':
            if num_ps == 0:
                chi2dof, fit_norm, norm_error, fit_lon, fit_lat = fit_4_params()
            elif num_ps == 1:
                chi2dof, fit_norm, norm_error, fit_lon, fit_lat = fit_7_params()
            elif num_ps == 2:
                chi2dof, fit_norm, norm_error, fit_lon, fit_lat = fit_10_params()
            elif num_ps == 3:
                chi2dof, fit_norm, norm_error, fit_lon, fit_lat = fit_13_params()
            elif num_ps == 4:
                chi2dof, fit_norm, norm_error, fit_lon, fit_lat = fit_16_params()


            fit_error = np.abs(fit_norm - true_norm_beam) / true_norm_beam

            print(f'{chi2dof=}, {fit_norm=}, {norm_error=}, {fit_lon=}, {fit_lat=}')
            print(f'{true_norm_beam=}, {fit_norm=}, {fit_error=}')
            return num_ps, chi2dof, fit_norm, norm_error, fit_lon, fit_lat




if __name__ == '__main__':
    m = np.load('../../FGSim/PSNOISE/2048/40.npy')[0]
    nstd = np.load('../../FGSim/NSTDNORTH/2048/40.npy')[0]
    df_mask = pd.read_csv('../partial_sky_ps/ps_in_mask/mask40.csv')
    flux_idx = 0
    lon = np.rad2deg(df_mask.at[flux_idx, 'lon'])
    lat = np.rad2deg(df_mask.at[flux_idx, 'lat'])
    iflux = df_mask.at[flux_idx, 'iflux']

    df_ps = pd.read_csv('../../test/ps_sort/sort_by_iflux/40.csv')
    
    lmax = 350
    nside = 2048
    beam = 63
    bl = hp.gauss_beam(fwhm=np.deg2rad(beam)/60, lmax=lmax)
    cl_cmb = np.load('../../src/cmbsim/cmbdata/cmbcl.npy')[:lmax+1,0]
    cl_cmb = cl_cmb * bl**2

    obj = FitPointSource(m=m, nstd=nstd, flux_idx=flux_idx, df_mask=df_mask, df_ps=df_ps, cl_cmb=cl_cmb, lon=lon, lat=lat, iflux=iflux, lmax=lmax, nside=nside, radius_factor=1.0, beam=beam)

    # obj.see_true_map(m=m, lon=lon, lat=lat, nside=nside, beam=beam)
    # obj.find_nearby_ps_lon_lat()
    # obj.find_first_second_nearby_ps_lon_lat()
    # obj.fit_ps_ns(mode='10params')
    obj.fit_ps_ns()

