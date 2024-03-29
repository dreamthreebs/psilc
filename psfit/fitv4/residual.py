import numpy as np
import healpy as hp
import matplotlib.pyplot as plt
import os,sys
import pandas as pd

import ipdb
from pathlib import Path

class GetResidual:
    def __init__(self, flux_idx, m_has_ps, m_no_ps, lon, lat, df_mask, nside, beam, radius_factor):
        self.flux_idx = flux_idx
        self.m_has_ps = m_has_ps
        self.m_no_ps = m_no_ps

        self.lon = lon
        self.lat = lat
        self.nside = nside
        self.beam = beam
        self.sigma = np.deg2rad(beam) / 60 / (np.sqrt(8 * np.log(2)))
        self.df_mask = df_mask
        self.radius_factor = radius_factor
        iflux = df_mask.at[flux_idx, 'iflux']
        self.true_beam = self.flux2norm_beam(iflux)

        ctr0_pix = hp.ang2pix(nside=self.nside, theta=self.lon, phi=self.lat, lonlat=True)
        ctr0_vec = np.array(hp.pix2vec(nside=self.nside, ipix=ctr0_pix)).astype(np.float64)

        self.ipix_fit = hp.query_disc(nside=self.nside, vec=ctr0_vec, radius=self.radius_factor * np.deg2rad(self.beam) / 60)
        self.vec_around = np.array(hp.pix2vec(nside=self.nside, ipix=self.ipix_fit.astype(int))).astype(np.float64)
        # print(f'{ipix_fit.shape=}')
        self.ndof = len(self.ipix_fit)

    def beam_model(self, norm_beam, theta):
        return norm_beam / (2 * np.pi * self.sigma**2) * np.exp(- (theta)**2 / (2 * self.sigma**2))

    def flux2norm_beam(self, flux):
        # from mJy to muK_CMB to norm_beam
        coeffmJy2norm = 2.1198465131100624e-05
        return coeffmJy2norm * flux

    def psnoise(self, mask):

        # num_ps = np.load(f'./fit_res/2048/PSNOISE/1.5/idx_{self.flux_idx}/num_ps.npy')[0].copy()
        # pcn_norm_beam = np.load(f'./fit_res/2048/PSNOISE/1.5/idx_{self.flux_idx}/norm_beam.npy')
        # pcn_fit_lon = np.load(f'./fit_res/2048/PSNOISE/1.5/idx_{self.flux_idx}/fit_lon.npy')
        # pcn_fit_lat = np.load(f'./fit_res/2048/PSNOISE/1.5/idx_{self.flux_idx}/fit_lat.npy')
        # pcn_fit_error = np.load(f'./fit_res/2048/PSNOISE/1.5/idx_{self.flux_idx}/fit_error.npy')
        # print(f'{num_ps=}')
        # print(f'{pcn_norm_beam=}')
        # print(f'{pcn_fit_lon=}')
        # print(f'{pcn_fit_lat=}')
        # print(f'{pcn_fit_error=}')

        # pcn_vec = np.asarray(hp.ang2vec(theta=pcn_fit_lon, phi=pcn_fit_lat, lonlat=True))
        # cos_theta = pcn_vec @ self.vec_around
        # print(f'{cos_theta.shape=}')
        # theta = np.arccos(cos_theta) # (n_rlz, n_pix_for_fit)
        # print(f'{pcn_norm_beam[0]=}, {self.true_beam=}')

        for idx_rlz in range(100):
            print(f'{idx_rlz=}')

            m_ps_noise = np.load(f'../../fitdata/synthesis_data/2048/PSNOISE/40/{idx_rlz}.npy')[0].copy()
            m_no_ps = np.load(f'../../fitdata/2048/NOISE/40/{idx_rlz}.npy')[0].copy()
            de_ps_map = m_ps_noise.copy()

            for flux_idx in range(136):

                print(f'{flux_idx=}')
                pcn_norm_beam = np.load(f'./fit_res/2048/PSNOISE/1.5/idx_{flux_idx}/norm_beam.npy')

                pcn_fit_lon = np.load(f'./fit_res/2048/PSNOISE/1.5/idx_{flux_idx}/fit_lon.npy')[idx_rlz]
                pcn_fit_lat = np.load(f'./fit_res/2048/PSNOISE/1.5/idx_{flux_idx}/fit_lat.npy')[idx_rlz]

                # pcn_fit_lon = np.rad2deg(self.df_mask.at[flux_idx, 'lon'])
                # pcn_fit_lat = np.rad2deg(self.df_mask.at[flux_idx, 'lat'])

                num_ps = np.load(f'./fit_res/2048/PSNOISE/1.5/idx_{flux_idx}/num_ps.npy')[0].copy()
                print(f'{pcn_fit_lon=}, {pcn_fit_lat=}')

                ctr0_pix = hp.ang2pix(nside=self.nside, theta=pcn_fit_lon, phi=pcn_fit_lat, lonlat=True)
                ctr0_vec = np.array(hp.pix2vec(nside=self.nside, ipix=ctr0_pix)).astype(np.float64)

                ipix_fit = hp.query_disc(nside=self.nside, vec=ctr0_vec, radius=self.radius_factor * np.deg2rad(self.beam) / 60)
                vec_around = np.array(hp.pix2vec(nside=self.nside, ipix=ipix_fit.astype(int))).astype(np.float64)

                pcn_vec = np.asarray(hp.ang2vec(theta=pcn_fit_lon, phi=pcn_fit_lat, lonlat=True))
                cos_theta = pcn_vec @ vec_around
                cos_theta = np.clip(cos_theta, -1, 1)
                theta = np.arccos(cos_theta) # (n_rlz, n_pix_for_fit)

                fit_map = self.beam_model(pcn_norm_beam[idx_rlz], theta)
                print(f'{fit_map.shape=}')

                de_ps_map[ipix_fit] = de_ps_map[ipix_fit].copy() - fit_map

            res_map = np.copy(de_ps_map)
            res_map = res_map - m_no_ps

            # hp.gnomview(m_ps_noise, rot=[self.lon, self.lat, 0], xsize=300, ysize=300, title='ps_cmb_noise map')
            # hp.gnomview(de_ps_map, rot=[self.lon, self.lat, 0], xsize=300, ysize=300, title='de_ps')
            # hp.gnomview(res_map, rot=[self.lon, self.lat, 0], xsize=60, ysize=60, title='residual map:de_ps - cmb noise map')
            # plt.show()

            # hp.orthview(m_ps_noise*mask, rot=[100,50,0], half_sky=True, title='ps_noise map', norm='hist')
            # hp.orthview(de_ps_map*mask, rot=[100,50,0], half_sky=True, title='de_ps map', norm='hist')
            # hp.orthview(np.abs(res_map*mask), rot=[100,50,0], half_sky=True, title='residual map:de_ps - noise map', min=0, max=1)
            # plt.show()

            path_for_res_map = Path('./fit_res/2048/ps_noise_residual')
            path_for_res_map.mkdir(parents=True, exist_ok=True)
            np.save(path_for_res_map / Path(f'{idx_rlz}.npy'), res_map)



    def _ps_fg_cmbnoise(self):
        num_ps = np.load(f'./fit_res/2048/PSCMBNOISE/1.5/idx_{self.flux_idx}/num_ps.npy')[0].copy()
        pcn_norm_beam = np.load(f'./fit_res/2048/PSCMBNOISE/1.5/idx_{self.flux_idx}/norm_beam.npy')
        pcn_fit_lon = np.load(f'./fit_res/2048/PSCMBNOISE/1.5/idx_{self.flux_idx}/fit_lon.npy')
        pcn_fit_lat = np.load(f'./fit_res/2048/PSCMBNOISE/1.5/idx_{self.flux_idx}/fit_lat.npy')
        print(f'{num_ps=}')
        print(f'{pcn_norm_beam=}')
        print(f'{pcn_fit_lon=}')
        print(f'{pcn_fit_lat=}')


    def ps_cmbnoise(self, mask):
        for idx_rlz in range(100):
            print(f'{idx_rlz=}')

            m_ps_cmb_noise = np.load(f'../../fitdata/synthesis_data/2048/PSCMBNOISE/40/{idx_rlz}.npy')[0].copy()
            m_no_ps = np.load(f'../../fitdata/synthesis_data/2048/CMBNOISE/40/{idx_rlz}.npy')[0].copy()
            de_ps_map = m_ps_cmb_noise.copy()
            mask_list = []

            for flux_idx in range(136):

                print(f'{flux_idx=}')
                pcn_norm_beam = np.load(f'./fit_res/2048/PSCMBNOISE/1.5/idx_{flux_idx}/norm_beam.npy')
                pcn_norm_error = np.load(f'./fit_res/2048/PSCMBNOISE/1.5/idx_{flux_idx}/norm_error.npy')
                print(f'{pcn_norm_beam[idx_rlz]=}, {pcn_norm_error[idx_rlz]=}')

                if pcn_norm_beam[idx_rlz] < 2 * pcn_norm_error[idx_rlz]:
                    print(f'smaller than threshold, break')
                    continue
                mask_list.append(flux_idx)

                pcn_fit_lon = np.load(f'./fit_res/2048/PSCMBNOISE/1.5/idx_{flux_idx}/fit_lon.npy')[idx_rlz]
                pcn_fit_lat = np.load(f'./fit_res/2048/PSCMBNOISE/1.5/idx_{flux_idx}/fit_lat.npy')[idx_rlz]

                # pcn_fit_lon = np.rad2deg(self.df_mask.at[flux_idx, 'lon'])
                # pcn_fit_lat = np.rad2deg(self.df_mask.at[flux_idx, 'lat'])

                num_ps = np.load(f'./fit_res/2048/PSCMBNOISE/1.5/idx_{flux_idx}/num_ps.npy')[0].copy()
                print(f'{pcn_fit_lon=}, {pcn_fit_lat=}')

                ctr0_pix = hp.ang2pix(nside=self.nside, theta=pcn_fit_lon, phi=pcn_fit_lat, lonlat=True)
                ctr0_vec = np.array(hp.pix2vec(nside=self.nside, ipix=ctr0_pix)).astype(np.float64)

                ipix_fit = hp.query_disc(nside=self.nside, vec=ctr0_vec, radius=self.radius_factor * np.deg2rad(self.beam) / 60)
                vec_around = np.array(hp.pix2vec(nside=self.nside, ipix=ipix_fit.astype(int))).astype(np.float64)

                pcn_vec = np.asarray(hp.ang2vec(theta=pcn_fit_lon, phi=pcn_fit_lat, lonlat=True))
                cos_theta = pcn_vec @ vec_around
                cos_theta = np.clip(cos_theta, -1, 1)
                theta = np.arccos(cos_theta) # (n_rlz, n_pix_for_fit)

                fit_map = self.beam_model(pcn_norm_beam[idx_rlz], theta)
                print(f'{fit_map.shape=}')

                de_ps_map[ipix_fit] = de_ps_map[ipix_fit].copy() - fit_map

            res_map = np.copy(de_ps_map)
            res_map = res_map - m_no_ps

            # hp.orthview(m_ps_cmb_noise*mask, rot=[100,50,0], half_sky=True, title='ps_cmb_noise map')
            # hp.orthview(de_ps_map*mask, rot=[100,50,0], half_sky=True, title='de_ps map')
            # hp.orthview(res_map*mask, rot=[100,50,0], half_sky=True, title='residual map:de_ps - cmb noise map', min=-10, max=10)
            # plt.show()

            path_for_res_map = Path('./fit_res/2048/ps_cmb_noise_residual/2sigma')
            path_for_res_map.mkdir(parents=True, exist_ok=True)
            np.save(path_for_res_map / Path(f'map{idx_rlz}.npy'), res_map)
            np.save(path_for_res_map / Path(f'mask{idx_rlz}.npy'), np.array(mask_list))


    def ps_fg_cmbnoise(self, mask):
        for idx_rlz in range(100):
            print(f'{idx_rlz=}')

            m_ps_cmb_fg_noise = np.load(f'../../fitdata/synthesis_data/2048/PSCMBFGNOISE/40/{idx_rlz}.npy')[0].copy()
            m_no_ps = np.load(f'../../fitdata/synthesis_data/2048/CMBFGNOISE/40/{idx_rlz}.npy')[0].copy()
            de_ps_map = m_ps_cmb_fg_noise.copy()
            mask_list = []

            for flux_idx in range(136):

                print(f'{flux_idx=}')
                pcn_norm_beam = np.load(f'./fit_res/2048/PSCMBFGNOISE/1.5/idx_{flux_idx}/norm_beam.npy')
                pcn_norm_error = np.load(f'./fit_res/2048/PSCMBFGNOISE/1.5/idx_{flux_idx}/norm_error.npy')
                print(f'{pcn_norm_beam[idx_rlz]=}, {pcn_norm_error[idx_rlz]=}')

                if pcn_norm_beam[idx_rlz] < 2 * pcn_norm_error[idx_rlz]:
                    print(f'smaller than threshold, break')
                    continue
                mask_list.append(flux_idx)



                pcn_fit_lon = np.load(f'./fit_res/2048/PSCMBFGNOISE/1.5/idx_{flux_idx}/fit_lon.npy')[idx_rlz]
                pcn_fit_lat = np.load(f'./fit_res/2048/PSCMBFGNOISE/1.5/idx_{flux_idx}/fit_lat.npy')[idx_rlz]

                # pcn_fit_lon = np.rad2deg(self.df_mask.at[flux_idx, 'lon'])
                # pcn_fit_lat = np.rad2deg(self.df_mask.at[flux_idx, 'lat'])

                num_ps = np.load(f'./fit_res/2048/PSCMBFGNOISE/1.5/idx_{flux_idx}/num_ps.npy')[0].copy()
                print(f'{pcn_fit_lon=}, {pcn_fit_lat=}')

                ctr0_pix = hp.ang2pix(nside=self.nside, theta=pcn_fit_lon, phi=pcn_fit_lat, lonlat=True)
                ctr0_vec = np.array(hp.pix2vec(nside=self.nside, ipix=ctr0_pix)).astype(np.float64)

                ipix_fit = hp.query_disc(nside=self.nside, vec=ctr0_vec, radius=self.radius_factor * np.deg2rad(self.beam) / 60)
                vec_around = np.array(hp.pix2vec(nside=self.nside, ipix=ipix_fit.astype(int))).astype(np.float64)

                pcn_vec = np.asarray(hp.ang2vec(theta=pcn_fit_lon, phi=pcn_fit_lat, lonlat=True))
                cos_theta = pcn_vec @ vec_around
                cos_theta = np.clip(cos_theta, -1, 1)
                print(f"{cos_theta=}")
                theta = np.arccos(cos_theta) # (n_rlz, n_pix_for_fit)

                fit_map = self.beam_model(pcn_norm_beam[idx_rlz], theta)
                print(f'{fit_map.shape=}')

                de_ps_map[ipix_fit] = de_ps_map[ipix_fit].copy() - fit_map

            res_map = np.copy(de_ps_map)
            res_map = res_map - m_no_ps


            # hp.orthview(m_ps_cmb_fg_noise*mask, rot=[100,50,0], half_sky=True, title='ps_cmb_noise map')
            # hp.orthview(de_ps_map*mask, rot=[100,50,0], half_sky=True, title='de_ps map')
            # hp.orthview(res_map*mask, rot=[100,50,0], half_sky=True, title='residual map:de_ps - cmb noise map', min=-20, max=20)
            # plt.show()

            path_for_res_map = Path('./fit_res/2048/ps_cmb_fg_noise_residual/2sigma')
            path_for_res_map.mkdir(parents=True, exist_ok=True)
            np.save(path_for_res_map / Path(f'map{idx_rlz}.npy'), res_map)
            np.save(path_for_res_map / Path(f'mask{idx_rlz}.npy'), np.array(mask_list))



def main():
    # m = np.load('../../fitdata/synthesis_data/2048/PSNOISE/40/1.npy')[0]
    m_has_ps = np.load('../../fitdata/synthesis_data/2048/PSNOISE/40/1.npy')[0]
    # m_no_ps = np.load('../../fitdata/2048/NOISE/40/1.npy')[0]
    m_no_ps = None
    mask = np.load('../../src/mask/north/BINMASKG2048.npy')
    nstd = np.load('../../FGSim/NSTDNORTH/2048/40.npy')[0]
    df_mask = pd.read_csv('../partial_sky_ps/ps_in_mask/2048/40mask.csv')
    df_ps = pd.read_csv('../partial_sky_ps/ps_in_mask/2048/40ps.csv')
    lmax = 350
    nside = 2048
    beam = 63

    flux_idx = 1
    lon = np.rad2deg(df_mask.at[flux_idx, 'lon'])
    lat = np.rad2deg(df_mask.at[flux_idx, 'lat'])

    obj = GetResidual(flux_idx=flux_idx, m_has_ps=m_has_ps, m_no_ps=m_no_ps, lon=lon, lat=lat, df_mask=df_mask, nside=nside, beam=beam, radius_factor=1.5)

    # obj.see_true_map(m=m, lon=lon, lat=lat, nside=nside, beam=beam)
    # obj.psnoise(mask=mask)
    # obj.ps_cmbnoise(mask=mask)
    obj.ps_fg_cmbnoise(mask=mask)

main()


