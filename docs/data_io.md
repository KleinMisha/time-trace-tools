# Simplified data file handling: `data_io`

## Reading data from the magnetic-tweezers 
The `data_io.raw_mt` module contains all functions required to load data from the magnetic tweezers. 


```python linenums="1" title="Read raw data"

from data_io.raw_mt import read_mt 
T, (X,Y,Z) = read_mt()

```

???+ info "Older experimental data" 
    The `data_io.labview_legacy.py` module contains functions that can be used to load in data that was still acquired using the LabView controlling software. The `data_io.raw_mt.read_mt_data()` wraps around both the `read_pytweezers()` and `read_labview()` methods.

???- tip "motor controlling scripts" 
    Want to use the scripts defining the motor movements? Check `data_io.magnet_script.py` and its equivalent in `data_io.labview_legacy.py`

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
    export_processor_to_toml(path=Path("processing_instructions.toml"), processor=processor)
    ```
=== "Output"
    The content will be a `TOML` file that looks as follows: 

    ```TOML
    original_data = "path/to/original/data/file"

    [[transformations]]
    type = data_processing.common_transformations.SelectTraces 
    target_traces =  ['trace_2', 'trace_2', ..., 'trace_10']

    [[transformations]]
    type = data_processing.common_transformations.SelectTracesByLabels 
    target_labels =  ['activity']
    ```
To recreate your analysis from this output simply:

1. Re-load the original data set
2. Create an Experiment processor from the `TOML` file 
3. Run the analysis

```python linenums="1" title="Reloading the analysis"
# Load the raw data and instantiate the trace list 
experiment = MagneticTweezersExperiment()
experiment.load_raw_data(path="path/to/raw_data", data_loader_fn: read_mt_data)
experiment.create_traces_from_raw_data()

# Load the analysis 
applied_transformations = read_transformations_from_toml("processing_instructions.toml")
processor = ExperimentProcessor(experiment)
processor.add_transformations(applied_transformations)

# Redo the analysis, and done 
processor.run()
```

### Time traces 
Want to save time trace data directly? 

```python linenums="1" title="Save experiment to file (magnetic tweezers)"
from data_io.raw_mt import write_traces

# save time traces to file 
mt_traces = mt_experiment.traces
write_traces(mt_traces, path="my_traces.npy")
```




