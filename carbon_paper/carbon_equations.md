# Assumptions and background

Here, I can follow the WAF method to solve for the evolution of C abundances for different assumptions about the yields.

## Introduction to Chemical Evolution

The simplest model of chemical evolution is a single-zone model, where the system consists of a single homogenous gas reservoir which is instantaneously mixed. Thus, baryonic matter exists in the system in a gas-phase or a stellar phase. 

The processes that affect the ISM are

- Inflows, adding gas material to the system
- Outflows, removing material from the ISM
- ISM formed into stars (removing gas and metals from the system)
- Material returned from stars back to the ISM

The resulting equations for the change in total ISM mass ($M_{\rm gas}$) and the ISM mass of element $X$ ($M_{\rm gas,\;x}$) are given by
$$
\dot{M}_{\rm gas} = \dot{M}_{\rm in} - \dot{M}_{\rm out} - \dot{M}_{\star} + \dot{M}_{\rm return} \\
\dot{M}_X = \dot{M}_{\rm in, X} - \dot{M}_{\rm out, X} - \dot{M}_{\star, X} + \dot{M}_{\rm return, X} + \dot{M}_{\rm new, X}
$$
where $\dot{M}_{\star}$ is the rate of star formation and $\dot{M}_{\rm return}$ is the rate that stars return material back to the ISM. To simplify these equations, we apply the following assumptions

- Inflows are zero metallicity, so $\dot{M}_{\rm in, X}=0$
- Outflows remove material proportional to the SFH with the ISM abundance, $\dot{M}_{\rm out} = \eta\;\dot{M}_\star$, $\dot{M}_{\rm out, X} = Z_X\;\eta\; \dot{M}_\star$ 
- Recycling is instantaneous and constant: $\dot{M}_{\rm return} = r \dot{M}_\star$ , $\dot{M}_{return, X} = Z_X\;r\;\dot{M}_\star$ 
- The SFH present-day yields are represented as $\langle y_X \rangle$, so that the newly produced mass of $X$ is given by $\dot{M}_{\rm new, X} = \langle y_X \rangle \dot{M}_\star$ 
- The star formation rate is proportional to the gas mass, $\dot{M}_\star = M_g / \tau_\star$

So, the change in ISM mass equation becomes
$$
\dot{M}_g = \dot{M}_{\rm in} - \dot{M}_\star ( 1 + \eta - r)
$$

which allows solving for the IFR if the metallicity of inflows is non zero. For a given element $X$, the rate of gas evolution is now determined by the form
$$
\dot{M}_X = \langle y_X\rangle_\star\dot{M}_\star - (1+\eta - r) Z_X\,\dot{M}_\star
$$
where the first term describes the present-day enrichment rate (a convolution on the system/star formation history for delayed-processes)  and the second term describes the evolution of the mass of the material due to the element locked away in stars, released through outflows, and returned by older stars.

The SFH-averaged effective yield is 
$$
\langle y_X \rangle(t) = \frac{\int_0^t \dot{M}_\star(t')\,\dot{M}_{X, \rm SSP}\,(Z_{\rm ISM}, t-t')\,dt' }{\dot{M}_\star}
$$
where $\dot{M}_{X, \rm SSP}$ is the rate of new $X$ ejected from a single stellar population of metallicity $Z$ at time $t-t'$ after birth. The integrand in detail looks different depending on the process (and can incorporate either a stellar-mass-dependent yield or some DTD prescription). Written in terms of a time-dependent yield and a DTD $R(t)$, this equation beomes
$$
\dot{M}_\star \langle y_X \rangle = \frac{\int_0^t \dot{M}_\star(t') y_C(t') R(t-t')\; dt'}{\int_0^{t_{\rm end}} R(t') dt'}
$$


## Solving Equations of evolution

By defining 
$$
1/\varpi = \tau_{\rm dep} = \frac{\tau_\star}{1+\eta - r}
$$
using $\tau_\star = M_g / \dot{M}_\star$, the above differential equation can be rewritten as
$$
\dot{M}_{X} + \varpi M_{X} = \lang \dot{m}_{X} \rang_\star
$$
To solve this equation, we can use that a differential equation of the form $\dot{M} + p(t) M = f(t)$ is solved with
$$
M(t) = \frac{1}{\mu} \left[ \int_0^t \mu(t')\, f(t')\ dt' + C\right]
$$
where $\mu(t) = \exp{\int p(t)\ dt}$ . In our case, $p(t) = \varpi$, so $\mu(t) = \epsilon(-\varpi t)$, and $f(t) = \dot{M}_\star \langle y_X\rangle$. We can find $M_C(t)$ with
$$
M_{\rm C}(t) =  \epsilon(\varpi t) \int_0^t \epsilon(-\varpi t')\ \langle \dot{m}_{\rm C} \rangle(t') \ dt'
$$

Or in terms of metallicity
$$
Z_X(t) = \frac{\epsilon(\varpi t)}{M_g(t)} \int_0^t \epsilon(-\varpi t')\;\langle \dot{m}_X \rangle (t')\; dt'
$$


So, to solve these equations, we first integrate to find $\langle \dot{M}_X \rangle $ and then integrate to solve for the ISM mass $M_X(t)$ and finally divide by the gas mass (given by the SFH) to find $Z_X(t)$. 

For CCSNe, $\lang \dot{m}_{X} \rang_\star = y_{X}\ \dot{M}_\star $ since $R(t) \approx \delta(t)$, so the equation tends to be much simpler.

## Convenience definitions

I have defined the following functions and variables to make later expressions much easier to work with. Firstly, 
$$
\epsilon(x) \equiv e^{-x}\\
\epsilon_i(x) = x^i\,e^{-x}
$$
As a helper, we will need
$$
c_{i, j} \equiv \frac{i!}{j! (i-j)!}
$$
which represents the combination i choose j.

We will also adopt the summation convention
$$
a_i b_i \equiv \sum_i a_i b_i
$$
for any index repeated two or more times. 

The derivative is then 
$$
\frac{d}{dx} \epsilon_i(x) = -\epsilon_i(x) - i \epsilon_{i-1}x\\
\frac{d}{dx} \epsilon(x) = -\epsilon(x)
$$
And the integrals are given by

! TODO HERE

Given these definitions, the integrals and derivatives are
$$
\int \epsilon(ax)\,dx = -\frac{1}{a} \epsilon(ax)\\
\int \chi(ax) = -\frac{1}{a} \chi(ax) - \frac{1}{a} \epsilon(ax)\\
\frac{d}{dy} \epsilon(y) = -\frac{dy}{dx} \epsilon(y) \\
\frac{d}{dx} \chi(y) = \frac{da}{dx} \epsilon(y) - \frac{dy}{dx} \chi(y)
$$
furthermore, I like writing all the timescales instead as frequencies which avoids more complex algebraic expressions later on.

# Equilibrium

### Constant SFH

In the event that $\dot{M}_\star$ is constant, then, $\langle \dot{m}_X\rangle_\star = m_x = y_X \dot{M}_\star$ for any process (as they are all time-independent), so that if the system evolves to reach equilibrium, the equilibrium value of $Z_X$ (found by setting $\dot{M}_X$ to zero above) is given by
$$
Z_{X,\;\rm Eq(cosnt)} = \frac{y_X}{1+\eta - r} = \frac{y_X}{\tau_\star \varpi}
$$

### Exponential SFH

However, in the case that $\dot{M}_\star$ is exponential, equilibrium becomes more complex, depending on the rate of star formation decline. Because the gas mass is now $M_g = M_{g, 0} \exp(-t/\tau_{\rm sfh})$, we can rewrite the above evolution equation in terms of 
$$
Z_{X, \rm eq} = \frac{\langle y_X \rangle_\star}{1 + \eta - r - \tau_\star / \tau_{\rm sfh}} = \frac{\langle y \rangle}{\tau_\star (\varpi - \phi)}
$$

 For instance, the mean yield of sneia Fe in our prescription is given by
$$
\nu_{\rm Fe}^{\rm Ia} = \frac{\int_0^t \dot{M}_\star(t') R(t-t') dt'}{\dot{M}_\star\int_0^\infty R(t') dt'}
$$
For the exponential delay time distribution, 
$$
\nu_{\rm Fe}^{\rm Ia} = \frac{\iota}{\iota - \phi} \epsilon(-\phi\;t_D) (1 - \epsilon((\iota - \phi)\Delta	t))
$$


And for AGB stars (the most complex of all of them)
$$
\nu_{\rm X}^{\rm AGB} = \frac{\int_0^t Y_X^{\rm AGB}(m_{\rm AGB}(t-t'), Z(t')) \dot{M_\star}(t') \dot{h}(t-t') dt'
}{
y_{X}^{\rm AGB} \dot{M}_\star }
$$
where
$$
h_{\rm agb}(t) = \frac{\int_l^{m_{\rm agb}(t)} m\, \frac{dN}{dm}\,dm}{\int_l^u m\, \frac{dN}{dm}\,dm}
$$
so 
$$
\dot{h}_{\rm agb} = \frac{1}{\int_l^u m \frac{dN}{dm}\,dm} \left(m_{\rm agb} \dot{m}_{\rm agb} \frac{dN}{dm} \right)
$$
where we have suppresed the dependences on $t$ or $m_{\rm agb}(t)$ for all components.

# Constant SFH

Constant star formation history is expressed as simply $M_{\rm gas}(t) = M_0$, which is the simplist case.

## Constant CCSNe 

Most directly applicable to O and Mg, and a good approximation for $Z$. $y(Z) = y_0$. 
$$
Z_{\rm Mg} = Z_{\rm Mg}^{\rm eq} \left[ 1 - \epsilon(\varpi t)\right]
$$


where 
$$
Z_{\rm Mg}^{\rm eq} = \frac{y_{\rm Mg}}{\tau_\star\, \varpi} = \frac{y_{\rm Mg}}{1 + \eta - r}
$$


## Linear Z CCSNe 

Say that a yield is linearly dependent on $Z$, i.e.
$$
y(Z) = \zeta\,Z
$$
We know what $Z$ is from above, we know $y(t)$ and can integrate over this, using that $Z(t) \approx Z_{\rm Mg}\  Z_\odot / Z_{\rm Mg,\ \odot} = \frac{y_{\rm Mg} Z_\odot}{\tau_\star\,\varpi Z_{\rm Mg,\ \odot}}(1 - \epsilon(\varpi t))$ 
$$
y(t) = y(Z(t)) = \zeta' (1 - \epsilon(\varpi t))
$$
where we have defined $\zeta' \equiv \zeta y_{\rm Mg} Z_{\odot} / (\tau_\star \varpi Z_{\rm Mg,\,\odot})$. Since addition is separable, the first term of $y(t)$ evaluates to the constant Z solution above, and the second term is
$$
Z_{\rm C,\,lin}(t) = - \frac{\zeta'}{\tau_\star}\ t\,\epsilon(\varpi t)
$$
so the metallicity dependent yield in total is 
$$
Z_{\rm C}(t) = Z_{\rm C}^{\rm eq} (\zeta' + y_{\rm C, 0})( 1 - \epsilon(\varpi(t))) - \zeta' \frac{t}{\tau_\star}\,\epsilon(\varpi\,t)
$$


## Sne Ia (exp)

The exponential SNe Ia delay time distribution is given as
$$
R(t) \sim \begin{cases}
\iota \exp(-\iota\ \Delta x) & x > t_D \\
0 & {\rm else}
\end{cases}
$$
and
$$
Z_{\rm Fe}^{\rm Ia}(t) = \frac{y^{\rm Ia}}{\tau_\star\,\varpi} \left[1 - \frac{\iota}{\iota - \varpi} \epsilon(\varpi\,\Delta t) + \frac{\varpi}{\iota - \varpi} \epsilon(\iota\,\Delta t)\right]
$$


## SNe Ia (plaw)

In the analytically tractable special case that $R \sim t^{-1}$, the integrals can be evaluated in terms of the Exponential Integral ${\rm Ei}(t) = \int_{-\infty}^t \exp (t)\ dt / t$.

The one issue is that $R$ is no longer normalizable, but I just leave that factor out for now. The resulting formula is
$$
Z_{\rm Fe}^{\rm Ia}(t) = Z_{\rm Fe}^{\rm Ia,\,eq} \left[\log t/t_D - \epsilon(\varpi\,t) ({\rm Ei}(\varpi\,t) - {\rm Ei}(\varpi\,t_D) \right]
$$


## AGB



# Exponential SFH

Assume that $\dot{M}_\star \propto \epsilon(\phi t) = \exp(-t/\tau_{\rm sfh}) = \epsilon(\phi t)$. 

## CCSNe

$$
Z_X^{\rm CC}(t) = Z_{X, \rm Eq(exp)}^{\rm CC} \left[1 - \epsilon(\varpi t - \phi t)\right]
$$

which looks the same as for a constant SFH except with an increase on the depletion timescale.

## SneIa (exp)


$$
Z^{\rm Ia}(t) = Z_X^{\rm eq, exp} \left[
1 - \frac{\varpi - \phi}{\varpi - \iota}
\epsilon((\iota - \phi)\Delta  t) 
- \left(1 - \frac{\varpi - \phi}{\varpi - \iota} \right)
\epsilon((\varpi - \phi)\Delta  t)
\right]
$$
where 
$$
Z_{X}^{\rm eq, exp} = \frac{y}{\tau_\star (\varpi - \phi)} \frac{\iota}{\iota - \phi} \epsilon(-\phi\;t_d)
$$
is the limit of the time-dependent equilibrium expression above.

# Old work



## Oxygen (pure CCSNe)

# Oxygen

The simplest solution is a pure CCSNe yield with no metallicity dependence, such as O or Mg. 

## Constant Yields

Hereafter, I will simply use $\tau$ for $\tau_{\rm dep}$, and $Z$ and $y$ are taken to be specific to the yield in question. We also use $Z_{\rm eq} = \tau/\tau_\star\ y(Z_{\rm O, eq}) $. 

If $y$ is constant, then the solution to the integral equation is simply
$$
Z(t) = y \frac{\tau_{\rm dep}}{\tau_\star} \left(1 - e^{-t/\tau} \right)
$$
We will use this solution for $Z_O$, which we assume to be the only dependence of $y_{\rm C}$. A useful simplification is $Z_{\rm O}^{\rm eq} = y_{\rm O} \ \tau_{\rm dep}/\tau_\star$.

It is useful to also rewrite the exponential in terms of $Z$, where
$$
e^{-t/\tau} = 1 - \frac{Z_{\rm O}}{Z_{\rm O, eq}} = 1-q
$$

where 
$$
q \equiv \frac{Z_O}{Z_{\rm O}^{eq}}
$$



# Iron

We will consider two different SNe Ia delay time distributions
$$
R_{\rm ia,\ exp} = \exp(-t/\tau_{\rm ia}), t > t_D
$$
and the powerlaw 
$$
R_{\rm ia, \ plaw} \propto t^{-\kappa}, t > t_D
$$
where $\kappa = 1$ is the most analytically tractable form that we will solve here

## Constant SFH



# CCSNe Carbon



## Linear dependence


$$
y(Z_O) = \zeta Z_{\rm O}
$$
then, we find that
$$
Z(t) = Z_{\rm eq} \left( 1 - e^{-t/\tau} - t/\tau\ e^{-t/\tau} \right)
$$
The linear dependence adds a $t e^{-t/\tau}$ term which simply slows the approach to equilibrium by a factor of $\sim$ 2. Rewriting in terms of $Z_O$, we have
$$
Z(t) = Z_{\rm eq}\left(q + (1-q)\log(1-q)\right)
$$
whre 

## Quadratic Dependence

$$
y(Z_O) = \xi {Z_{\rm O}}^2
$$

gives 
$$
Z(t) = Z_{\rm eq} \left(1 - e^{-2t/\tau} - 2\frac{t}{\tau} e^{-t/\tau} \right)
$$

or otherwise
$$
Z(t) =\left(1 - (1-q)^2 - 2(1-q) \log(1-q)  \right)
$$


## Log dependence

Another form is for the yield to be linearly dependent on $\log Z_{\rm O}$,
$$
y(Z_{\rm O}) = a\ \log(q)
$$
while this form isn't immediately useful, we can scale the reference value of the log by adding a constant (which we know how to solve), so this simplified form is still workable. here, sagemath gives

```
(a*τ*e^(t/τ)*log((e^(t/τ) - 1)*e^(-t/τ)) - a*τ*log(e^(t/τ) - 1))*e^(-t/τ)/τs
```

which is 
$$
Z = e^{-t/\tau}\frac{a\,\tau}{\tau_\star} \left(e^{t/\tau}\log(1-e^{-t/\tau}) - \log(e^{t/\tau} - 1) \right)
$$
simplifying to


$$
Z = \frac{a\,\tau}{\tau_\star} \left(\log(q) -(1-q) \log\left(\frac{q}{1-q}\right)\right)
$$

$$
Z = \frac{a\,\tau}{\tau_\star} \left(q\log(q) + (1-q) \log(1-q) \right)
$$

## Log-squared dependence


$$
-e^{-t/τ}/τs (b\,τ \log(Z_{eq})^2 - (τ e^{t/τ}\log(Z_O)^2 - (2\log(Z_o)\log(e^{t/τ} - 1) - \log(e^{t/τ} - 1)^2 + 2t\log(e^{t/τ} - 1)/τ + 2 {\rm dilog}(-e^{t/τ} + 1))τ)b)
$$
Which can be simplified to 
$$

$$

```
(b*τ*e^(t/τ)*log((Zeq*e^(t/τ) - Zeq)*e^(-t/τ))^2 - b*τ*log(Zeq)^2 - 2*b*τ*log((Zeq*e^(t/τ) - Zeq)*e^(-t/τ))*log(e^(t/τ) - 1) + b*τ*log(e^(t/τ) - 1)^2 - 2*b*τ*dilog(-e^(t/τ) + 1) - 2*b*t*log(e^(t/τ) - 1))*e^(-t/τ)/τs
```



## Sigmoid dependence

Finally, consider
$$
y = \frac{1}{a + Z_{\rm O}}
$$
This results in 

```
e^(-t/τ)/((a^2 + 2*a + 1)*τs) ( (a + 1)*τ*e^(t/τ) - (a + log(-a) + 1)*τ + τ*log(-((a + 1)*e^(t/τ) - 1)*e^(-t/τ)) + t )
```

which simplifies to 
$$
e^{t/\tau} \frac{\tau}{\tau_\star (a+1)^2} \left((a+1)  e^{t/\tau} - (a+\log(-a) + 1) + \log(-((a+1)e^{t/\tau}-1)e^{-t/\tau})) + t/\tau\right)
$$










# The AGBS

## DTD

For the delay time distribution, I use
$$
R(t) = \begin{cases}
0 & t<t_D\\
R_0\ \Delta t\,e^{-\Delta t/\tau_{\rm agb}}
\end{cases}
$$
where we use $\Delta t = t - t_D$. The normalization constant is
$$
R_0^{-1} = \int Rdt = τ_{\rm agb}^2.
$$
We can calculate what the mass distribution must be with 
$$
y(m) = \frac{1}{m} \frac{dt}{dm}\frac{dm}{dN} R(t)
$$
Using that $t(m) \propto m^{-\alpha_{\rm mlr}}$ where $\alpha_{\rm mlr}=3.5$  and $dN/dm = m^{-2.3}$ . 
$$
y(m) = \frac{1}{m}\ m^{-4.5} m^{2.3} R(m^{-1/3.5}) = m^{-3.2}\ R(m^{-3.5})
$$
for our distribution
$$
y(m) \propto m^{-3.2}(\tau_\odot\, m^{-3.5} - t_D) e^{-(\tau_\odot\, m^{-3.5} - t_D)/\tau_{\rm agb}}
$$
for $m < m_{up}$, defined by the minimum delay $t_d$,

This is a horrid expression but is integrable and can be used to specify the input to vice.  For the special case $t_D = 0.015$ and $\tau_{\rm agb} = 0.3$, then the integral is 0.0038202434.

## Abundances

The SFH averaged yield is
$$
y_{\rm agb}\langle \dot{M}_\star\rangle = \int_0^t \dot{M}_\star(t')\ R(t-t
')\ y(Z_{\rm O}(t'))\ dt'
$$
since $\dot{M}_\star = M_0 / \tau_\star$ is constant.  In practice, it is helpful to rearange the equation


$$
y_{\rm agb}\langle \dot{M}_\star\rangle = \frac{M_0}{\tau_\star} \int_{0}^{\Delta t}\ R(t
')\ y(Z_{\rm O}(t-t'))\ dt'
$$


The rest of the solution is the same as above, so we can use this value for $y$ and thus
$$
Z_{\rm agb}(t) = \frac{1}{M_g\ \tau_\star} e^{-t/\tau_{\rm dep}} \int_0^t e^{t'/\tau_{\rm dep}}\ y_{\rm agb}\lang \dot{M}_\star \rang(t')\ dt'
$$


## Constant Yield



In this case
$$
\lang y \rang / M_g = \frac{y_{\rm agb}}{\tau_\star} \left(1 - \left(1 + \frac{\Delta t}{\tau_{\rm agb}}\right) e^{-\Delta t/\tau_{\rm agb}} \right)
$$


so

```
Z_c_agb(t) = ((τ^3*e^(t/τ) - 2*τ^2*τa*e^(t/τ) + τ*τa^2*e^(t/τ) - τ^3*e^(t_d/τ))*e^(t/τa) + ((t - t_d)*τ^2*e^(t/τ) - τ*τa^2*e^(t/τ) - ((t - t_d)*τ - 2*τ^2)*τa*e^(t/τ))*e^(t_d/τa))*e^(-t/τa)/((τ^2*e^(t/τ) - 2*τ*τa*e^(t/τ) + τa^2*e^(t/τ))*τs)
```







# Inverse transform 

$$
y_{\rm C} = \frac{\tau_\star}{\tau_{\rm dep}} \left(Z_{\rm C} + (1-q) \frac{dZ_{\rm c}}{dq}\right)
$$

assuming CCSNe make up 100% of C. In the equilibrium limit, $q=1$ which reduces correctly. Note that if $q=0$, than the derivative of $Z$ depends as much as $Z$ itself. Rewriting in terms of $Z_O$, 
$$
y_{\rm C} = \frac{y_{\rm O}}{Z_{\rm O, eq}} \left(Z_{\rm C}  + (Z_{\rm O, eq} - Z_{\rm O}) \frac{dZ_{\rm C}}{d Z_{\rm O}}\right)
$$


## As applied to AGB

The main difference is $y$ is replaced with the SFH averaged.

## Estimating Q

for the above to be useful, we need an estimate of $q$ or equivalently $Z_{\rm eq, O}$. 


$$
Z_{\rm Fe}^{\rm Ia} = y_{\rm Fe}^{\rm Ia} \frac{\tau_{\rm dep}}{\tau_\star} \left[1 - e^{-\Delta t/\tau_{\rm dep}} - \frac{\tau_{\rm dep, ia}}{\tau_{\rm dep}} \left( e^{-\Delta t/\tau_{\rm Ia}} - e^{-\Delta t/\tau_{\rm dep}} \right)\right]
$$
This equation can be rewritten in terms of $q$ but is not easily invertible. A strong, simplifying assumption is that $\tau_{\rm dep} \approx \tau_{\rm ia}$, which leads to 
$$
Z_{\rm Fe}^{\rm Ia} = \frac{\tau_{\rm dep}}{\tau_\star}\left(\right)
$$
approximating yet again, the $t\,e^{-t/\tau_{\rm dep}}$ term can be approximated as $e^{-t/2\tau_{\rm dep}}$, so $q_{\rm Ia} \sim \sqrt{q}$. 

To verify this, I run MCMC....

