# `TimeTraceTools` 
Handling single-molecule time-trace data made easy. 
???+ question 
    Suggestions for a good name are welcome. For now, will stick with `TimeTraceTools`. Will check how to change the name of this repo accordingly. 


**description:** *library for handling and (post-)processing data from high-throughput single-molecule experiments (e.g. magnetic tweezers, TIRF/fluorescence microscopy data).*

## Project layout
    .
    ├── docs/                # markdown files MKdocs website
    ├── public/              # artifact from `mkdocs build` command. GitLab pages needs this directory name
    ├── htmlcov              # coverage reports from `pytest --cov`
    ├── src             # All Python code is in this 'source' directory 
    │   ├── data_io 
    │   ├── data_processing
    │   └── data_types
    ├── tests           # The `tests/` directory contains all the unit tests (`pytest`) code and follows the same structure as the corresponding `src/` directory. 
    │   ├── data_io
    │   ├── data_processing
    │   └── data_types
    ├── mkdocs.yml.     # settings for MKdocs site 
    ├── pyproject.toml  # Python project/environment management 
    ├── uv.lock         # Python dependencies `uv`
    └── README.md       # README as seen on Gitlab page 


