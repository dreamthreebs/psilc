import numpy as np
import matplotlib.pyplot as plt
import healpy as hp

lmax = 300
n_freq = 8
cl_type = 'B'
sim = np.load(f'../smooth/FULL_PATCH/noPS_northNOI/SIM/B/data.npy')
fg = np.load(f'../smooth/FULL_PATCH/noPS_northNOI/FG/B/data.npy')
noise = np.load(f'../smooth/FULL_PATCH/noPS_northNOI/NOISE/B/data.npy')
bl = np.load('../smooth/BL/bl_std_curl.npy')


print(f'sim.shape = {sim.shape}')

def pixel_ilc(sim):
    C = np.zeros((n_freq, n_freq))
    C = np.cov(sim)
    A = np.zeros((n_freq+1, n_freq+1))
    A[0:-1,0:-1] = 2 * C
    A[-1,0:n_freq] = 1
    A[0:n_freq,-1] = -1
    print(f'{A = }')
    b = np.zeros(n_freq+1)
    b[-1] = 1
    print(f'{b = }')
    x = np.linalg.solve(A, b)

    weight = x[0:n_freq]
    print(f'{weight = }')

    ilc = weight @ sim
    return weight, ilc

weight, ilc_res = pixel_ilc(sim)
fgres = weight @ fg
noiseres = weight @ noise
ilc_cl = hp.anafast(ilc_res, lmax=lmax)
fgres_cl = hp.anafast(fgres, lmax=lmax)
noise_cl = hp.anafast(noiseres, lmax=lmax)

# np.save('./PILCRESULT/w2.npy',weight)
# np.save('./PILCRESULT/pilc_cl2.npy',ilc_cl)
# np.save('./PILCRESULT/pilc_fgres_cl2.npy',fgres_cl)
# np.save('./PILCRESULT/pilc_noise_cl2.npy',noise_cl)

# n_sim = 50
# noise_cl_sum = 0
# for i in range(n_sim):
#     print(f'loop:{i}')
#     noise = np.load(f'../smooth/FULL_PATCH/noPS_northNOI/NOISESIM/{i}/{cl_type}/data.npy')
#     noiseres = weight @ noise
#     noise_res_cl = hp.anafast(noiseres, lmax=lmax)
#     noise_cl_sum = noise_cl_sum + noise_res_cl

# noise_res_avg = noise_cl_sum / n_sim
# np.save('./PILCRESULT/pilc_noise_avg2',noise_res_avg)



