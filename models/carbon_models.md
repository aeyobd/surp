# Carbon Models

To reproduce the models in the carbon paper, we need to run the following full MW models.

- `fiducial/run` This is the fiducial model used in most plots. f=0.3 fruitty AGB
- `fruity/zeta_lower`
- `fruity/zeta_higher`
- `fruity/f_0`
- `fruity/f_0.5`
- `fruity/fz_0`
- `fruity/fz_0.5`

- `fruity/best`
- `aton/run`
- `monash/run`
- `nugrid/run`
- `fruity/agb_mass_0.7_alpha`

- `fruity/agb_mass_0.5`
- `fruity/agb_mass_0.7_fixed`
- `fruity/agb_mass_1.5`

- `fiducial/lateburst`
- `fiducial/twoinfall`
- `fiducial/eta2`


Then, for the last section and to derive the parameters for these models, we run the following setup models for the MCMC analysis
- `perturbations/linear`
- `perturbations/constant`
- `perturbations/fruity`
- `perturbations/aton`
- `perturbations/monash`
- `perturbations/nugrid`
- `perturbations/fruity_mf0.7`

- `multi_perturbations/lateburst`
- `multi_perturbations/twoinfall`
- `multi_perturbations/eta2`
- `multi_perturbations/sneia_1.2`


And the associated MCMC models
- `mcmc_models_2d/fiducial`
- `mcmc_models_2d/fiducial_constrained`
- `mcmc_models_2d/aton`
- `mcmc_models_2d/nugrid`
- `mcmc_models_2d/monash`
- `mcmc_models_2d/fruity_mf0.7`

- `mcmc_models_2d/fiducial_sigma0.05`
- `mcmc_models_2d/aton_sigma0.05`
- `mcmc_models_2d/nugrid_sigma0.05`
- `mcmc_models_2d/monash_sigma0.05`
- `mcmc_models_2d/fruity_mf0.7_sigma0.05`

- `mcmc_models_2d/lateburst`
- `mcmc_models_2d/twoinfall`
- `mcmc_models_2d/eta2`
- `mcmc_models_2d/sneia_1.2`

Once these models are run, the parameters are derived from the notebook `carbon_paper/mcmc_samples.ipynb` which collects and reports the derived parameters. 



## Tests
We also have a number of tests to validate that the conclusions are robust.

