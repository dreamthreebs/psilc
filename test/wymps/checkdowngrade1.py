import numpy as np
import healpy as hp
import matplotlib.pyplot as plt

ipix2048 = hp.ang2pix(nside=2048, theta=0, phi=0, lonlat=True)
m2048 = np.zeros(hp.nside2npix(2048))
m2048[ipix2048] = 1e6


ipix512 = hp.ang2pix(nside=512, theta=0, phi=0, lonlat=True)
m512 = np.zeros(hp.nside2npix(512))
m512[ipix512] = 1e6

sm2048_512 = hp.ud_grade(m2048, nside_out=512)

hp.gnomview(sm2048_512, title='2048 to 512')
hp.gnomview(m512, title='512')
plt.show()

