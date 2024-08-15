# Models


This directory contains the models I have used in my carbon paper. 
Each model is specified by a `params.toml` and a `yield_params.toml` file inside a separate directory.
`params.toml` and `yield_params.toml` files can inherit other files, so all models inherit these files from the files in the `fiducial` directory. Additionally, models in subdirectories other than `fiducial` should inherit their parent directories parameter-files. 

To run a model, in this directory (`surp/models`) run the command

```bash
bash run.sh path/to/model
```

where `path/to/model` is the path to the model directory. `run.sh` searches for a `run.py` file in the model directory, the parent directory, or defaults to this directory. Overriding `run.py` allows for more flexibility than the static parameter-files.

There is also a thin wrapper `run_nohup.sh` which runs the model in the background. 

## Core scripts

`run.py`. This script takes two arguments, paths to the `params.toml` and `yield_params.toml` files. `run.py` loads the parameters from these files, runs the model, and saves the output to a file in the present directory. This creates a `milkyway.vice` file and a `model.json` file.


`visualize.py` contains code to create the most basic plots of the model. 



