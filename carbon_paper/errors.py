def polynomial(x, coeffs):
    s = 0
    N = len(coeffs)
    for i in range(N):
        power = (N - i - 1)
        s += coeffs[i] * x**(N - i - 1)

    return s

    
def fe_h_err(Fe_H):
    return polynomial(Fe_H, [-0.00557748, 0.00831548])

def c_mg_err(Fe_H):
    return polynomial(Fe_H, [-0.03789911, 0.03505672])

def mg_h_err(Fe_H):
    return polynomial(Fe_H,[0.06521454,0.00522015,0.03381753])


def mg_fe_err(Fe_H):
    return polynomial(Fe_H,[ 0.00792663,-0.00801737, 0.0138201 ])

