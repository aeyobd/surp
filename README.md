# SURP
This is a collection of scripts, jupyter notebooks, and the source files for my research thesis. 

## Requirements

To build (pip should take care of these)
- Python 3.11
- numpy
- cython
- meson-python

Other main dependencies
- my vice fork (https://github.com/aeyobd/VICE) on branch `develop`. Needs cython 3.0 to install but seems to install well. Install with `python setup.py build install` as pip seems to break things in VICE :/.
- pandas 
- toml
- pydantic

Optional dependencies to run all notebooks
- latest version of arya (matplotlib style files)
- matplotlib
- seaborn (for contour / scatter plots)
- molmass
- astropy
- scipy


## Installing the library
Recommended to install with
```bash
python -m pip install --no-build-isolation --editable .
```
because I have not figured out datafiles fully.

which depends on `meson-python`, `ninja`, and `meson` python packages being installed. 

## Running models
A model runs in about 10 minutes on a single core with about 4 GB of RAM (storing many star particles).
All models are in the directory `models`.
To run a model, navigate to the `models` directory and run the script. 
```bash
./run_nohub.sh <DIRNAME>
```
where `<DIRNAME>` is the name of the directory containing the model.
See `models/README.md` for more information on the structure and all.

Each model contains several outputs
- `model.json` A plaintext (sory) json containing several subcomponents: Stars.
- `stars.csv` a CSV file meant to replicate APOGEE solar observations from the model.
- `milkyway.vice` the full VICE output
- other files such as migration files specified optionally in params.



### Model configuration
See the documentation on MWParams and YieldParams in the package to understand encoded options. Broadly most components of the vice models are stored in two files: `params.toml` and `yield_params.toml` in each model directory. If you would like additional or more active configuration, overload the `run.py` script and add new options there.

In general there are options for changing relevant yields, and star formation histories and yield/scales. 


