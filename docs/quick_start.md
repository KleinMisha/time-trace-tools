# Quick start guide
If you do not need to understand the *why* and the *how* of this library, here are some example code snippets that explain the most important use cases. 

## Loading raw data into your code 
Having acquired your raw data file using our magnetic-tweezers, or MT-TIRF setups, the following will create an `Experiment` object that holds your time trace data. 
The `Experiment` object not only stores a list of `TimeTrace` objects, representing the individual time trajectories of the beads / fluorescent spots, it also allows for some more convenient manipulation. See below for more details. 

```python 
from data_io.read_mt import read_mt 
from data_types.magnetic_tweezers_experiment import MagneticTweezersExperiment


# Instantiate your magnetic tweezers Experiment 
experiment = MagneticTweezersExperiment()

# use the `read_mt()` function to load the data and store it in an instance variable of the experiment 
experiment.load_raw_data(path="path/to/raw_data", data_loader_fn: read_mt_data)


# parse the matrices the loader function returns to instantiate MagneticTweezersTrace objects.
experiment.create_traces_from_raw_data()


# your traces are now stored in the following list 
print(experiment.traces)
```

You can use this `Experiment` object to perform postprocessing, see below. 

## Basic manipulations 
For simple manipulations, you can directly act on the `Experiment` and `TimeTrace` objects. That is, subtracting one trace's values from another is as easy as using the `+` and `-` operators.

Assuming you loaded actual trace data from a file (into your `Experiment`), instantiating a new `TimeTrace` will be covered on the `data_types` page. 
```python 
#  A MagneticTweezersExperiment has traces of type MagneticTweezersTrace 
trace_1: MagneticTweezersTrace
trace_2: MagneticTweezersTrace

# these operations are made to only work on the ._values (x,y,z for MagneticTweezersTrace). It checks that the time arrays are identical 

trace_1_plus_2 = trace_1 + trace_2
trace_2_min_1 = trace_2 + trace_1
```

Both `TimeTrace` and `Experiment` (parent) classes have convenient methods for finding a trace by the id, finding all traces having selected qualitative labels, etc. 

```python 
trace_42 = experiment.fetch_trace(id="trace_42")
``` 

If you added (qualitative) labels to your traces
```python
traces_with_activity = experiment.fetch_traces_by_label(label = ["activity"])
```
### Reference beads in magnetic-tweezers experiments 
Specific to magnetic tweezers data, traces have a `is_REF` property (`TRUE` / `FALSE`).
```python 
# given we are using a MagneticTweezersExperiment 
reference_bead_traces = experiment.REF_beads

# Use a different reference bead? 
experiment.set_reference_bead(ref_bead_id = "trace_3")

# Use an additional reference bead? 
experiment.set_reference_bead(ref_bead_id = "trace_2", keep_previous = True)

# Convenience method for subtracting the reference bead / drift correction 
experiment.set_reference_bead() 
```

## Postprocess your experimental data 
The `ExperimentProcessor` handles applying a series of `Transformations` on your `Experiment`. To setup your analysis, simply instantiate an `ExperimentProcessor` and register the desired set of operations to be performed. 

```python 
from data_processing.processor import ExperimentProcessor 
from data_processing.common_transformations import SelectTracesByLabels, SelectTraces 

# having loaded your experiment data, let's start an analysis 
processor = ExperimentProcessor(experiment)

# register your desired set of operations to be performed on the data 
#NOTE: These operations are just here for illustration purposes. Probably not the most useful ones.

processor.add_transformations(
    [
        # Say, we want to continue with only the first 10 beads.
        SelectTraces(target_traces = [trace.ID for trace in experiment.traces[:10]]),

        # Now, select further by searching for those traces that are labelled displaying protein activity
        SelectTracesByLabels(
            target_labels = ["activity"]
            ),
    ]
)

```
Call the `.run()` method to cary out the postprocessing 
```python 
processor.run()
```

Modifications are made on a copy of the `original_experiment`, stored as `_current_experiment`. 
???+ note "list of transformations is the ground truth" 
    `_current_experiment` is not the ground truth of the application. The set of (to be) applied `Transformation`'s is. Hence, the final state of the experiment is merely kept for cache purposes (hence the underscore it it's name). 

```python
# Need the (final) modified copy of the experiment data? 
modified_experiment = processor._current_experiment() 
```
This returns a new `Experiment` object. The corresponding `TimeTraces` are those after all transformations have been performed. Using the set of transformations as the 'ground truth of the code' allows for simple undo/redo behavior, regardless of the kind of operation. 

Want to undo the last `Transformation`? 
```python
# Simply tell the processor to apply everything excluding the last Transformation 
processor.undo()

# perform pipeline again 
processor.run()
```

Changed your mind? Redo the last `Transformation`
```python
#similar to the above: Tell the processor include the final Transformation once again  
processor.redo()

# re-run the pipeline 
processor.run() 
```

## What does saved data look like ? 
Instead of storing all intermediate transformed versions of traces (as we did in the past), we simply store the raw data and a set of instructions from which you can recreate the processed data. 

```python 
from data_io.processor import export_processor_to_toml
export_processor_to_toml(path=Path("processing_instructions.toml"), processor=processor)
```


The output will be a `TOML` file containing the following 

```TOML
original_data = "path/to/original/data/file"

[[transformations]]
type = data_processing.common_transformations.SelectTraces 
target_traces =  ['trace_2', 'trace_2', ..., 'trace_10']

[[transformations]]
type = data_processing.common_transformations.SelectTracesByLabels 
target_labels =  ['activity']
```

## Recreating analysis from saved data 
Given the processed data has not been saved directly (by default), how to quickly load it back into your code? 
The TOML file will be parsed to produce a list of `Transformation` instances that can be immediately registered again at an `ExperimentProcessor`.

Combining the above, to load / instantiate the modified data: 
```python
from data_io.raw_mt import read_mt_data
from data_io.processor import read_transformations_from_toml
from data_types.magnetic_tweezers_experiment import MagneticTweezersExperiment 
from data_processing.processor import ExperimentProcessor 


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

