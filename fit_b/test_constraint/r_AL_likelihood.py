import numpy as np
import pymaster as nmt
import matplotlib.pyplot as plt
from cobaya import run

method = 'pcfn'
cl_r = np.load(f'../../src/cmbsim/cmbdata/cmbcl_r_1.npy')
cl_AL = np.load(f'../../src/cmbsim/cmbdata/cmbcl_8k.npy')
lmax = 1500

print(f'{cl_r.shape=}')
print(f'{cl_AL.shape=}')

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

# generate bin
l_min_edges, l_max_edges = generate_bins(l_min_start=10, delta_l_min=30, l_max=lmax+1, fold=0.2)
bin_dl = nmt.NmtBin.from_edges(l_min_edges, l_max_edges, is_Dell=True)
ell_arr = bin_dl.get_effective_ells()
print(f'{ell_arr=}')
print(f'{ell_arr[1:8]=}')
ell_arr = ell_arr[1:8]

binned_cl_r = bin_dl.bin_cell(cls_in=cl_r[:lmax+1,2])[1:8]
binned_cl_AL = bin_dl.bin_cell(cls_in=cl_AL[:lmax+1,2])[1:8]

def load_data_inv_cov():
    _data_method = np.asarray([np.load(f'../nilc_5_freq/dl_res1/std/cfn/{rlz_idx}.npy')[1:8] for rlz_idx in range(1,200)])
    _data_noise = np.asarray([np.load(f'../nilc_5_freq/dl_res1/std/n_cfn/{rlz_idx}.npy')[1:8] for rlz_idx in range(1,200)])
    _data = _data_method - _data_noise
    _data_mean = np.mean(_data, axis=0)
    print(f'{np.size(_data_method, axis=1)=}')
    cov = np.zeros(shape=(7,7))
    for i in np.arange(np.size(_data_method, axis=1)):

        print(f'{i=}')
        print(np.cov(_data_method[:,i]))
        cov[i,i] = np.cov(_data_method[:,i])

    print(f'{_data.shape=}')
    print(f'{_data_mean.shape=}')
    # _cov = np.cov(_data_method, rowvar=False)
    _inv = np.linalg.inv(cov)
    print(f'{_inv=}')

    return _data_mean, _inv

data, inv_cov = load_data_inv_cov()
### check binned cl

plt.loglog(ell_arr, binned_cl_r, label='r')
plt.loglog(ell_arr, binned_cl_AL, label='AL')
plt.loglog(ell_arr, data, label='data')
plt.legend()
plt.show()

def r_AL_likelihood(r, AL):
    # remember to / -2
    model = r * binned_cl_r + AL * binned_cl_AL
    diff = data - model
    # print(f'{r=}, {AL=}')
    log_l = -0.5 * (diff @ inv_cov @ diff)
    print(f'{log_l=}')
    return log_l

r_AL_likelihood(r=0, AL=1.0)

info = {"likelihood": {"r&AL": r_AL_likelihood}}
info["params"] = {
    "r":  {"prior": {"min": -0.1, "max": 0.1}, "ref": 0.0, "proposal": 0.001},
    "AL": {"prior": {"min": 0.8, "max": 1.2}, "ref": 1.0, "proposal": 0.01}}

info["sampler"] = {"mcmc": {"Rminus1_stop": 0.001, "max_tries": 10000000}}
# info["sampler"] = {"minimize": {}}
info["output"] = "chains/r_AL"
updated_info, sampler = run(info)

# Export the results to GetDist
gd_sample = sampler.products(skip_samples=0.33,to_getdist=True)["sample"]

# Analyze and plot
mean = gd_sample.getMeans()[:2]
covmat = gd_sample.getCovMat().matrix[:2, :2]
print("Mean:")
print(mean)
print("Standard error:")
print(np.sqrt(covmat))
