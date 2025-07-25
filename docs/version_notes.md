# [1.0.0] - 2025-07-25
First version with all essential stuff working (woohoooo!). All features can be seen as documentation on this website. For future versions, this page can be used to specify the updates done. 


# [0.1.0] - 2025-02-15
First set of functional code to be released and that can be imported / used as dependency in your own project.
"Version 0" used to indicate things are still a work in progress.  

<span style = "color:indianred">**NOTE: packages/modules not mentioned in this changelog are likely not implemented yet and not intended to be used yet ;-) **</span>

## new features
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