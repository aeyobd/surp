import numpy as np
import surp
from numbers import Number

keys = ["alpha_c_agb", "Y_c_agb", "y0_c_cc", "zeta_c_cc"]
latex_table = ""

print(f"{'model':16}"  + " & ".join(keys) + r"\\")
print("\\hline\\\\")

labels = {
    "fiducial/run": "fiducial",
    "fruity/zeta_lower": "zeta low",
    "fruity/zeta_higher": "zeta high",
    "fruity/f_0": "f=0",
    "fruity/f_0.5": "f=0.5",
    "fruity/fz_0": "f=0, zeta",
    "fruity/fz_0.5": "f=0.5, zeta",
    "fruity/best": "fruity",
    "aton/run": "aton",
    "monash/run": "monash",
    "nugrid/run": "nugrid",
    "fruity/agb_mass_0.7_alpha": "fruity shifted",
    "fruity/agb_mass_0.5": "mass factor 0.5",
    "fruity/agb_mass_0.7_fixed": "mass factor 0.7",
    "fruity/agb_mass_1.5": "mass factor 1.5",
}



for modelname, label in labels.items():
    result = surp.YieldParams.from_file("../../models/" + modelname + "/yield_params.toml")
    
    latex_table += f"{label:16} & "

    # Extract parameter values and uncertainties
    parameter_lines = []
    for key in keys:
        x = getattr(result, key)

        if key == "zeta_c_cc":
            x = surp.yield_models.zeta_to_slope(x) * surp.Z_SUN

        if key in ["y0_c_cc", "zeta_c_cc"]:
            x *= 1/1e-4

        if isinstance(x, Number):
            s = f"{x:0.2f}"
        else:
            s = f"{x:12}"
        parameter_lines.append(f"{s}")
        
    latex_table += "  &  ".join(parameter_lines)
    latex_table += "\\\\ \n"

print(latex_table)
