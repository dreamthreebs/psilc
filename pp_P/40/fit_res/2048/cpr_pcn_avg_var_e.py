import numpy as np
import healpy as hp
import matplotlib.pyplot as plt
import pandas as pd
import pymaster as nmt
import glob

from pathlib import Path

lmax = 400
l = np.arange(lmax+1)
nside = 2048
rlz_idx = 0
threshold = 2

df = pd.read_csv('../../../../FGSim/FreqBand')
freq = df.at[2, 'freq']
beam = df.at[2, 'beam']
print(f'{freq=}, {beam=}')

rmv_list = []
# rmv1_list = []
c_list = []
cn_list = []
pcn_list = []

def generate_bins(l_min_start=30, delta_l_min=30, l_max=1500, fold=0.3):
    bins_edges = []
    l_min = l_min_start  # starting l_min

    while l_min < l_max:
        delta_l = max(delta_l_min, int(fold * l_min))
        l_next = l_min + delta_l
        bins_edges.append(l_min)
        l_min = l_next

    # Adding l_max to ensure the last bin goes up to l_max
    bins_edges.append(l_max)
    return bins_edges[:-1], bins_edges[1:]

l_min_edges, l_max_edges = generate_bins(l_min_start=30, delta_l_min=30, l_max=lmax, fold=0.2)
bin_dl = nmt.NmtBin.from_edges(l_min_edges, l_max_edges, is_Dell=True)
ell_arr = bin_dl.get_effective_ells()

for rlz_idx in range(1,100):
    if rlz_idx == 50:
        continue
    rmv = np.load(f'./pcn_dl/E/removal_2sigma/{rlz_idx}.npy')
    # rmv1 = np.load(f'./pcn_dl/E/removal_10sigma/{rlz_idx}.npy')
    c = np.load(f'./pcn_dl/E/c/{rlz_idx}.npy')
    cn = np.load(f'./pcn_dl/E/cn/{rlz_idx}.npy')
    pcn = np.load(f'./pcn_dl/E/pcn/{rlz_idx}.npy')

    # plt.plot(ell_arr, rmv, label=f'rmv {rlz_idx}')
    # plt.plot(ell_arr, c, label=f'c {rlz_idx}')
    # plt.semilogy()
    # plt.legend()

    rmv_list.append(rmv)
    # rmv1_list.append(rmv1)
    c_list.append(c)
    cn_list.append(cn)
    pcn_list.append(pcn)

# plt.show()

rmv_arr = np.array(rmv_list)
# rmv1_arr = np.array(rmv1_list)
c_arr = np.array(c_list)
cn_arr = np.array(cn_list)
pcn_arr = np.array(pcn_list)
print(f'{rmv_arr.shape=}')

rmv_mean = np.mean(rmv_arr, axis=0)
# rmv1_mean = np.mean(rmv1_arr, axis=0)
c_mean = np.mean(c_arr, axis=0)
cn_mean = np.mean(cn_arr, axis=0)
pcn_mean = np.mean(pcn_arr, axis=0)
print(f'{rmv_mean.shape=}')

rmv_std = np.std(rmv_arr, axis=0)
# rmv1_std = np.std(rmv1_arr, axis=0)
c_std = np.std(c_arr, axis=0)
cn_std = np.std(cn_arr, axis=0)
pcn_std = np.std(pcn_arr, axis=0)
print(f'{rmv_std.shape=}')

n_list = []
path_n = glob.glob('./pcn_dl/E/n/*.npy')
for p in path_n:
    n = np.load(p)
    n_list.append(n)

n_arr = np.array(n_list)
print(f'{n_arr.shape=}')
n_mean = np.mean(n_arr, axis=0)
n_std = np.std(n_arr, axis=0)

l_min_edges, l_max_edges = generate_bins(l_min_start=30, delta_l_min=30, l_max=lmax, fold=0.2)
bin_dl = nmt.NmtBin.from_edges(l_min_edges, l_max_edges, is_Dell=True)
ell_arr = bin_dl.get_effective_ells()

plt.figure(1)
plt.plot(ell_arr, rmv_mean - n_mean, label='debias rmv_mean 2sigma')
# plt.plot(ell_arr, rmv1_mean, label='rmv_mean 10sigma')
plt.plot(ell_arr, c_mean, label='c_mean')
plt.plot(ell_arr, cn_mean - n_mean, label='debias cn_mean')
plt.plot(ell_arr, pcn_mean - n_mean, label='debias pcn_mean')
plt.xlabel('$\\ell$')
plt.ylabel('$D_\\ell^{EE}$')
plt.semilogy()
plt.legend()
plt.title('debiased power spectrum')

plt.figure(2)
plt.plot(ell_arr, rmv_std, label='rmv_std 2sigma')
# plt.plot(ell_arr, rmv1_std, label='rmv_std 10sigma')
plt.plot(ell_arr, c_std, label='c_std')
plt.plot(ell_arr, cn_std, label='cn_std')
plt.plot(ell_arr, pcn_std, label='pcn_std')
plt.xlabel('$\\ell$')
plt.ylabel('$D_\\ell^{EE}$')
plt.semilogy()
plt.legend()
plt.title('standard deviation')

plt.figure(3)

plt.plot(ell_arr, rmv_mean - cn_mean, label='rmv res')
plt.plot(ell_arr, pcn_mean - cn_mean, label='pcn res')
plt.xlabel('$\\ell$')
plt.ylabel('$D_\\ell^{EE}$')
plt.ylim(-0.1,0.1)
plt.legend()
plt.title('residual power spectrum')

plt.show()




