"""
I am so sorry that most of these parameters are named in reverse of YieldParams
"""
from surp import YieldParams, Z_SUN
import vice

noneq_factor = 1.025
noneq_A_factor = 1.8
noneq_zeta_factor = 1.8

Y_MG = 0.000652

Y_C_0 = 4.12 * Y_MG * noneq_factor # +- 0.01
ZETA_C_0 = 1.21 * Y_MG * noneq_factor * noneq_zeta_factor # +- 0.05
# quadratic coeff
A_C_0 = 3.07 * Y_MG * noneq_factor * noneq_A_factor # +- 0.07


Y_C_AGB= {
        "cristallo11": 3.8e-4,
        "ventura13": 1.85e-4,
        "karakas16": 2.8e-4,
        "pignatari16": 5.9e-4,
}

ZETA_C_AGB = {
        "cristallo11": -3.5e-4,
        "ventura13": -9.4e-4,
        "karakas16": -10.1e-4,
        "pignatari16": -5.7e-4,
}





Y_C_0_EXP = 2.85e-3 * noneq_factor
ZETA_C_0_EXP = 0.029 * noneq_factor

Y_C_0_LIN = 4.20 * Y_MG * noneq_factor # +- 0.009
ZETA_C_0_LIN = 1.64 * Y_MG  * noneq_factor # +- 0.044


# comments from linear regression of sampled points
# regression ran on points with M_H > -1 except -1.5 for P16 and -2 for C11
Y_C_AGB_EXP = {
        "cristallo11": 4.5e-4, # 3.5 +- 0.3
        "ventura13": 3.0e-4, # 1.6 +- 1.2
        "karakas16": 5.0e-4, # 2.9 +- 0.5
        "pignatari16": 9.2e-4, # 6.2 +- 0.1
}

ZETA_C_AGB_EXP = {
        "cristallo11": -0.015, # -0.0096 +- 0.0009
        "ventura13": -0.03, #  -0.018 pm 0.01
        "karakas16": -0.035, # -0.029 pm 0.003
        "pignatari16": -0.010, # -0.015 pm 0.003
}



def y_c_total(Z):
    """Returns our adopted total C yield given Z"""
    return Y_C_0 + ZETA_C_0*(Z-Z_SUN)

def y_c_lin(M_H):
    """Returns our adopted total C yield given [M/H]"""
    y_mg = vice.yields.ccsne.settings["mg"]
    return y_mg * (4.20 + 1.64*M_H)

def y_c_quad(M_H):
    y_mg = vice.yields.ccsne.settings["mg"]
    return y_mg * (4.12 + 1.21*M_H + 3.07*M_H**2)

def y_c_exp(M_H):
    y_mg = vice.yields.ccsne.settings["mg"]
    return y_mg * (3.57 + 0.588*10**M_H)

def make_yield_params( zeta_cc=None, agb_n_model="A", yield_scale=1, mlr="larson1974",
                      fe_ia_factor=1, y1=1e-4, Z1=0, cc_model="Lin", **kwargs):
    """Creates yields as given by """

    params = YieldParams(yield_scale=yield_scale, mlr=mlr)
    y_c_agb, zeta_c_agb = set_c_agb(params, **kwargs)

    y_c_cc = Y_C_0 - y_c_agb

    if zeta_cc is None:
        zeta_cc = ZETA_C_0 - zeta_c_agb

    set_c_cc(params, y0=y_c_cc, zeta=zeta_cc, model=cc_model, y1=y1, Z1=Z1)
    params.n_agb_model = agb_n_model

    enhance_fe_ia(params, fe_ia_factor)
    return params



def set_c_cc(params, y0, zeta, model="Lin", y1=1e-4, Z1=0):
    params.y0_c_cc = y0
    params.zeta_c_cc = zeta
    params.y_c_cc= model
    if model == "BiLin":
        params.kwargs_c_cc = dict(y1=y1, Z1=Z1)
    elif model == "BiLogLin":
        params.kwargs_c_cc = dict(y1=y1)
    elif model == "Quadratic":
        params.kwargs_c_cc = dict(A=A_C_0)


def set_c_agb(params, agb_model="cristallo11", f_agb=0.2, alpha_agb=None, zeta_agb=None, 
            mass_factor=1, no_negative=False, interp_kind="linear", t_D=0.1, tau_agb=0.3, low_z_flat=False):

    y0 = f_agb * Y_C_0
    params.y_c_agb = agb_model

    if agb_model == "A":
        if zeta_agb is None:
            raise ValueError("for analytic AGB model, zeta_agb must be specified")

        params.kwargs_c_agb = dict(t_D=t_D, tau_agb=tau_agb, y0=y0, zeta=zeta_agb)
        params.alpha_c_agb = 1
    else:
        params.kwargs_c_agb = dict(mass_factor=mass_factor, no_negative=no_negative, interp_kind=interp_kind, low_z_flat=low_z_flat)

        y_c_agb = Y_C_AGB[agb_model]
        if alpha_agb is None:
            alpha_agb = y0 / y_c_agb

        y0 = alpha_agb * y_c_agb

        zeta_agb = ZETA_C_AGB[agb_model] * alpha_agb
        params.alpha_c_agb = alpha_agb


    return y0, zeta_agb


def enhance_fe_ia(params, factor):
    """if factor != 1, then enhances sne ia fe yield by factor but maintains same total fe yield, applied to params"""
    if factor == 1:
        return
    y_fe = params.y_fe_cc + params.y_fe_ia
    params.y_fe_ia *= factor
    params.y_fe_cc = y_fe - params.y_fe_ia
    return params


def print_yc_tot():
    """prints out the current total c yield in an (almost nice) table"""

    print('total c yield')

    ycc = ccsne.settings["c"]
    yagb = agb.settings["c"]

    y0_cc = ycc.y0
    zeta_cc = ycc.zeta

    if isinstance(yagb, agb.interpolator):
        model = yagb.study
        alpha = yagb.prefactor
        y0_agb = alpha * Y_C_AGB[model]
        zeta_agb = alpha * ZETA_C_AGB[model]
        print("y0_agb ", Y_C_AGB[model])
        print("z0_agb ", ZETA_C_AGB[model])
    elif isinstance(yagb, C_AGB_Model):
        model = "A"
        y0_agb = yagb.y0
        zeta_agb = yagb.zeta
        print("Y agb", y0_agb)
        print("zeta agb", zeta_agb)

    print("agb_model: ", model)

    z_tot = zeta_cc + zeta_agb
    y_tot =  y0_agb + y0_cc
    f = y0_agb/y_tot

    print(f"{y_tot:0.6f} + {z_tot:0.6f} (Z-Zo)")
    print(f"f_agb = {f:0.4f}")
    print()
    print()


