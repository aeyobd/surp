import vice
import sys 
from dataclasses import dataclass

sys.path.append("..")
from src.analysis.vice_model import vice_model


@dataclass
class model_id():
    agb: str = None
    eta: str = None
    f_agb: str = None
    beta: str = None
    name: str = None
    version: str = ""


def find_model(id):
    """
    Finds the pickled model with either the given name or the parameters 
    and returns the vice_model object
    """
    if id.name is None:
        name = id.agb + "_f" + id.f_agb + "_Z" + id.beta + "_eta" + id.eta + id.version
    else:
        name = id.name
    file_name = "../output/" + name + ".json"
    return vice_model(file_name)


def fiducial():
    fiducial = find_model(model_id(agb="cristallo11", f_agb="0.2", eta="1.0",
        beta="0.4", version="_v0.1.3"))
    return fiducial
