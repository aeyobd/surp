import numpy as np
import random
import vice
from surp.gce_math import is_high_alpha


def load_model(name, hydrodisk=False, zone_width=0.01):
    """Loads a vice.milkyway model output at the location name

    Parameters
    ----------
    name : str
        the name of the model to load
    hydrodisk : bool = False
        if hydrodisk, than reads in abs_z from  analogdata

    Returns
    -------
    vice.multioutput file
    """
    milkyway = vice.output(name)
    if hydrodisk:
        milkyway.stars["abs_z"] = calculate_z(milkyway)
    else:
        milkyway.stars["abs_z"] = [0 for _ in milkyway.stars["zone_origin"]]

    milkyway.stars["R_origin"] = zone_to_R(np.array(milkyway.stars["zone_origin"]), zone_width)
    milkyway.stars["R_final"] = zone_to_R(np.array(milkyway.stars["zone_final"]), zone_width)

    if "[c/o]" not in milkyway.stars.keys():
        milkyway.stars["[c/o]"] = -np.array(milkyway.stars["[o/c]"])
    if "[c/n]" not in milkyway.stars.keys():
        milkyway.stars["[c/n]"] = -np.array(milkyway.stars["[n/c]"])

    o_fe = np.array(milkyway.stars["[o/fe]"])
    fe_h = np.array(milkyway.stars["[fe/h]"])
    milkyway.stars["high_alpha"] = is_high_alpha(o_fe, fe_h)

    return milkyway




def sample_stars(stars, num=1000):
    r"""
    Samples a population of stars while respecting mass weights

    Parameters
    ----------
    stars: the stars attribute from vice.output
    num: (int) the number of stars to sample

    Returns
    -------
    A np.array of the sampled parameter from stars
    """

    size = len(stars.todict()["mass"])
    result = {key: np.zeros(num) for key in stars.keys()}

    index = random.choices(np.arange(size), weights=stars["mass"], k=num)
    for i in range(num):
        for key in stars.keys():
            result[key][i] = stars[key][index[i]]
    return vice.dataframe(result)





def R_to_zone(r: float, zone_width):
    return int(np.floor(r/zone_width))

def zone_to_R(zone: int, zone_width):
    return (zone + 1/2) * zone_width



def analogdata(filename):
    # from VICE/src/utils
    # last column of analogdata is z_height_final
    data = []
    with open(filename, 'r') as f:
        line = f.readline()
        while line[0] == '#':
            line = f.readline()
        while line != '':
            line = line.split()
            data.append([int(line[0]), float(line[1]), float(line[-1])])
            line = f.readline()
        f.close()
    return data


def calculate_z(output):
    analog_data = analogdata(output.name + "_analogdata.out")
    return [np.abs(row[-1]) for row in analog_data][:output.stars.size[0]]
