import vice

C12_PROXY = "hg"
C13_PROXY = "tl"

def set_isotopic():
    c12_c13 = 89.3 # source: 
    c13 = vice.solar_z["c"] / (1 + c12_c13)
    c12 = c13 * c12_c13
    assert c12 + c13 == vice.solar_z["c"]
    assert c12 / c13 == c12_c13
    vice.solar_z[C12_PROXY] = c12
    vice.solar_z[C13_PROXY] = c13

