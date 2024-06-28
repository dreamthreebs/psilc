import numpy as np
import healpy as hp
import matplotlib.pyplot as plt

from iminuit import Minuit
from pathlib import Path

class Fit_on_B:
    def __init__(self, m, lmax, nside, beam, lon, lat, r_fold=3, r_fold_rmv=5):
        self.m = m
        self.lmax = lmax
        self.nside = nside
        self.beam = beam
        self.lon = lon
        self.lat = lat
        self.r_fold = r_fold
        self.r_fold_rmv = r_fold_rmv

        self.npix = hp.nside2npix(nside)
        self.sigma = np.deg2rad(beam) / 60 / (np.sqrt(8 * np.log(2)))

        ipix_ctr = hp.ang2pix(theta=lon, phi=lat, lonlat=True, nside=nside)
        self.pix_lon, self.pix_lat = hp.pix2ang(ipix=ipix_ctr, nside=nside, lonlat=True)
        self.ctr_vec = np.array(hp.pix2vec(nside=nside, ipix=ipix_ctr))

        ctr_theta, ctr_phi = hp.pix2ang(nside=nside, ipix=ipix_ctr) # center pixel theta phi in sphere coordinate
        self.vec_theta = np.asarray((np.cos(ctr_theta)*np.cos(ctr_phi), np.cos(ctr_theta)*np.sin(ctr_phi), -np.sin(ctr_theta)))
        self.vec_phi = np.asarray((-np.sin(ctr_phi), np.cos(ctr_phi), 0))

    # Set up parameters
    def params_for_fitting(self):
        self.ipix_disc = hp.query_disc(nside=self.nside, vec=self.ctr_vec, radius=self.r_fold * np.deg2rad(beam) / 60 ) # disc for fitting
        np.save('./data/pix_idx.npy', self.ipix_disc)
        self.ndof = np.size(self.ipix_disc) # degree of freedom
        print(f'{self.ipix_disc.shape=}, {self.ndof=}')

        vec_disc = np.array(hp.pix2vec(nside=self.nside, ipix=self.ipix_disc.astype(int))).astype(np.float64)
        vec_ctr_to_disc = vec_disc.T - self.ctr_vec # vector from center to fitting point

        r = np.linalg.norm(vec_ctr_to_disc, axis=1) # radius in polar coordinate
        # np.set_printoptions(threshold=np.inf)
        # print(f'{r=}')

        normed_vec_ctr_to_disc = vec_ctr_to_disc.T / r # normed vector from center to fitting point for calculating xi
        normed_vec_ctr_to_disc = np.nan_to_num(normed_vec_ctr_to_disc, nan=0)
        print(f'{normed_vec_ctr_to_disc=}')

        cos_theta = normed_vec_ctr_to_disc.T @ self.vec_theta
        cos_phi = normed_vec_ctr_to_disc.T @ self.vec_phi

        xi = np.arctan2(cos_phi, cos_theta) # xi in polar coordinate
        self.cos_2xi = np.cos(2*xi)
        self.sin_2xi = np.sin(2*xi)
        print(f'{xi=}')

        self.r_2 = r**2
        self.r_2_div_sigma = self.r_2 / (2 * self.sigma**2)

    def params_for_testing(self):
        self.ipix_disc = hp.query_disc(nside=self.nside, vec=self.ctr_vec, radius=self.r_fold_rmv * np.deg2rad(beam) / 60 ) # disc for fitting
        self.ndof = np.size(self.ipix_disc) # degree of freedom
        print(f'{self.ipix_disc.shape=}, {self.ndof=}')

        vec_disc = np.array(hp.pix2vec(nside=self.nside, ipix=self.ipix_disc.astype(int))).astype(np.float64)
        vec_ctr_to_disc = vec_disc.T - self.ctr_vec # vector from center to fitting point

        r = np.linalg.norm(vec_ctr_to_disc, axis=1) # radius in polar coordinate
        # np.set_printoptions(threshold=np.inf)
        # print(f'{r=}')

        normed_vec_ctr_to_disc = vec_ctr_to_disc.T / r # normed vector from center to fitting point for calculating xi
        normed_vec_ctr_to_disc = np.nan_to_num(normed_vec_ctr_to_disc, nan=0)
        print(f'{normed_vec_ctr_to_disc=}')

        cos_theta = normed_vec_ctr_to_disc.T @ self.vec_theta
        cos_phi = normed_vec_ctr_to_disc.T @ self.vec_phi

        xi = np.arctan2(cos_phi, cos_theta) # xi in polar coordinate
        self.cos_2xi = np.cos(2*xi)
        self.sin_2xi = np.sin(2*xi)
        print(f'{xi=}')

        self.r_2 = r**2
        self.r_2_div_sigma = self.r_2 / (2 * self.sigma**2)

    # Calculate inverse covariance matrix
    def calc_inv_cov(self, mode='n'):

        if mode == 'cn':
            cov = np.load('./cmb_b_cov/0.npy') # load cmb cov
            print(f'{cov.shape=}')
            # nstd = 0.85661
            # nstd = 0.1

        if mode == 'n':
            cov = np.zeros((self.ndof, self.ndof))

        nstd = 0.1
        # nstd = 0.0856540128628882
        nstd2 = nstd**2

        for i in range(self.ndof):
            cov[i,i] = cov[i,i] + nstd2

        self.inv_cov = np.linalg.inv(cov)

    # Code for fitting
    def model(self, A, ps_2phi):
        model = - A / (np.pi) * (self.sin_2xi * np.cos(ps_2phi) - self.cos_2xi * np.sin(ps_2phi)) * (1 / self.r_2) * (np.exp(-self.r_2_div_sigma) * (1+self.r_2_div_sigma) - 1)
        model = np.nan_to_num(model, nan=0)
        return model

    def lsq(self, A, ps_2phi, const):
        y_model = self.model(A, ps_2phi) + const
        y_data = self.m[self.ipix_disc]
        y_diff = y_data - y_model

        z = y_diff @ self.inv_cov @ y_diff
        return z

    def fit_b(self):
        params = (0.0, 0.0, 0.0)
        obj_minuit = Minuit(self.lsq, name=("A", "ps_2phi", "const"), *params)
        obj_minuit.limits = [(None,None), (-np.pi,np.pi), (-100,100)]
        print(obj_minuit.migrad())
        print(obj_minuit.hesse())
        chi2dof = obj_minuit.fval / self.ndof
        str_chi2 = f"𝜒²/ndof = {obj_minuit.fval:.2f} / {self.ndof} = {chi2dof}"
        print(str_chi2)
        self.A = obj_minuit.values["A"]
        P = self.A / hp.nside2pixarea(nside=self.nside)
        print(f'{P=}')
        self.ps_2phi = obj_minuit.values["ps_2phi"]
        print(f'Q = {P*np.cos(self.ps_2phi)}')
        print(f'U = {P*np.sin(self.ps_2phi)}')


    # tests
    def test_residual(self):

        m_model = np.zeros(self.npix)
        m_model[self.ipix_disc] = self.model(self.A, self.ps_2phi)

        res = self.m - m_model
        res = res - np.load('./m_cn_b_1.npy')

        hp.gnomview(m_model, rot=[self.pix_lon, self.pix_lat, 0], title='model')
        hp.gnomview(self.m, rot=[self.pix_lon, self.pix_lat, 0], title='input')
        hp.gnomview(res, rot=[self.pix_lon, self.pix_lat, 0], title='res', min=-3.5, max=3.5)

        plt.show()




if __name__=='__main__':
    lmax = 1999
    nside = 2048
    beam = 11
    lon = 0
    lat = 0
    # m = np.load('./data/qu_pn.npy').copy()
    m = np.load('./data/m_pn_b.npy').copy()
    # m = np.load('./m_pcn_b_1.npy').copy()
    # m = np.load('./m_qu_pcn.npy').copy()
    # m = np.load('./m_qu_cn.npy').copy()

    obj = Fit_on_B(m, lmax, nside, beam, lon, lat, r_fold=2, r_fold_rmv=5)
    obj.params_for_fitting()
    obj.calc_inv_cov(mode='n')
    obj.fit_b()
    obj.params_for_testing()
    obj.test_residual()

