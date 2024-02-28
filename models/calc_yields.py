Y_C_0 = 2.85e-3
ZETA_C_0 = 0.029

# comments from linear regression of sampled points
# regression ran on points with M_H > -1 except -1.5 for P16 and -2 for C11
Y_C_AGB = {
        "cristallo11": 3.8e-4, # 2.8 pm 0.5
        "ventura13": 2.1e-4, # 3.0 pm 1.3
        "karakas16": 3.6e-4, # 4.3 pm 0.6
        "pignatari16": 6.9e-4, # 7.5 pm 1.5
        "A": 5e-4,
}

ZETA_C_AGB = {
        "cristallo11": -0.01, # -0.032 pm 0.004
        "ventura13": -0.04, #  -0.04 pm 0.01
        "karakas16": -0.04, # -0.04 pm 0.006
        "pignatari16": -0.01, # -0.010 pm 0.16
}



def y_c_total(Z):
    """Returns our adopted total C yield given Z"""
    return Y_C_0 + ZETA_C_0*(Z-Z_SUN)


def make_yield_params( zeta_cc=None, fe_ia_factor=1,
        **kwargs):

    params = surp.yields.YieldParams()
    y_agb, zeta_agb = set_agb(params, **kwargs)


    y_cc = Y_C_0 - y_agb

    if zeta_cc is None:
        zeta_cc = ZETA_C_0 - zeta_agb

    params.c_cc_y0 = Y_C_0 - alpha_agb * y_c_agb
    params.c_cc_zeta = zeta_cc

    enahce_fe_ia(params, fe_ia_factor)
    return params



def set_agb(params, agb_model="cristallo11", f_agb=0.2, alpha_agb=None, zeta_agb=None):
    y_c_agb = Y_C_AGB[agb_model]

    if alpha_agb is None:
        alpha_agb = f_agb * Y_C_0 /y_c_agb

    y0 = alpha_agb * y_c_agb

    if agb_model == "A":
        if zeta_agb is None:
            raise ValueError("for analytic AGB model, zeta_agb must be specified")

        params.c_agb_zeta *= alpha_agb
        params.c_agb_alpha = alpha_agb
        params.c_agb_kwargs = dict(t_d_agb, tau_agb, etc.)
    else:
        params.c_agb_params = dict(alpha=alpha_agb, mass_factor=mass_factor, 
                no_negative=no_negative, interp_kind=interp_kind)
        # equals kwargs?
        zeta_agb = ZETA_C_AGB[agb_model] * alpha_agb

    return y0, zeta_agb


def enhance_fe_ia(params, factor)
    """if factor != 1, then enhances sne ia fe yield by factor but maintains same total fe yield, applied to params"""
    if factor == 1:
        return
    fe_total = params.fe_cc + params.fe_ia
    params.fe_ia *= factor
    params.fe_cc = fe_total - params.fe_ia
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


