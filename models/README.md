# Models


This directory contains the models I have used in my carbon paper. 
Each model is specified by a params.toml and a yield_params.toml file inside a seperate directory.
params.toml and yield_params.toml files can inherit other files, so all models inherit these files from the files in the `fiducial` directory. Additionally, models in subdirectories other than `fiducial` should inherit their parent directories parameterfiles. 

To run a model, in this directory (`surp/models`) run the command

```bash
run.sh path/to/model
```


