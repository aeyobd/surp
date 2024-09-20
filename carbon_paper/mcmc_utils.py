import emcee
from  scipy import stats
import numpy as np
import matplotlib.pyplot as plt
from corner import corner


class MCMCModel():
    def log_prior(self, theta):
        s = 0
        for i, dist in enumerate(self.distributions):
            s += dist.logpdf(theta[i])

        return s

    def prior_sample(self, N=1):
        return np.array([dist.rvs(size=N) for dist in self.distributions]).T


class Linear(MCMCModel):
    def __init__(self, beta0=(0, 1), beta1=(0, 1), log_sigma=(0, 1)):
        self.distributions = [
            stats.norm(beta0[0], beta0[1]),
            stats.norm(beta1[0], beta1[1]),
            stats.norm(log_sigma[0], log_sigma[1])
        ]

    def __call__(self, x, theta):
        beta0, beta1, log_sigma = theta
        return beta0 + beta1 * x

    def d_dx(self, x, theta):
        return theta[1] + 0 * x

    @property
    def labels(self):
        return [r"$\beta_0$", r"$\beta_1$", r"$\log(\sigma)$"]

class Quadratic(MCMCModel):
    def __init__(self, beta0=(0, 1), beta1=(0, 1), beta2=(0, 1), log_sigma=(0, 1)):
        self.distributions = [
            stats.norm(beta0[0], beta0[1]),
            stats.norm(beta1[0], beta1[1]),
            stats.norm(beta2[0], beta2[1]),
            stats.norm(log_sigma[0], log_sigma[1])
        ]

    def __call__(self, x, theta):
        beta0, beta1, beta2, log_sigma = theta
        return beta0 + beta1 * x + beta2 * x ** 2

    def d_dx(self, x, theta):
        beta0, beta1, beta2, log_sigma = theta
        return beta1 + 2 * beta2 * x

    @property
    def labels(self):
        return [r"$\beta_0$", r"$\beta_1$", r"$\beta_2$", r"$\log(\sigma)$"]


"""
An exponential modeel.
"""
class Exponential(MCMCModel):
    def __init__(self, beta0=(0, 1), beta1=(0, 1), alpha=(1, 4), log_sigma=(0, 1)):
        self.distributions = [
            stats.norm(beta0[0], beta0[1]),
            stats.norm(beta1[0], beta1[1]),
            stats.norm(alpha[0], alpha[1]),
            stats.norm(log_sigma[0], log_sigma[1]),
        ]

    def __call__(self, x, theta):
        beta0, beta1, alpha, log_sigma = theta
        return beta0 + beta1 * np.exp(x * alpha)

    def d_dx(self, x, theta):
        beta0, beta1, alpha, log_sigma = theta
        return beta1 * np.exp(x * alpha)  * alpha

    @property
    def labels(self):
        return [r"$\beta_0$", r"$\beta_1$", r"$\log(\sigma)$", r"$\alpha$"]


def LogLinear(MCMCModel):
    def __init__(self, beta0=(0, 1), beta1=(0, 1), log_sigma=(0, 1)):
        self.distributions = [
            stats.norm(beta0[0], beta0[1]),
            stats.norm(beta1[0], beta1[1]),
            stats.norm(log_sigma[0], log_sigma[1])
        ]

    def __call__(self, x, theta):
        beta0, beta1, log_sigma = theta
        return beta0 + beta1 * np.log(x)

    def d_dx(self, x, theta):
        return theta[1] / x

    @property
    def labels(self):
        return [r"$\beta_0$", r"$\beta_1$", r"$\log(\sigma)$"]



def log_likelihood(theta, model, obs):
    x, y, xerr, yerr = obs
    if xerr is None:
        return log_likelihood_simple(theta, model, x, y)
    else:
        return log_likelihood_uncertanties(theta, model, obs)


def log_likelihood_simple(theta, model, x, y):
    pred = model(x, theta)
    sigma = np.exp(theta[-1])
    return -0.5 * np.sum((y - pred) ** 2 / sigma + np.log(2 * np.pi * sigma))


def log_likelihood_uncertanties(theta, model, obs, verbose=False):
    # ν = 1
    # ll_model = t(df=ν)
    ll_model = stats.norm()
    x_obs, y_obs, x_err, y_err = obs
    sigma = np.exp(theta[-1])
    y_model = model(x_obs, theta)
    m = model.d_dx(x_obs, theta)
    sigma_tot = np.sqrt(y_err**2 + (m**2 * x_err**2) + sigma**2)
    
    z = (y_model - y_obs) / sigma_tot
    ll = np.sum(ll_model.logpdf(z))
    
    return ll


def log_probability(theta, model, obs):
    p = model.log_prior(theta)
    l = log_likelihood(theta, model, obs)
    
    lp = l + p
    return np.where(np.isfinite(lp), lp, -np.inf)




def plot_prior(model, N=1000, nwalkers=10, xlims=(-2, 2), N_lines=100):
    empty_obs = [np.array([]), np.array([]), np.array([]), np.array([])]
    
    p0 = model.prior_sample(nwalkers)
    nwalkers, ndim = p0.shape
    sampler = emcee.EnsembleSampler(nwalkers, ndim, log_probability, args=(model, empty_obs))
    sampler.run_mcmc(p0, N, progress=True);
    samples = sampler.get_chain(discard=200, thin=15, flat=True)
    corner(samples, labels=model.labels);
    print_posterior(model, samples)
    plt.show()

    x_pred = np.linspace(xlims[0], xlims[1], 1000)

    for theta in samples[np.random.randint(len(samples), size=N_lines)]:
        y_pred = model(x_pred, theta)
        plt.plot(x_pred, y_pred, "k", alpha=0.1/np.sqrt(N_lines))


def run_mcmc(model, obs, N=1000, nwalkers=10, discard=200, thin=15):
    p0 = model.prior_sample(nwalkers)
    nwalkers, ndim = p0.shape
    sampler = emcee.EnsembleSampler(nwalkers, ndim, log_probability, args=(model, obs))
    sampler.run_mcmc(p0, N, progress=True);
    samples = sampler.get_chain(discard=discard, thin=thin, flat=True)
    corner(samples, labels=model.labels);
    return samples


def plot_posterior(model, obs, samples, N_lines=100):
    x, y, xerr, yerr = obs
    x_pred = np.linspace(x.min(), x.max(), 1000)

    for theta in samples[np.random.randint(len(samples), size=N_lines)]:
        y_pred = model(x_pred, theta)
        plt.plot(x_pred, y_pred, "k", alpha=0.1/np.sqrt(N_lines))

    plt.errorbar(x, y, xerr=xerr, yerr=yerr, fmt=".", capsize=0)
    print_posterior(model, samples)


def print_posterior(model, samples):
    for i in range(len(model.labels)):
        ps = np.percentile(samples[:, i], [16, 50, 84])
        q = np.diff(ps)
        txt = f"{model.labels[i]} = {ps[1]:.2e} + {q[0]:.2e} - {q[1]:.2e}"
        print(txt)
