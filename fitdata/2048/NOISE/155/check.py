import numpy as np
import healpy as hp
import matplotlib.pyplot as plt

m = np.load('./0.npy')

nstd = np.load('../../../../FGSim/NSTDNORTH/2048/155.npy')
hp.mollview(nstd[0])
plt.show()

std = np.std(m[0])
std1 = np.std(m[1])
print(f'{std=}')
print(f'{std1=}')


