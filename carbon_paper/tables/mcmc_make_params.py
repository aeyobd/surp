from mcmc_setup import results
import numpy as np
import math

keys = ["alpha", "y0_cc", "zeta_cc", ]
latex_table = ""

print("label\t" + "\t".join(keys) + r"\\")
print("\\hline\\\\")

labels = {
    "fruity": r"\fruity",
    "aton": r"\aton",
    "monash": r"\monash",
    "nugrid": r"\nugrid",
    "fruity_mf0.7": r"\fruity\ m0.7",
}


def round_value_with_uncertainty(value, uncertainty):
    """
    Round a value and its uncertainty using the rule:
    - Round the uncertainty to 1 significant figure,
    - Except when that first digit is '1', then keep 2 significant figures.
    """

    # Handle trivial case
    if uncertainty == 0:
        return value, uncertainty

    # Determine the order of magnitude of the uncertainty
    exponent = math.floor(math.log10(abs(uncertainty)))
    first_digit = int(uncertainty / (10**exponent))

    # Decide number of significant figures
    if first_digit == 1:
        sig_figs = 2
    else:
        sig_figs = 1

    # Round uncertainty to sig_figs
    rounded_unc = round(uncertainty, sig_figs - 1 - exponent)

    # Now round the value to match the uncertainty's decimal place
    # Determine decimal place of rounded_unc
    unc_exponent = math.floor(math.log10(abs(rounded_unc)))
    decimals = -(unc_exponent - (sig_figs - 1))
    rounded_val = round(value, decimals)

    return rounded_val, rounded_unc




def get_median_uncertainty(x):
    median = np.median(x)
    lower, upper = np.quantile(x, [0.16, 0.84])
    uncertainty = (upper - median, median - lower)  # Asymmetric uncertainties
    if abs(np.log10(uncertainty[1] / uncertainty[0])) > 0.02:
        print(f"uncertainty difference large for {key} in {label}: {uncertainty}")
    uncertainty = np.mean(uncertainty)

    return median, uncertainty

for model_key, label in labels.items():
    result = results[model_key]

    latex_table += f"{label:16}"

    # Extract parameter values and uncertainties
    parameter_lines = []
    for key in keys:
        if key not in result.samples.columns:
            parameter_lines.append(" ")
            continue

        x = result.samples[key]
        if key == "y0_cc":
            x += result.samples["zeta_cc"] # convert to y_0 in paper
            x *= 1e-3


        if key == "zeta_cc":
            x *= 1e-3 * np.log(10)

        if (model_key == "eta2") and (key not in ["f_agb"]):
            x *= 2


        median, uncertainty = get_median_uncertainty(x)
        if key == "alpha":
            parameter_lines.append(f"{median:0.2f}")
        else:
            parameter_lines.append(f"{median:0.2e}")
        
    latex_table += "  &  ".join(parameter_lines)
    latex_table += "\n"

print(latex_table)
