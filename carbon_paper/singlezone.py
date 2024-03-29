import numpy as np
import pandas as pd

import vice
import surp
from surp.simulation.sfh_models import insideout, exp_sfh, linexp, static, lateburst



def run_singlezone(
        dt=0.01, t_end=13.2, tau_sfh=None, 
        eta=0.5, tau_star=2.5, mode="sfr", sfh=insideout(tau_sfh=14),
        RIa="plaw", Mg0=1, verbose=False,
    ):
    """

    Note that the solar model has tau_sfh=14 with an insideout sfh
    Parameters
    ----------
    dt : float
        time step in Gyr
    t_end : float
        end time in Gyr
    sfh : function
        star formation history function. default is exponential
    tau_sfh : float
        star formation history decay timescale in Gyr
    eta : float
        mass loading factor
    tau_star : float
        star formation efficiency timescale in Gyr
    mode : str
        star formation mode, see vice documentation
    RIa : str
        SNe Ia delay time distribution, "exp" or "plaw", see vice documentation
    Mg0 : float
        Total gas mass
    verbose : bool
        print vice model info

    Returns
    -------
    out : vice output
        vice output object
    history : pandas DataFrame
        history of the singlezone model as a dataframe with APOGEE-like abundance columns
    """

    if tau_sfh is not None:
        sfh.tau_sfh = tau_sfh

    sz = vice.singlezone(
        elements=surp.ELEMENTS,
        func=sfh, mode=mode,
        eta=eta, tau_star=tau_star, 
        Mg0=Mg0, dt=dt
    )

    sz.RIa = RIa
    sz.Z_solar = surp.Z_SUN

    if verbose:
        print(sz)

    out = sz.run(np.arange(0, t_end, dt), capture=True, overwrite=True)

    return out, extract_history(out)


def extract_history(out):
    """Returns the history as a pandas DataFrame from a vice output
    with APOGEE-style column names"""
    history = pd.DataFrame(out.history.todict())

    Nele = len(out.elements)
    for i in range(Nele):
        for j in range(i+1):
            if j == i:
                B = "h"
            else:
                B = out.elements[i]
            A = out.elements[j]
            old_name = f"[{A}/{B}]"
            old_name_rev= f"[{B}/{A}]"
            new_name = f"{A}_{B}".upper()
            if old_name in history.keys():
                history[new_name] = history[old_name]
            elif old_name_rev in history.keys():
                history[new_name] = -history[old_name_rev]
            else:
                print("warning, key not found ", old_name)
        
    return history

