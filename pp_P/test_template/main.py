import healpy as hp
import numpy as np
import matplotlib.pyplot as plt

nside = 512
npix  = hp.nside2npix(nside)
m = np.zeros((3, npix))
lon = 1
colat = 1
idx = hp.ang2pix(nside, np.deg2rad(colat), np.deg2rad(lon))

m[:, idx] = np.random.uniform(-10, 10, 3)
print(f'{m[:,idx]=}')

# smoothing by healpy

healpy_m = hp.smoothing(m, np.deg2rad(1))
hp.gnomview(healpy_m[1], rot=(lon, 90-colat), sub=121)
hp.gnomview(healpy_m[2], rot=(lon, 90-colat), sub=122)

# smoothing by lugwid

P = m[1, idx] + 1j * m[2, idx]
_, iphi = hp.pix2ang(nside, idx)
P = P * np.exp(2j * iphi)

ivec = np.array(hp.pix2vec(nside, idx))
vec = np.vstack(hp.pix2vec(nside, np.arange(npix)))

cost = ivec @ vec
half_t2 = 1 - cost
print(f'{half_t2.shape=}')
sigma = np.deg2rad(1) / np.sqrt(8*np.log(2))
profile = np.exp(-half_t2 / sigma**2)
print(f'{profile.shape=}')

inv_norm_factor = np.sum(profile)
# inv_norm_factor = 1 / (2*np.pi*sigma**2)
print(f'{inv_norm_factor=}')
profile /= inv_norm_factor

lugwidP = P * profile
_, phi = hp.pix2ang(nside, np.arange(npix))
QU = lugwidP * np.exp(-2j * phi)
Q = QU.real
U = QU.imag
print(f'{np.sum(Q)=}')
print(f'{np.sum(U)=}')

fig = plt.figure()
hp.gnomview(Q, rot=(lon, 90-colat), sub=121, fig=fig)
hp.gnomview(U, rot=(lon, 90-colat), sub=122, fig=fig)
plt.show()



