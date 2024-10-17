# Perturbative analysis

The goal of these models is to determine the GCE evolution for each yield component individually so that we can exploit the linearity of the yield equations and determine estimates for permissible combinations of yields.

The assumptions used here are 
- SFH is fixed (and other yield scale/etc parameters). As demonstrated by the more precise models, this is likely an adequate assumption
- Metallicity evolution is fixed. To approximate this, we scale down all the used yields by a factor of 1e-3 and only change the yields of "ag" so that the total metallicity remains approximantly unchanged. 
- Yields are linear. SOme changes of yields are not linear in detail.



Models here are
- Unchanged AGB models (fruity, etc.) these models only contain the agb production of c
- constant CCSNe yield
- piecewise linear ccsne (with transition at $[M/H] = 0$)
- zero: sanity check that unchanged yields will not affect anything.
