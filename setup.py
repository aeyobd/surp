from setuptools import setup
import numpy as np
from Cython.Build import cythonize

setup(
    name="surp",
    packages=["surp", "surp.simulation"],
    ext_modules = cythonize("surp/yield_models.pyx", annotate=True),
    include_dirs=[np.get_include()],
)
