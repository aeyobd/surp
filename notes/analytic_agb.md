---
title: Analytic AGB yields
author: Daniel Boyea
header-includes: |
    \usepackage{newtxtext, newtxmath}
---



The equation
============

Defining a succinct, minimal-parameter representation of AGB C behavior is challenging. 
AGB yields generally have the following properties: 

- a peak yield at mass between 2 and $3\,M_\odot$
- asymmetric peak
- near zero yield at both $1\,M_\odot$ and $8\,M_\odot$
- metallicity dependent total yield
- metallicity dependent peak location
- negative yields at lowest and highest masses at high metallicity


As a simple working model, we use cubic splines to represent the mass dependence multiplied by a linear metallicity-dependent term. 
Our parameters are 

- $m_0$
- $\delta m_+$
- $\delta m_-$
- $\zeta = dy/dz$
- $y_1$, the total yield at solar metallicity
- $y_0$, the (negative) low-mass yield
- $y_2$, the (negative) upper-intermediate-mass yield

And the resulting equation is
$$
\tilde{y}_{\rm C}^{\rm CC} = 
\kappa 
\begin{cases}
y_0 & m < m_- \\
y_0 + (y_1 - y_0) \left(3 (\frac{m - m_-}{m_0 - m_-})^2 - 
2 (\frac{m-m_-}{m_0 - m_-})^3\right) & m_- < m < m_0 \\
y_1 + (y_2 - y_1) \left(3 (\frac{m - m_0}{m_+ - m_0})^2 - 
2 (\frac{m-m_0}{m_+ - m_0})^3\right) & m_0 < m < m_+ \\
y_2 & m_+ > m
\end{cases}
$$

Where $\kappa$ represents an overall multiplication set such that the normalized IMF yields are as set, and 
$$
\kappa(Z) = \kappa_0 \left[y_1 + \eta \log_{10}(Z/Z_\odot) \right]
$$




Comparison to existing models
----------

![A comparison between the literature AGB yields (light lines) and the analytic model (heavy black line) \label{ana_agb}](figures/analytic_vs_studies_agb.pdf)

In Fig. \ref{ana_agb}, 

![The metallicity dependence of IMF-integrated AGB yields. ](figures/agb_ana_vs_z.pdf)


![agb_z](figures/agb_ana_dtd.pdf)





Effects of alternate parameters
========================

AGB fraction
----------


Metallicity dependence
---------------

Interestingly, the metallicity dependence of AGB yields does matter. Increasing the metallicity dependence "flattens" the caafe relationship. While we do only select one metallicity, because of the delay time of AGB yields, the higher Mg/Fe stars, which are formed with a rapidly declining SFH, reach higher metallicities faster. This means that the AGB progeneters are at lower metallicity than in regions where Mg/Fe is lower. As AGB yields are predicted to have a negative metallicity dependence, the resulting trends are flattened. 

We also note that the metallicity dependence of AGB yields is directly degenerate with the metallicity dependence of CCSNe in caah as this is mostlhy sensitive to the combined metallicity dependence of IMF-integrated C yields. 

![z_dep](figures/agb_z_dependence.pdf)





### Mass distribution

The masses which are important for AGB C production furthermore complicate results. When only upper intermediate mass stars produce C, the AGB componet is produced more quickly, resulting in a flatter caafe, similar to a higher CCSNe C fraction. 

![masses](figures/agb_mass.pdf)
![shift_mass](figures/shift_mass.pdf)

### Negative yields

![negative_yields](figures/negative_yields.pdf)


### Alternate SFH

![alt_sfh](figures/twoexp_strength.pdf)



Degeneracies
===============

![agb_f](figures/ia_agb_degeneracy.pdf)



Summary
================









