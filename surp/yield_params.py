from dataclasses import dataclass, field, asdict
import json


@dataclass
class YieldParams:
    """
    A class storing yield parameters for this project

    Params
    ------
    c_cc_model: [str] = "Lin"
        The CCSNe model to use. If Lin or LogLin, c_cc_y0 and c_cc_zeta are used.
        May also be a float or a recognized study in VICE
    c_cc_y0: [float]
        The CCSNe of C at Z=Z0
    c_cc_zeta: [float]
        The metallicity dependence of C CCSNe yields at Z=Z0
    c_cc_kwargs: dicct = {}
        Extra kwargs to pass to c_cc_model

    c_agb_model: str
        The C AGB model. May be a recognized study in VICE, or 
        - Zero
        - Lin
        - LogLin
        - BiLin
        - BiLogLin
    c_agb_alpha: float = 1
        factor to independenty scale C yield by (especially for use with published yields)

    n_agb_model: str
        

    """
    c_cc_model:str = "Lin"
    c_cc_y0:float = 2.28e-3
    c_cc_zeta:float = 0.03
    c_cc_kwargs:dict = field(default_factory=dict)

    c_agb_model:str = "cristallo11"
    c_agb_alpha:float = 1
    c_agb_kwargs:dict = field(default_factory=dict)

    n_agb_model:str = "A"
    n_agb_eta:float = 5.02e-4
    n_agb_y0:float = 0
    n_cc_y0: float = 5e-4
    n_cc_zeta: float = 0

    fe_ia: float = 7.7e-4
    fe_cc: float = 4.73e-4

    def to_dict(self):
        return asdict(self)

    def save(self, filename):
        with open(filename, "w") as f:
            json.dump(self.to_dict(), f, indent=4)


    @classmethod
    def from_file(cls, filename):
        with open(filename, "r") as f:
            params = json.load(f)
        return cls(**params)

