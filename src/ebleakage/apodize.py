import numpy as np
import healpy as hp
import matplotlib.pyplot as plt
import pymaster as nmt

def MaskApodize(mask_raw:np.ndarray, save_path:str, fig_bin_path:str, fig_apo_path:str, apodization_scale:float=1, flag:str='C2'):

    # The following function calls create apodized versions of the raw mask
    # with an apodization scale of 2.5 degrees using three different methods

    # Apodization scale in degrees
    aposcale = apodization_scale
    match flag:
        case 'C1':
            mask_res = nmt.mask_apodization(mask_raw, aposcale, apotype="C1")
        case 'C2':
            mask_res = nmt.mask_apodization(mask_raw, aposcale, apotype="C2")
        case 'Sm':
            mask_res = nmt.mask_apodization(mask_raw, aposcale, apotype="Smooth")

    np.save(save_path, mask_res)
    # Let's plot the results
    hp.mollview(mask_raw, title='Binary mask')
    plt.savefig(fig_bin_path,dpi=300)
    hp.mollview(mask_res, title=' apodized mask ')
    plt.savefig(fig_apo_path, dpi=300)
    plt.show()

if __name__=='__main__':

    mask_raw = np.load("./circle_mask2048.npy")
    fig_bin_path = '/afs/ihep.ac.cn/users/w/wangyiming25/tmp/20230920/NorthBinMask.png'
    fig_apo_path = '/afs/ihep.ac.cn/users/w/wangyiming25/tmp/20230920/NorthApoMask.png'

    save_path = "./apo_circle_mask2048C1_8.npy"
    MaskApodize(mask_raw, save_path, fig_bin_path,fig_apo_path,apodization_scale=8,flag='C1')

