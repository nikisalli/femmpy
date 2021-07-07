# femmpy
femmpy is a python wrapper and geometry generator for xfemm, written as an alternative to pyfemm for anyone who doesn't want to use windows

# requirements
- install xfemm from [here](https://github.com/REOptimize-Systems/xfemm)
- make sure "fmesher" and "fsolver" are installed and accessible from your system! please note that this may require you to manually copy these files to your /usr/local/bin after compiling them!

# installation
- run  ```python setup.py install```

# usage
just check the provided example

# TODO
- add more methods to generate shapes
- better mesher and solver handling
- support for axial simulations (only cartesian supported for now)
- support for other kinds of simulations (this package currently supports cartesian magnetostatic problems only)