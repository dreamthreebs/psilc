import numpy as np
import healpy as hp
import matplotlib.pyplot as plt
import pandas as pd
import pymaster as nmt

def calc_dl_from_scalar_map(scalar_map, bl, apo_mask, bin_dl):
    scalar_field = nmt.NmtField(apo_mask, [scalar_map], beam=bl, masked_on_input=False)
    dl = nmt.compute_full_master(scalar_field, scalar_field, bin_dl)
    return dl[0]

def gen_ps_remove_map_pcn(rlz_idx, mask):

    m_res = np.load('./ps_cmb_noise_residual/2sigma/map0.npy')
    m_cmb_noise = np.load('../../../../fitdata/synthesis_data/2048/CMBNOISE/40/0.npy')[0].copy()
    m_all = m_res + m_cmb_noise
    
    # hp.orthview(m_all * mask, rot=[100,50,0], half_sky=True)
    # plt.show()
    return m_all * mask

def gen_ps_remove_map_pcfn(rlz_idx, mask):

    m_res = np.load('./ps_cmb_noise_residual/2sigma/map0.npy')
    m_cmb_noise = np.load('../../../../fitdata/synthesis_data/2048/CMBNOISE/40/0.npy')[0].copy()
    m_all = m_res + m_cmb_noise
    
    # hp.orthview(m_all * mask, rot=[100,50,0], half_sky=True)
    # plt.show()
    return m_all * mask

def cpr_spectrum_pcn(bin_mask, apo_mask, bl):
    bin_dl = nmt.NmtBin.from_edges([20,50,100,150,200,250,300,350,400,450,500,550,600],[50,100,150,200,250,300,350,400,450,500,550,600,650], is_Dell=True)
    ell_arr = bin_dl.get_effective_ells()

    m_inpaint = hp.read_map('./for_inpainting/output/pcn/0.fits', field=0) * bin_mask
    m_removal = gen_ps_remove_map_pcn(rlz_idx=0, mask=bin_mask)

    # dl_inpaint = calc_dl_from_scalar_map(m_inpaint, bl, apo_mask, bin_dl)
    dl_removal = calc_dl_from_scalar_map(m_removal, bl, apo_mask, bin_dl)

    m_ps_cmb_noise = np.load('../../../../fitdata/synthesis_data/2048/PSCMBNOISE/40/0.npy')[0]
    dl_ps_cmb_noise = calc_dl_from_scalar_map(m_ps_cmb_noise, bl, apo_mask, bin_dl)

    m_cmb_noise = np.load('../../../../fitdata/synthesis_data/2048/CMBNOISE/40/0.npy')[0]
    dl_cmb_noise = calc_dl_from_scalar_map(m_cmb_noise, bl, apo_mask, bin_dl)

    m_cmb = np.load('../../../../fitdata/2048/CMB/40/0.npy')[0]
    dl_cmb = calc_dl_from_scalar_map(m_cmb, bl, apo_mask, bin_dl)

    m_ps = np.load('../../../../fitdata/2048/PS/40/ps.npy')[0]
    dl_ps = calc_dl_from_scalar_map(m_ps, bl, apo_mask, bin_dl)

    m_ps_res = np.load('./ps_cmb_noise_residual/2sigma/map0.npy')
    dl_ps_res = calc_dl_from_scalar_map(m_ps_res, bl, apo_mask, bin_dl)


    # plt.plot(ell_arr, dl_inpaint, label='inpaint', marker='o')
    plt.plot(ell_arr, dl_removal, label='removal', marker='o')
    plt.plot(ell_arr, dl_ps_cmb_noise, label='ps+cmb+noise', marker='o')
    plt.plot(ell_arr, dl_cmb_noise, label='cmb+noise', marker='o')
    plt.plot(ell_arr, dl_cmb, label='cmb', marker='o')

    plt.plot(ell_arr, dl_ps, label='ps', marker='o')
    plt.plot(ell_arr, dl_ps_res, label='ps removal res', marker='o')

    plt.semilogy()
    plt.xlabel('l')
    plt.ylabel('Dl')

    plt.legend()
    plt.savefig('./fig/pcn/cpr_ps.svg')
    plt.show()


def cpr_spectrum_pcfn(bin_mask, apo_mask, bl):
    bin_dl = nmt.NmtBin.from_edges([20,50,100,150,200,250,300,350,400,450,500,550,600],[50,100,150,200,250,300,350,400,450,500,550,600,650], is_Dell=True)
    ell_arr = bin_dl.get_effective_ells()

    m_inpaint = hp.read_map('./for_inpainting/output/pcfn/0.fits', field=0) * bin_mask
    m_removal = gen_ps_remove_map_pcfn(rlz_idx=0, mask=bin_mask)

    dl_inpaint = calc_dl_from_scalar_map(m_inpaint, bl, apo_mask, bin_dl)
    dl_removal = calc_dl_from_scalar_map(m_removal, bl, apo_mask, bin_dl)

    m_ps_cmb_fg_noise = np.load('../../../../fitdata/synthesis_data/2048/PSCMBFGNOISE/40/0.npy')[0]
    dl_ps_cmb_fg_noise = calc_dl_from_scalar_map(m_ps_cmb_fg_noise, bl, apo_mask, bin_dl)

    m_cmb_fg_noise = np.load('../../../../fitdata/synthesis_data/2048/CMBFGNOISE/40/0.npy')[0]
    dl_cmb_fg_noise = calc_dl_from_scalar_map(m_cmb_fg_noise, bl, apo_mask, bin_dl)

    m_cmb = np.load('../../../../fitdata/2048/CMB/40/0.npy')[0]
    m_fg = np.load('../../../../fitdata/2048/FG/40/fg.npy')[0]

    dl_cmb_fg = calc_dl_from_scalar_map(m_cmb + m_fg, bl, apo_mask, bin_dl)
    dl_cmb = calc_dl_from_scalar_map(m_cmb, bl, apo_mask, bin_dl)

    dl_fg = calc_dl_from_scalar_map(m_fg, bl, apo_mask, bin_dl)

    m_ps = np.load('../../../../fitdata/2048/PS/40/ps.npy')[0]
    dl_ps = calc_dl_from_scalar_map(m_ps, bl, apo_mask, bin_dl)

    m_ps_res = np.load('./ps_cmb_noise_residual/2sigma/map0.npy')
    dl_ps_res = calc_dl_from_scalar_map(m_ps_res, bl, apo_mask, bin_dl)


    plt.plot(ell_arr, dl_inpaint, label='inpaint', marker='o')
    plt.plot(ell_arr, dl_removal, label='removal', marker='o')
    plt.plot(ell_arr, dl_ps_cmb_fg_noise, label='ps+cmb+fg+noise', marker='o')
    plt.plot(ell_arr, dl_cmb_fg_noise, label='cmb+fg+noise', marker='o')
    plt.plot(ell_arr, dl_cmb, label='cmb', marker='o')
    plt.plot(ell_arr, dl_fg, label='diffuse fg', marker='o')

    plt.plot(ell_arr, dl_ps, label='ps', marker='o')
    plt.plot(ell_arr, dl_ps_res, label='ps removal res', marker='o')

    plt.semilogy()
    plt.xlabel('l')
    plt.ylabel('Dl')

    plt.legend()
    plt.savefig('./fig/pcfn/cpr_ps.pdf')
    plt.show()



if __name__ == '__main__':

    lmax = 750
    l = np.arange(lmax+1)
    nside = 2048
    df = pd.read_csv('../../../../FGSim/FreqBand')

    freq = df.at[1, 'freq']
    beam = df.at[1, 'beam']
    print(f'{freq=}, {beam=}')
    bl = hp.gauss_beam(fwhm=np.deg2rad(beam)/60, lmax=7000, pol=True)[:,2]

    # apo_mask = np.load('../src/mask/north/APOMASK2048C1_8.npy')
    bin_mask = np.load('./ps_mask/no_edge_mask/C1_5.npy')
    apo_mask = np.load('./ps_mask/no_edge_mask/C1_5APO_5.npy')


    cpr_spectrum_pcn(bin_mask, apo_mask, bl)
    # cpr_spectrum_pcfn(bin_mask, apo_mask, bl)





