# Installation
Dependencies are manged using `uv` ([uv website for installation instructions](https://docs.astral.sh/uv/)): This is much faster, and more easy to use than `pip` or `conda`. It is also based on using the more modern setup with a `pyproject.toml` file. Dependencies, and other project details, are listed in the `pyproject.toml` file. Dependency managers like `uv` use the `uv.lock` file to specify specific versions of packages used.

???+ tip 

    To use the code, you do not need to clone this repository. If not developing the code, it is recommended to simply list this GitLab repository as a dependency. That way you can import everything within this package in your own code and use it like any other library.


## Users (non-developers). 
To include this library as one of the dependencies for your own project ***you do not need to clone this repository***. Instead, simply add the following into your `pyproject.toml`. 

```TOML
[tool.uv.sources]
pytweezer_tools = { git = 'ssh://git@gitlab.com/DulinlabVU/time-trace-tools.git', tag = <VERSION TAG>}
```

???+ tip 
    replace ```<VERSION TAG>``` with the version of choice for maximum reproducibility of your code



Next, run 

```zsh
uv run python your_python_script.py
```
to let `uv` take care of building/installing all required packages into a `.venv/` directory before running your code. 
(subsequent runs will be a bit faster as the `uv.lock` keeps a cache of the already build/installed packages)

## Developers
Once `uv` is installed, you can setup your `.venv`(will be created inside your current folder) with all requirements installed using

### using `uv`

```bash 
uv venv create 
uv pip sync -d 
```

???+ note 
    use the `-d` tag to also install tools needed for development such as `pytest`(not included as a strict dependency as the code can be executed without of course needed for development). 




## VS-code setup
For VS-code users, this repository contains a `.vscode` directory. 
- `.vscode/settings.json` contains all IDE settings, including those for typechecking, pytest, spell checking, and more. 
- `.vscode/extensions.json` lists all recommended extensions used.  You should be able to install these with one click of the button in the Marketplace. There should be a button to instantly install all the recommended extensions. (extensions include: `ruff` for code formatting, a spell checker that understands snake_case and CamelCase, viewing YAML/TOML files, making `mermaid` diagrams in markdown, and more.)
