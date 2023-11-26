import math as m
import numbers
from ..._globals import MAX_SF_RADIUS, END_TIME, M_STAR_MW


_THIN_DISK_SCALE_RADIUS_ = 2.5 # kpc
_THICK_DISK_SCALE_RADIUS_ = 2.0 # kpc
_THICK_TO_THIN_RATIO_ = 0.27 # at r = 0



def get_bin_number(bins, value):
	r"""
	Obtain the bin number of a given value in an array-like object of bin
	edges.

	Parameters
	----------
	bins : array-like
		The bin-edges themselves. Assumed to be sorted from least to greatest.
	value : real number
		The value to obtain the bin number for.

	Returns
	-------
	x : int
		The bin number of ``value`` in the array ``bins``. -1 if the value
		lies outside the extent of the bins.
	"""
	for i in range(len(bins) - 1):
		if bins[i] <= value <= bins[i + 1]: return i
	return -1



def interpolate(x1, y1, x2, y2, x):
	r"""
	Extrapolate a y-coordinate for a given x-coordinate from a line defined
	by two points (x1, y1) and (x2, y2) in arbitrary units.

	Parameters
	----------
	x1 : real number
		The x-coordinate of the first point.
	y1 : real number
		The y-coordinate of the first point.
	x2 : real number
		The x-coordinate of the second point.
	y2 : real number
		The y-coordinate of the second point.
	x : real number
		The x-coordinate to extrapolate a y-coordinate for.

	Returns
	-------
	y : real number
		The y-coordinate such that the point (x, y) lies on the line defined
		by the points (x1, y1) and (x2, y2).
	"""
	return (y2 - y1) / (x2 - x1) * (x - x1) + y1






def timescale(radius, Re = 5):
    r"""
    Determine the timescale of star formation at a given radius reported
    by Sanchez (2020) [1]_.

    Parameters
    ----------
    radius : real number
        Galactocentric radius in kpc.
    Re : real number [default : 5]
        The effective radius (i.e. half-mass radius) of the galaxy in kpc.

    Returns
    -------
    tau_sfh : real number
        The e-folding timescale of the star formation history at that
        radius. The detailed time-dependence on the star formation history
        has the following form:

        .. math:: \dot{M}_\star \sim
            (1 - e^{-t / \tau_\text{rise}})e^{-t / \tau_\text{sfh}}

        where :math:`\tau_\text{rise}` = 2 Gyr and :math:`\tau_\text{sfh}`
        is the value returned by this function.

    .. [1] Sanchez (2020), ARA&A, 58, 99
    """
    radius /= Re # convert to units of Re
    radii, timescales = _read_sanchez_data()
    idx = get_bin_number(radii, radius)
    if idx != -1:
        return interpolate(radii[idx], timescales[idx], radii[idx + 1],
            timescales[idx + 1], radius) 
    else:
        return interpolate(radii[-2], timescales[-2], radii[-1],
            timescales[-1], radius) 


def _read_sanchez_data():
	r"""
	Reads the Sanchez (2020) [1]_ star formation timescale data.

	Returns
	-------
	radii : list
		Radius in units of the effective radius :math:`R_e` (i.e. the
		half-mass radius).
	timescales : list
		The star formation timescales in Gyr associated with each effective
		radius.

	.. [1] Sanchez (2020), ARA&A, 58, 99
	"""
	radii = []
	timescales = []

	# This function likely won't be called from this directory -> full path
	with open("%s/sanchez_tau_sfh.dat" % (
		os.path.abspath(os.path.dirname(__file__))), 'r') as f:

		line = f.readline()
		
		# read past the header
		while line[0] == '#':
			line = f.readline()

		# pull in each line until end of file is reached
		while line != "":
			line = [float(i) for i in line.split()]
			radii.append(line[0])
			timescales.append(line[1])
			line = f.readline()

		f.close()
	return [radii, timescales]


def normalize(time_dependence, radial_gradient, radius, dt = 0.01, dr = 0.5,
	recycling = 0.4):
	r"""
	Determine the prefactor on the surface density of star formation as a
	function of time as described in Appendix A of Johnson et al. (2021).

	Parameters
	----------
	time_dependence : <function>
		A function accepting time in Gyr and galactocentric radius in kpc, in
		that order, specifying the time-dependence of the star formation
		history at that radius. Return value assumed to be unitless and
		unnormalized.
	radial_gradient : <function>
		A function accepting galactocentric radius in kpc specifying the
		desired stellar radial surface density gradient at the present day.
		Return value assumed to be unitless and unnormalized.
	radius : real number
		The galactocentric radius to evaluate the normalization at.
	dt : real number [default : 0.01]
		The timestep size in Gyr.
	dr : real number [default : 0.5]
		The width of each annulus in kpc.
	recycling : real number [default : 0.4]
		The instantaneous recycling mass fraction for a single stellar
		population. Default is calculated for the Kroupa IMF [1]_.

	Returns
	-------
	A : real number
		The prefactor on the surface density of star formation at that radius
		such that when used in simulation, the correct total stellar mass with
		the specified radial gradient is produced.

	Notes
	-----
	This function automatically adopts the desired maximum radius of star
	formation, end time of the model, and total stellar mass declared in
	``src/_globals.py``.

	.. [1] Kroupa (2001), MNRAS, 322, 231
	"""

	time_integral = 0
	for i in range(int(END_TIME / dt)):
		time_integral += time_dependence(i * dt) * dt * 1.e9 # yr to Gyr

	radial_integral = 0
	for i in range(int(MAX_SF_RADIUS / dr)):
		radial_integral += radial_gradient(dr * (i + 0.5)) * m.pi * (
			(dr * (i + 1))**2 - (dr * i)**2
		)

	return M_STAR_MW / ((1 - recycling) * radial_integral * time_integral)


def gradient(radius):
	r"""
	The gradient in stellar surface density defined in Bland-Hawthorn &
	Gerhard (2016) [1]_.

	Parameters
	----------
	radius : real number
		Galactocentric radius in kpc.

	Returns
	-------
	sigma : real number
		The radial surface density at that radius defined by the following
		double-exponential profile:

		.. math:: \Sigma_\star(r) = e^{-r/r_t} + Ae^{-r/r_T}

		where :math:`r_t` = 2.5 kpc is the scale radius of the thin disk,
		:math:`r_T` = 2.0 kpc is the scale radius of the thick disk, and
		:math:`A = \Sigma_T / \Sigma_t \approx` 0.27 is the ratio of thick to
		thin disks at :math:`r = 0`.

		.. note:: This gradient is un-normalized.

	.. [1] Bland-Hawthorn & Gerhard (2016), ARA&A, 54, 529
	"""
	return (
		m.exp(-radius / _THIN_DISK_SCALE_RADIUS_) +
		_THICK_TO_THIN_RATIO_ * m.exp(-radius / _THICK_DISK_SCALE_RADIUS_)
	)




