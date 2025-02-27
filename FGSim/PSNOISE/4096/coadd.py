import numpy as np
import healpy as hp
import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv('../../FreqBand5')

for i in range(len(df)):
    freq = df.at[i, 'freq']
    print(f'{freq=}')

    ps = hp.read_map(f'/sharefs/alicpt/users/zrzhang/allFreqPSMOutput/observations/AliCPT_uKCMB/{freq}GHz/group3_map_{freq}GHz.fits', field=(0,1,2))
    print(f'{hp.get_nside(ps)=}')

    # hp.mollview(ps[0], norm='hist', title='ps2048')
    # plt.show()

    ps4096 = hp.ud_grade(ps, nside_out=4096)

    # hp.mollview(ps512[0], norm='hist', title='ps512')
    # plt.show()

    nstd512 = np.load(f'../../NSTDNORTH/{freq}.npy')
    nstd4096 = hp.ud_grade(nstd512, nside_out=4096)
    n_pix_nstd = hp.nside2npix(nside=4096)

    noise = nstd4096 * np.random.normal(0,1,(3,n_pix_nstd))

    # hp.mollview(noise, title=f'noise at {freq=}')
    # plt.show()

    psnoise = ps4096 + noise
    hp.mollview(psnoise[0], title=f'{freq=}', norm='hist')
    plt.show()
    
    np.save(f'./{freq}psnoise.npy', psnoise)
    np.save(f'./{freq}nstd.npy', nstd4096)


