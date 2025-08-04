# `TimeTraceTools` 
A Python library that makes handling single-molecule time-trace data easy.


## Project layout
    
    .
    ├── README.md           # README.md as displayed on GitLab 
    ├── pyproject.toml      # Python project/environment management 
    ├── uv.lock             # Python project/environment management: Created by `uv` 
    ├── .gitlab-ci.yml      # Gitlab actions CI/CD
    ├── .vscode           
    │   ├── extensions.json # Recommended VScode extensions 
    │   └── settings.json   # Recommended VScode settings 
    ├── docs                # Content of MKdocs documentation website 
    │    └── ...            # Markdown (`.md`) files     
    ├── mkdocs.yml          # settings for MKdocs site 
    ├── htmlcov             # coverage reports from `pytest --cov`
    ├── src                 # All Python code is in this 'source' directory 
    │   ├── time_trace_tools  # Nested structure to unify imports from any directory (always `import time_trace_tools`)
    │   ├── __init__.py 
    │   ├── data_io
    │   │   └── ...         # `.py` files in here 
    │   ├── data_processing
    │   │   └── ...         # `.py` files in here 
    │   └── data_types
    │       └── ...         # `.py` files in here 
    └── tests                   # Unit tests (`pytest`) code. Follows the same structure as the corresponding `src/` directory. 
        ├── __init__.py
        ├── data_io
        │   └── ...
        ├── data_processing
        │   └── ...
        └── data_types
            └── ...

