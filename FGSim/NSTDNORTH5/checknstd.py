import numpy as np
import matplotlib.pyplot as plt
import healpy as hp

nstd = np.load('./145.npy')
print(f'{nstd.shape}')
hp.mollview(nstd[0]);plt.show()
