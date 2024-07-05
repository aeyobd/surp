from . import simulation
from .simulation import MWParams
from .simulation.create_model import create_model

from .yield_params import YieldParams
from . import utils
from . import yields
from .yields import set_yields
from . import gce_math
from ._globals import *

from .vice_model import ViceModel

from .subgiants import _read_subgiants
from .vincenzo import vincenzo2021 



def check_dependencies(dependencies):
    missing = []
    for package in dependencies:
        try:
            __import__(package)
        except ImportError:
            missing.append(package)
    return missing



missing_opt_deps = check_dependencies(['matplotlib', 'seaborn'])

if not missing_opt_deps:
    from . import plots
else:
    print(f"""Missing dependencies for `plots` module: 
    {', '.join(missing_opt_deps)}. 
The `plots` module will not be available.""")



# from . import yield_models
subgiants = _read_subgiants()
