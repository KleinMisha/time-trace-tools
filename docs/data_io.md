# Simplified data file handling: `data_io`

## Reading data from the magnetic-tweezers 
The `data_io.raw_mt` module contains all functions required to load data from the magnetic tweezers. 


```python linenums="1" title="Read raw data"

from data_io.raw_mt import read_mt 
T, (X,Y,Z) = read_mt()

```

???+ info "Older experimental data" 
    The `data_io.labview_legacy` module contains functions that can be used to load in data that was still acquired using the LabView controlling software. The `data_io.raw_mt.read_mt_data()` wraps around both the `read_pytweezers()` and `read_labview()` methods.

### Loading data into your `Experiment` 

```python linenums="1" title="Create an Experiment object"

from data_io.raw_mt import read_mt 
from data_types.magnetic_tweezers_experiment import MagneticTweezersExperiment 

experiment = MagneticTweezersExperiment()
experiment.create_traces(data_loader_fn = read_mt)
```

## Exporting 

### Analysis pipeline  
Once done with processing your time traces (using the `ExperimentProcessor`) you can store the set of operations needed to recreate the final form of the data (from the original data). 

=== "Code"
    ```python linenums="1" title="Save transformations to file"
    from data_io.processor import export_processor_to_toml

    ... 
    ```

=== "Output"
    The content will be a `TOML` file that looks as follows: 

    ```TOML linenums="1" title="Output"
    ```

To recreate your analysis from this output simply:
1. Re-load the original data set
2. Create an Experiment processor from the `TOML` file 
3. Run the analysis

```python linenums="1" title="Reloading the analysis"
# Get code snippet from quick start guide

```

### Time traces 
Want to save time trace data directly? 

=== "write"

    ```python linenums="1" title="Save experiment to file"
    # save time traces to file 

    # save all information needed to recreate experiment to file (???)
    ```

=== "read" 

    ```python linenums="1" title="Reloading the experiment"
    #NOTE: maybe not needed and just load the new file with traces as if it is a raw data file. 
    ```


