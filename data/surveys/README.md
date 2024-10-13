# Data Files

## Desi
Desi takes spectra of R ~ 2000 to 4000.

As of now, we only have access to the desi EDR1. https://data.desi.lbl.gov/doc/releases/edr/vac/mws/.
I use the mwsall-pix-fuji.fits file, which contains all of the data. In HDU2, the elemental abundances for Fe, Ca, C, Mg in \[elem/H\](in order) are provided. There are also columns for FEH, ALPHAFE, LOG10MICRO, TEFF, LOGG (also stored in PARAM), with covariances in COVAR.

