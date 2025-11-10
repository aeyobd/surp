from mcmc_setup import results
import numpy as np

keys = results["aton"].labels + ["f_agb", "y_tot"]
latex_table = ""

print(f"{'model':16} & $\\log p$ & " + " & ".join(keys) + r"\\")
print("\\hline\\\\")

labels = {
    "fruity": r"\fruity",
    "aton": r"\aton",
    "monash": r"\monash",
    "nugrid": r"\nugrid",
    "fruity_mf0.7": r"\fruity\ m0.7",
    "eta2": r"$y\rightarrow 2y$",
    "lateburst": r"lateburst",
    "twoinfall": r"twoinfall",
    "sneia_1.2": r"SN Ia 1.2",
    "fruity_sigma": r"\fruity",
    "aton_sigma": r"\aton",
    "monash_sigma": r"\monash",
    "nugrid_sigma": r"\nugrid",
    "fruity_mf0.7_sigma": r"\fruity\ m0.7",
}



for key, label in labels.items():
    result = results[key]
    #χ2 = calc_χ2(result, median=True, normalized=True)
    lp = np.max(result.samples.lp)

    
    # Add the row for χ2 and lp
    #{ χ2:8.1f} & 
    latex_table += f"{label:16} & {lp:8.2f} & "

    # Extract parameter values and uncertainties
    parameter_lines = []
    for key in keys:
        if key not in result.samples.columns:
            parameter_lines.append(" ")
            continue
            
        if key in ["y_tot", "zeta1_a"]:
            x = result.samples[key] / 1e-4
        else:
            x = result.samples[key]

        if key in ["y0_cc", "zeta_cc"]:
            x *= 10 # 1e-3 to 1e-4
        median = np.median(x)
        lower, upper = np.quantile(x, [0.16, 0.84])
        uncertainty = (upper - median, median - lower)  # Asymmetric uncertainties

        if key in ["alpha", "f_agb"]:
            formatted_value = f"${median:.2f}^{{+{uncertainty[0]:.2f}}}_{{-{uncertainty[1]:.2f}}}$"
        else:
            formatted_value = f"${median:.1f}^{{+{uncertainty[0]:.1f}}}_{{-{uncertainty[1]:.1f}}}$"
        parameter_lines.append(f"{formatted_value}")
        
    latex_table += "  &  ".join(parameter_lines)
    latex_table += "\\\\ \n"

print(latex_table)
