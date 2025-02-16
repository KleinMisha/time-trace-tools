# Changelog 
This file will keep track of all release-notes. 

**semantic versioning: version `MAJOR.MINOR.PATCH` indicates:
- The first number (say `v1.0.0`) indicates the major release. We only update this version when we make changes that could potentially break code that imports `v1.0.0`. That is, if you change the required arguments of an existing function or even remove a function entirely, then update the major version. This way, packages using `v1.0.0` can still use the old version of the code without problem. 
- The second number indicates the minor version (say, `v1.1.0` ). Could be used if you introduce new functionality that cannot break existing code. For instance, if you add a feature that uses some optional function argument. Now calls without this optional argument do not result in an error at run time. 
- the final number indicates a small bug fix (say `v1.1.1`). No real new features added, but just some bug is fixed.

(Typically, if my code uses `pytweezers_tools version 1`, I would want to use it up to the latest minor version and patch. 




## [0.1.0] - 2025-02-15
First set of functional code to be released and that can be imported / used as dependency in your own project.
"Version 0" used to indicate things are still a work in progress.  

<span style = "color:indianred">**NOTE: packages/modules not mentioned in this changelog are likely not implemented yet and not intended to be used yet ;-) **</span>

### new features
packages available / minimally operational
- `data_io`
_Package containing all functions need to read (and in the future write) experimental data_ 
    - `raw_mt.py` to handle raw data from magnetic tweezers (pytweezers format)
    - `magnet_script.py` to handle/parse the magnet script used to control the magnet's motors 
    - `labview_legacy.py` to load the raw data / magnet script from LabView (legacy format). Also can convert the current format to old format (if needed for backwards-compatibility)

- `data_types`
_Package with internal data representations. Convenient ways of handling (collections of) traces in your code._ 
    - Abstractions: `TimeTrace`, `Experiment` 
    - Specific implementations: `MagneticTweezersTrace`, `MagneticTweezersExperiment`

### other components included 
- `.vscode` directory with `settings.json` and `extensions.json`. For `VS code` users: some nice extensions to have autoformatting using `ruff`, a spell checker (US-english), and more. 
- `README.md` with first basic installation instructions and description of the available code 
- `environment.yml` : `conda` environment specifications
- `uv.lock` and `pyproject.toml` : to manage dependencies with `uv`. **NOTE: mainly included to allow other, independent, python projects install this project as a dependency. For stand-alone usage `conda` should still work fine. Will figure out what we use to manage dependencies in the future** 


