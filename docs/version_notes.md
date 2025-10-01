# [1.1.1] - 2025-10-01
* Added methods to expose getting the labels and section labels from a `TimeTrace`. Needed for development of GUI.
* Gitlab CI/CD jobs will run when pushing to the main branch 
  * run pytest 
  * build the documentation website (and deployment on Gitlab pages)
  * a job to bump the version (**manual trigger**)
  
  To trigger the version bump:
  * open the pipeline (click on the checkmark icon next to the latest commit)
  * alternatively: go to "**Build -> Jobs**"
  * the final job will be shown with a grayed out timer icon.
  * click on it, and you will be prompted to provide some arguments
    * key: VERSION_TYPE 
    * value: major | minor | patch (**pick the one that is appropriate**)
  * the job will run and automatically bump the version in the `pyproject.toml` and will create a new version tag with git and push it to this repository.
   

# [1.1.0] - 2025-08-13
Added simple `Experiment` level entry points to set/get the labels (or section labels) for all traces in the experiment.

**NOTE: renamed function `data_types.experiment.Experiment.add_batch_labels_from_dictionary()` to `data_types.experiment.Experiment.set_labels()`**


=== "Labels"

    ```python linenums="1" title="use dictionary mapping trace id's to list of labels" 

        # setting from dictionary 
        new_labels = {
                "trace_1": ["first_label", "second_label"],
                "trace_50": ["second_label", "third_label"],
                "trace_13": ["first_label", "fourth_label"],
            }
        experiment.set_labels(labels=new_labels)

    
        # getting a dictionary 
        all_labels = experiment.get_labels()
    ```


=== "Section Labels"

    ```python linenums="1" title="use dictionary mapping trace id's to dictionary of section labels" 

        # setting from dictionary 
        new_section_labels = {
        "trace_23": {
            (0, 10): ["start", "first_label"],
            (23, 42): ["first_label", "second_label"],
        },
        "trace_45": {
            (32, 60): ["start", "first_label"],
            (75, 80): ["second_label"],
        },
    }
        experiment.set_section_labels(new_section_labels)
    
        # getting a dictionary 
        all_section_labels = experiment.get_section_labels()
    ```

Added reader/writers in `data_io.labels.py`:

```python linenums="1" title="Simple JSON reading/writing"
    from time_trace_tools.data_io.labels import write_experiment_labels, write_experiment_section_labels, read_json

    # write by entering the experiment (for convenience. Can also just call the .get_...() method and write to JSON)
    write_experiment_labels(experiment, "labelled_traces.json")
    write_experiment_section_labels(experiment, "labelled_trace_sections.json")

    # read the JSON file: Can be used to instantiate an Experiment with correctly labelled traces 
    my_labels = read_json("labelled_traces.json")
    my_section_labels = read_json("labelled_trace_sections.json")
```

Included `SetLabels(labels:dict[str, list[str]])` and `SetSectionLabels(section_labels:dict[str, dict[tuple[int,int], list[str]]])` to `data_processing.common_transformations` to enable equivalent operations to be part of a data processing pipeline. 


# [1.0.1] - 2025-07-28
Had to adjust a minor issue regarding imports. No new features 


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