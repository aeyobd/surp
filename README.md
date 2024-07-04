# SURP
This is a collection of scripts, jupyter notebooks, and the source files for my research thesis. 

## Requirements
- Python 3.11
- my vice fork (https://github.com/aeyobd/VICE) on branch `new_yields`. Needs cython 3.0 to install but seems to install well.
- latest version of arya (matplotlib style files)
- numpy, scipy, astropy, matplotlib
- pandas 
- seaborn (for contour / scatter plots)
- molmass
- hatch (build requirement)



## Installing the library
To install surp, run 
```bash
python setup.py build_ext --inplace
pip install -e .
```

if there are issues with running the mod

## Running models
A model runs in about 10 minutes on a single core with about 4 GB of RAM (storing many star particles).
All models are in the directory 'models/'. 
To run a model, navigate to the directory and run the script. 
```bash
./run.sh <DIRNAME>
```
where `<DIRNAME>` is the name of the directory containing the model.


## Outputs
Each model contains several outputs
- `model.json` A plaintext (sory) json containing several subcomponents: Stars.
- `stars.csv` a CSV file meant to replicate APOGEE solar observations from the model.
- `milkyway.vice` the full VICE output
- other files such as migration files specified optionally in params.



## Configuration
See the documentation on MWParams and YieldParams in the package to understand encoded options. Broadly most components of the vice models are stored in two files: `params.toml` and `yield_params.tom` in each model directory. If you would like additional or more active configuration, overload the `run.py` script and add new options there.

In general there are options for changing relevant yields, and star formation histories and yield/scales. 


