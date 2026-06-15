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
1/\omega = \tau_{\rm dep} = \frac{\tau_\star}{1+\eta - r}
$$
using $\tau_\star = M_g / \dot{M}_\star$, the above differential equation can be rewritten as
$$
\dot{M}_{X} + \omega M_{X} = \lang \dot{m}_{X} \rang_\star
$$
To solve this equation, we can use that a differential equation of the form $\dot{M} + p(t) M = f(t)$ is solved with
$$
M(t) = \frac{1}{\mu} \left[ \int_0^t \mu(t')\, f(t')\ dt' + C\right]
$$
where $\mu(t) = \exp{\int p(t)\ dt}$ . In our case, $p(t) = \omega$, so $\mu(t) = \xi(-\omega t)$, and $f(t) = \dot{M}_\star \langle y_X\rangle$. We can find $M_C(t)$ with
$$
M_{X}(t) =  \xi(\omega t) \int_0^t \xi(-\omega t')\ \langle \dot{m}_{X} \rangle(t') \ dt'
$$

(Where we have assumed $M_0=0$ implying $C=0$ this can be easily relaxed.)  In terms of metallicity
$$
Z_X(t) = \frac{\xi(\omega t)}{M_g(t)} \int_0^t \xi(-\omega t')\;\langle \dot{m}_X \rangle (t')\; dt'
$$


So, to solve these equations, we first integrate to find $\langle \dot{M}_X \rangle $ and then integrate to solve for the ISM mass $M_X(t)$ and finally divide by the gas mass (given by the SFH) to find $Z_X(t)$. 

For CCSNe, $\lang \dot{m}_{X} \rang_\star = y_{X}\ \dot{M}_\star $ since $R(t) \approx \delta(t)$, so the equation tends to be much simpler.

## Convenience definitions

I have defined the following functions and variables to make later expressions much easier to work with. Firstly, 
$$
\xi(x) \equiv e^{-x}\\
\xi^i(x) = x^i\,e^{-x}
$$
As helpers, we will need
$$
p_i = i!
$$
and
$$
c_{i, j} = \frac{p_i}{p_j p_{i-j}}
$$
which represents the combination i choose j.

### Properties of poly-exponentials


$$
\xi(x)\xi(y) = \xi(x+y)
$$

$$
\xi^i(x) \xi^j(y) =\frac{x^iy^j}{(x+y)^{i+j}} \xi^{i+j}(x+y)
$$

$$
\xi^i(x+y) = \sum_j^i c_{i,j}\,x^iy^{j-i}\xi(x)\xi(y)
$$



The derivative is then 
$$
\frac{d}{dx} \xi^n(ax) = -a\xi^n(x) - a\,n\xi^{n-1}(x)\\
\frac{d}{dx} \xi(ax) = -a\xi(ax)
$$
From these derivatives, a hint at the form of the integral is from the first expression, i.e. if $\Xi$ is the integral $\int \Xi^i dx$, then $\Xi$ satisfies
$$
\Xi^{n}(x) = -\xi^n(x) + n\, \Xi^{n-1}(x)
$$
but we know that 
$$
\Xi^0(ax) = - \frac{1}{a} \xi(ax)
$$
so that
$$
\Xi^n(ax) = -\frac{1}{a} \sum_{i=0}^n \frac{p_n}{p_i}\, \xi^i(ax)
$$




## AGB Model



For C abundances, a reasonable approximation of the DTD is
$$
R(t) = R_0\,\xi^\gamma(\alpha\,\Delta t) ;\quad 0 < \Delta t < t_{\rm max}
$$
where $\alpha = 1/\tau_{\rm agb}$ is the characteristic AGB frequency, $\Delta t = t - t_D$ is the time after some initial delay, and $t_{\rm max}$ is the maximum timescale for AGB production (or minimum mass of stars producing AGB enrichment).  I find that $\gamma=2$ provides a reasonable approximation to the AGB tables.

We can transform this DTD into a stellar mass enrichment distribution. Since the mass of some yield ejected into the ISM from AGB stars is given by
$$
\dot{M}_{X} = -\xi \, Y_X(m(t), Z)\, M_\star\,\dot h
$$
where $\xi$ is the entrainment fraction (portion of the yield retained by the ISM), $Y$ is the individual stellar yield at a mass and metallicity, $m(t)$ is the mass with a lifetime $t$, and $\dot h$ is the derivative of the (post)-main-sequence-mass-fraction (pMSMF) . The pMSMF is given by
$$
 h(t) = \frac{\int_l^{m(t)} m \frac{dN}{dm}dm}{\int_l^u m \frac{dN}{dm}dm}
$$
If we let $\mathcal I(m) = \frac{dN}{dm} / \int_l^u m \frac{dN}{dm} dm$ be the normalized IMF, then $h = \int_l^{m(t)} m\, \mathcal I \ dm$ and 
$$
\dot h(t) = m \,\mathcal I(m) \, \dot m
$$
where all the $m$ are in fact $m(t)$. For the larson1974 MLR, $\dot m$ is 
$$
\dot m_{\rm larson1974} = -\frac{m}{t} \frac{1}{\sqrt{\beta^2 - 4\gamma (\alpha - \log t + \log(1+pMS))}}
$$
where we have added a correction term for the use of the post-Main sequence MLR. 

Since $R(t)$ is proportional to $\dot M_X$, i.e. $R(t)\, y(Z) = \dot M_X / M_\star$, assuming that $\xi_X = 1$ and that $R(t)$ is normalized. As a result, $ Y_X (m, Z) = R(t) y(Z) / \dot h$. We can further simplify and assume $Y_X(m, Z) = S(m) y(Z)$ so that $S(m)$ isolates the mass dependence of the yield. Then
$$
S(m) \equiv Y_X(m, Z) / y(Z)= \frac{R(t)}{\dot h} = \frac{R(t(m))}{m\,\dot m(t(m))\,\mathcal I (m)}
$$


# Equilibrium

### Constant SFH

In the event that $\dot{M}_\star$ is constant, then, $\langle \dot{m}_X\rangle_\star = m_x = y_X \dot{M}_\star$ for any process (as they are all time-independent), so that if the system evolves to reach equilibrium, the equilibrium value of $Z_X$ (found by setting $\dot{M}_X$ to zero above) is given by
$$
Z_{X,\;\rm Eq(cosnt)} = \frac{y_X}{1+\eta - r} = \frac{y_X}{\tau_\star \omega}
$$

### Exponential SFH

However, in the case that $\dot{M}_\star$ is exponential, equilibrium becomes more complex, depending on the rate of star formation decline. Because the gas mass is now $M_g = M_{g, 0} \exp(-t/\tau_{\rm sfh})$, we can rewrite the above evolution equation in terms of 
$$
Z_{X, \rm eq} = \frac{\langle y_X \rangle_\star}{1 + \eta - r - \tau_\star / \tau_{\rm sfh}} = \frac{\langle y \rangle}{\tau_\star (\omega - \phi)}
$$

 For instance, the mean yield of sneia Fe in our prescription is given by
$$
\nu_{\rm Fe}^{\rm Ia} = \frac{\int_0^t \dot{M}_\star(t') R(t-t') dt'}{\dot{M}_\star\int_0^\infty R(t') dt'}
$$
For the exponential delay time distribution, 
$$
\nu_{\rm Fe}^{\rm Ia} = \frac{\iota}{\iota - \phi} \xi(-\phi\;t_D) (1 - \xi((\iota - \phi)\Delta	t))
$$


And for AGB stars (the most complex of all of them)
$$
\nu_{\rm X}^{\rm AGB} = \frac{\int_0^t Y_X^{\rm AGB}(m_{\rm AGB}(t-t'), Z(t')) \dot{M_\star}(t') \dot{h}(t-t') dt'
}{
y_{X}^{\rm AGB} \dot{M}_\star }
$$
where $\dot h$ is as above.

# Constant SFH

Constant star formation history is expressed as simply $M_{\rm gas}(t) = M_0$, which is the simplist case.

## Constant CCSNe 

Most directly applicable to O and Mg, and a good approximation for $Z$. $y(Z) = y_0$. 
$$
Z_{\rm Mg} = Z_{\rm Mg}^{\rm eq} \left[ 1 - \xi(\omega t)\right]
$$


where 
$$
Z_{\rm Mg}^{\rm eq} = \frac{y_{\rm Mg}}{\tau_\star\, \omega} = \frac{y_{\rm Mg}}{1 + \eta - r}
$$


## Linear Z CCSNe 

Say that a yield is linearly dependent on $Z$, i.e.
$$
y(Z) = \zeta\,Z
$$
We know what $Z$ is from above, we know $y(t)$ and can integrate over this, using that $Z(t) \approx Z_{\rm Mg}\  Z_\odot / Z_{\rm Mg,\ \odot} = \frac{y_{\rm Mg} Z_\odot}{\tau_\star\,\omega Z_{\rm Mg,\ \odot}}(1 - \xi(\omega t))$ 
$$
y(t) = y(Z(t)) = \zeta' (1 - \xi(\omega t))
$$
where we have defined $\zeta' \equiv \zeta y_{\rm Mg} Z_{\odot} / (\tau_\star \omega Z_{\rm Mg,\,\odot})$. Since addition is separable, the first term of $y(t)$ evaluates to the constant Z solution above, and the second term is
$$
Z_{\rm C,\,lin}(t) = - \frac{\zeta'}{\tau_\star}\ t\,\xi(\omega t)
$$
so the metallicity dependent yield in total is 
$$
Z_{\rm C}(t) = Z_{\rm C}^{\rm eq} (\zeta' + y_{\rm C, 0})( 1 - \xi(\omega(t))) - \zeta' \frac{t}{\tau_\star}\,\xi(\omega\,t)
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
Z_{\rm Fe}^{\rm Ia}(t) = \frac{y^{\rm Ia}}{\tau_\star\,\omega} \left[1 - \frac{\iota}{\iota - \omega} \xi(\omega\,\Delta t) + \frac{\omega}{\iota - \omega} \xi(\iota\,\Delta t)\right]
$$


## SNe Ia (plaw)

In the analytically tractable special case that $R \sim t^{-1}$, the integrals can be evaluated in terms of the Exponential Integral ${\rm Ei}(t) = \int_{-\infty}^t \exp (t)\ dt / t$.

The one issue is that $R$ is no longer normalizable, but I just leave that factor out for now. The resulting formula is
$$
Z_{\rm Fe}^{\rm Ia}(t) = Z_{\rm Fe}^{\rm Ia,\,eq} \left[\log t/t_D - \xi(\omega\,t) ({\rm Ei}(\omega\,t) - {\rm Ei}(\omega\,t_D) \right]
$$

## AGB

For a constant SFH and $\gamma=2$, 
$$
\langle \dot m \rangle =y \dot M_\star  \int_0^t \xi^2(\alpha (t - t' - t_D)) \theta(t - t' - t_D)dt' \\
= \frac{y \dot M_\star}{\alpha} 
\left[2 - \xi^2(\alpha \Delta t) - 2 \xi^1(\alpha\Delta t) - 2\xi^0(\alpha\Delta t)\right]
$$


where $\Delta t$ is assumed to be positive.

We can then rewrite the integral (in terms of $\Delta t$)
$$
Z_C^{\rm AGB}(t) = 
\frac{y \dot M_\star}{M_0 \alpha} \xi(\omega t) \int_0^{\Delta t}
\xi(-\omega t' - \omega t_D) \left[2 - \xi^2(\alpha t') - 2\xi^1(\alpha t') - 2\xi^0(\alpha t')\right]
\ dt'
$$


We can derive the expression
$$
Z_{\rm C}^{\rm AGB}(t) = \frac{y}{\tau_\star \omega} \frac{R_0}{\alpha} \left[2 - 2\xi(\omega\Delta t) + 2(k-1)(k^2+k+1)[\xi(\alpha\Delta t) - \xi(\omega \Delta t)]
+ 2(k-1)(k+1)\xi^1(\alpha \Delta t) + (k-1)\xi^2(\alpha \Delta t)
\right]
$$
where we have defined $k = \alpha / (\alpha - \omega)$. 

For $\gamma=1$, similarly, we can derive:

$$
Z_{\rm C}^{\rm AGB}(t) = y_{\rm C}^{\rm AGB}/\tau_\star \left(
\frac{1}{\omega} + \frac{1}{\alpha  - \omega}\,\xi^1(\alpha\,\delta t) + \frac{2\alpha - \omega}{(\alpha - \omega)^2}\,\xi(\alpha\,\delta t) - \frac{1}{\omega} \xi(\omega\,\delta t) - \frac{2\alpha - \omega}{(\alpha - \omega)^2} \xi(\omega\, \delta t)
\right)
$$


# Exponential SFH

Assume that $\dot{M}_\star \propto \xi(\phi t) = \exp(-t/\tau_{\rm sfh}) = \xi(\phi t)$. 

## CCSNe

$$
Z_X^{\rm CC}(t) = Z_{X, \rm Eq(exp)}^{\rm CC} \left[1 - \xi(\omega t - \phi t)\right]
$$

which looks the same as for a constant SFH except with an increase on the depletion timescale.

## SneIa (exp)


$$
Z^{\rm Ia}(t) = Z_X^{\rm eq, exp} \left[
1 - \frac{\omega - \phi}{\omega - \iota}
\xi((\iota - \phi)\Delta  t) 
- \left(1 - \frac{\omega - \phi}{\omega - \iota} \right)
\xi((\omega - \phi)\Delta  t)
\right]
$$
where 
$$
Z_{X}^{\rm eq, exp} = \frac{y}{\tau_\star (\omega - \phi)} \frac{\iota}{\iota - \phi} \xi(-\phi\;t_d)
$$
is the limit of the time-dependent equilibrium expression above.







# Arbitrary solutions

For a fairly large class of functions, the exact solution for a metallicity independent yield is analytic. 

Let the star formation history be a poly-exponential function:
$$
\dot M_\star = M_g / \tau_\star = \sum_n s_n\,\xi^{i_n}(\phi_n t)
$$
(more complex SFR laws likely wreck havock, todo explore this in more detail...). 

Assuming a CCSNe yield (i.e. $R(t) = \delta(t)$), then $\langle \dot m_A \rangle_\star = \dot M_\star y_A$, and we need to solve the integral
$$
Z_A(t) = \frac{\xi(\omega t)}{M_g(t)} \int_0^t \xi(-\omega t) \dot M_\star y_A \ dt
$$
The sum for the SFH can be brought outside so that this is
$$
= \frac{y_A\xi(\omega t)}{M_g} \sum_n s_n \int_0^t \xi(-\omega t) \xi^{i_n}(\phi_n t) dt 
$$
Using the multiplication identity above and defining $k_n= \phi_n / (\phi_n - \omega)$, 
$$
= \ldots {k_n}^{i_n} \int_0^t  \xi^{i_n}((\phi_n-\omega) t) \ dt\\
= \ldots \ldots \left[
+\frac{1}{\omega -\phi_n }\sum_{j=0}^{i_n} \frac{i_n!}{j!} \xi^j((\phi_n - \omega)t)
\right]_0^t
$$
The only term in the sum that is nonzero at $t=0$ is when $j=0$, so we have our result (after factoring out some terms and adding back all the coefficients)
$$
Z_A(t) = \frac{y_A}{M_g(t)}
\sum_n \frac{S_n\, {k_n}^{i_n} }{\omega - \phi_n}
\left[-i_n!\ \xi(\omega t) 
+ \sum_{j=1}^{i_n} \frac{i_n!}{j!}{k_n}^{-j}\ \xi^j(\phi_nt)

\right]
$$
Note that if $e^{-at}$ times a function is integrable, this derivation can be done for that SFH. Additionally, the formula for $M_g$ only appears outside the integral so we do not need to make an assumption about the SFR law. In essence, metallicity-independent CCSNe yields are likely analytic for common functions. The last sum can be reduced to incomplete gamma functions but this is likely not more useful for our cases. 



In the special case that the SFH sum has exactly one component (even a sum of two plain exponentials causes trouble...) and the SFR is a linear relationship, then, we can simplify the above to remove the nonlinear $1/M_g(t)$ 
$$
Z_A(t) = \frac{y}{\tau_\star (\omega - \phi)} i!\, k^i\left[-\frac{\xi((\omega-\phi))}{\phi^i t^i } + \sum_{j=0}^i \frac{1}{j!} k^{-j} \frac{1}{\phi^{i-j} t^{i-j}}\right] \\
= \frac{y}{\tau_\star (\omega - \phi)} \frac{1}{(\phi - \omega)^i \, t^i} \left[
-i!\,\xi((\omega - \phi)t) + \sum_{j=0}^i \frac{i!}{j!} (\phi - \omega)^j t^j
\right]
$$

The latter expression correctly reduces to Eq. 56 in WAF for $i=1$. 

### Delayed

We can then extend this argument to arbitrary DTDs! If the DTD of the 





## Metallicity Dependence



As is hinted at by the expessions above, even a linear dependence on metallicity is much more challenging to resolve analytically. 

Say, for example, that a metallicity-independent CCSNe yield $Z_O$ is directly proportional to metallicity. Then, this expression, in general, may be an arbitrary quotent of polyexponential functions. I do not believe this is analytically tractable. Additionally, if there is a delayed component to the metallicity dependence, then the evolution of $Z$, even in the simplest case for a constant SFH, is a sum of two different exponential functions. I do not believe this is analytically integrable either unless the frequencies are an integer ratio. Maybe other basis functions may make this problem easier but for now I do not know.

As such, the only cases we can reasonable consider are the single-component SFH for a metallicity-independent CCSNe yield proxy. This derivation furthermore requires introduction of exponential integrals unless the SFH is a simple constant or exponential function.



