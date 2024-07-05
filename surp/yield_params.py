from surp.utils import AbstractParams

from typing import Union


class YieldParams(AbstractParams):
    """
    A class storing yield parameters for this project (C, N, Fe).
    Mg, O are held fixed. Note that the IMF is set through the vice singlezone
    and multizone models. This is helpful so that I can store yields
    as plain text files.

    Params
    ------
    yield_scale: float
        A global scaling factor for all yields
    mlr: str
        The mass lifetime relation. See ``vice.mlr`` for options


    yield_model_c_cc: str
        The CCSNe model to use. If Lin or LogLin, c_cc_y0 and c_cc_zeta are used.
        May also be a float or a recognized study in VICE
        - Zero
        - Lin
        - LogLin
        - BiLin
        - BiLogLin
        - Quadratic
    zeta_c_cc: [float]
        The metallicity dependence of C CCSNe yields at Z=Z0
    kwargs_c_cc: dict
        Extra kwargs to pass to c_cc_model
    y0_c_cc: float
        The CCSNe of C at Z=Z0
    c_cc_kwargs: dicct = {}
        Extra kwargs to pass to c_cc_model

    Y_c_agb: str
        The C AGB model. May be a recognized study in VICE, or "A" to use the analytic C AGB model
    alpha_c_agb: float = 1
        factor to independenty scale C yield by (especially for use with published yields)
    kwargs_c_agb: dict = {}
        Extra kwargs to pass to c_agb_model

    Y_n_agb: str = A
        The N AGB model. May be a recognized study in VICE, or "A" to use the analytic N AGB model
    eta_n_agb: float
        If n_agb_model="A", the scale factor for the yield
    y0_n_agb: float
        If n_agb_model="A", the solar yield of AGB N

    y0_n_cc: float
        The N yield of CCSNe at Z=Z0
    zeta_n_cc: float = 0
        The metallicity dependence of N CCSNe yields at Z=Z0
        

    y_fe_ia: float
        The iron yield of Ia supernovae
    y_fe_cc: float
        The iron yield of CCSNe

    """

    yield_scale: float #= 1
    mlr:str #= "larson1974"

    # carbon
    y_c_cc:Union[float, str]
    y0_c_cc:float #= 2.28e-3
    zeta_c_cc:float# = 0.00
    kwargs_c_cc:dict# = field(default_factory=dict)

    Y_c_agb:str #= "cristallo11"
    alpha_c_agb:float #= 1
    kwargs_c_agb:dict #= field(default_factory=dict)

    y_c_ia:float #= 0 # maximum is ~ 1.12e-4 from iwamoto + 99

    # nitrogen
    y0_n_cc: float #= 5e-4
    zeta_n_cc: float #= 0

    Y_n_agb:str #= "A"
    kwargs_n_agb:dict #= field(default_factory=dict)
    eta_n_agb:float #= 5.02e-4
    y0_n_agb:float #= 0

    # iron
    y_fe_cc: float #= 4.73e-4
    y_fe_ia: float #= 7.7e-4

