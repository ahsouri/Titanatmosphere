import numpy as np
import os
from time import time
import matplotlib.pyplot as plt
import sys
required_version = (3,3)
current_version = sys.version_info

os.environ['RTDATAPATH'] = '/mnt/c/Linux/PROJECTS/TIRAN/Titanatmosphere/refdata/'

import atmosphere as atm
from atmosphere.rt import pydisort

atm.refdata.setup_directory()

def create_atmosphere_model(**kw):
    """
    Setup layered atmospheric model using a default physical/thermal structure
    determined by HASI, and composition from the GCMS, with aerosol 
    scattering propertier from DISR.
    
    The titan dictionary contains the values used to determine the opacity
    and scattering albedo of each atmospheric layer as a function of
    wavelength. The dispersion axis is constrained by the k-coefficients that
    are used, as specified by the methane kc_file.
    """
    
    ts = time()
    titan = atm.structure.set_HASI_structure(nlev=21,method='split_at_tropopause')

    print("Levels:", titan["nlev"])
    print("Layers:", titan["nlay"])
    print(titan["layers"].keys())

  
    atm.composition.set_abundances(titan, trace_gas={'m_H2':0.001})


    layers = titan["layers"]

    fig, axs = plt.subplots(1, 2, figsize=(10, 5))

    axs[0].plot(layers["T"], layers["z"], "o-")
    axs[0].set_xlabel("Temperature (K)")
    axs[0].set_ylabel("Altitude (km)")
    axs[0].grid(True)

    axs[1].semilogx(layers["p"], layers["z"], "o-")
    axs[1].set_xlabel("Pressure (mbar)")
    axs[1].set_ylabel("Altitude (km)")
    axs[1].grid(True)

    #plt.tight_layout()
    #plt.show()

    #plt.figure(figsize=(5, 6))
    #plt.plot(
    #100 * layers["m_CH4"],
    #layers["z"],
    #"o-"
    #)

    #plt.xlabel("CH4 mole fraction (%)")
    #plt.ylabel("Altitude (km)")
    #plt.grid(True)
    #plt.show()

 
    atm.gas_opacity.set_methane(titan, 
                                kc_file=[
                                  os.path.join(os.environ['RTDATAPATH'],'gas_opacity/k-coefficients/kc_12CH4.VIMS_2004.v01.npy'),
                                  os.path.join(os.environ['RTDATAPATH'],'gas_opacity/k-coefficients/kc_12CH3D.VIMS_2004.v01.npy')
                                ],
                                CH3D_scale=5.28e-4
                                )
    
    atm.gas_opacity.set_cia(titan)

    lam = titan["wavelength"]  # micrometers 
    tau_ch4 = titan["layers"]["tau"]["CH4"]
    weights = titan["layers"]["kc"]["w"]

    # Layer-integrated optical depths at each g-node
    tau_column = np.sum(tau_ch4, axis=0)

    # Weighted optical-depth diagnostic
    tau_weighted = np.sum(
      tau_column * weights[None, :],
      axis=1
    )

    plt.figure(figsize=(10, 4))
    plt.semilogy(lam, np.maximum(tau_weighted, 1e-12))
    plt.xlabel("Wavelength (µm)")
    plt.ylabel("Weighted CH4 optical depth")
    plt.show()
 
    atm.aerosol.set_opacity(titan)


    lam = titan["wavelength"]
    haze_tau = titan["haze"]["tau"]

    plt.figure(figsize=(9, 4))

    for region in ["low", "mid", "high", "total"]:
       plt.plot(
        lam,
        haze_tau[region],
        label=region
       )

    #plt.yscale("log")
    #plt.xlabel("Wavelength (µm)")
    #plt.ylabel("Haze vertical optical depth")
    #plt.legend()
    #plt.grid(True)
    #plt.show()
    
    DISR = atm.aerosol.fit_DISR_phases()
    atm.aerosol.set_aerosol_phase_moments(titan, DISR, nmom=32)   
    t_setup = time()-ts
    
    titan['haze'].update({'ssalb':0.96})
    titan.update({'radius':2575.,
                  'rsurf':0.10,
                  't_setup':t_setup,
                 })
    if 'rsurf' in kw: titan.update({'rsurf':kw['rsurf']})
    if 'verbose' in kw and kw['verbose']:
        pstr = 'PyDISORT Titan atmosphere structure and opacity setup: {:4.1f} sec'
        print(pstr.format(titan['t_setup']))    
    
    return titan

def setup_VIMS_calc(**kw):
    """Specify the viewing geometry and wavelegth range for the
    radiative transfer calculation."""

    titan = create_atmosphere_model(**kw)
    titan.update({'rt':{'spher':False,
                        'wav_range':(2.0,2.40),
                        'view':{'umu0':0.99,'umue': 0.90,'phi0': 10.0,'phie': 11.0},
                       }})
    for k in ['view','wav_range']: 
        if k in kw: titan['rt'].update({k:kw[k]})
            
    fi = lambda array, v: abs(array-v).argmin()
    wav_indices = lambda array, wavs: tuple([fi(array, mu) for mu in wavs])
    wav_mn, wav_mx = wav_indices(titan['wavelength'], titan['rt']['wav_range'])
    titan['rt'].update({'wav_mn':wav_mn,
                        'wav_mx':wav_mx,
                        'nlam':wav_mx-wav_mn+1,
                        })          
    return titan

if __name__ == '__main__':

    if current_version >= required_version:
        ts = time()
        print('PyDISORT Running quick test.')
        titan = setup_VIMS_calc(wav_range=(2.0,2.01), verbose=True ) 
        pydisort.calculate_spectrum(titan)
        print("PyDISORT Calculation for {:d} channels complete: {:4.1f} sec [success]".format(
            titan['rt']['nlam'],
            time()-ts),)

        n_channels = min(30, titan["nlam"])
        lam = titan["wavelength"][:n_channels]
        radiance = titan["spectrum"][:n_channels]

        plt.plot(lam, radiance)
        plt.xlabel("Wavelength (µm)")
        plt.ylabel("DISORT modeled intensity")
        plt.show()
    else:
        print('PyDISORT Currently requires Python 3.3 or newer.')
