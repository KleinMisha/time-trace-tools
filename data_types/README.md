# Core data structures for magnetic tweezer data 

## The Experiment Class 

## The Trace Class 

## The ExperimentSeries Class 



```python

class MagneticTweezerTrace(TimeTrace):
    ID: str     
    t: NumpyArray[float]
    x: NumpyArray[float]
    y: NumpyArray[float]
    z: NumpyArray[float]
    is_REF:bool 
    labels: list[str]
    section_labels: dict[tuple[int, int], list[str]]
```
Simply put, a trace from the magnetic tweezers has a time-axis, and x,y, and z-positions. Furthermore, any `TimeTrace` has an optional list of any labels you wish to assign to a given trace. These can be used to mark a trace as showing activity, denoting the trace is (un)useable, etc. Besides 'global' labels applicable to the entire trace, you may wish to label particular sections of the trace. These lists of labels are stored as the values of a dictionary with keys equal to the pair of start/end indices in the time-array (demarking the section of interest). 
Finally, a if contains a property `.is_REF` to denote if this trace is of a reference bead or not. 

Why this object-oriented representation?
We can now define an entire data-set as an `Experiment`; essentially a container with many traces (of the same kind). For a magnetic tweezers experiment, we have 
```python
class MagneticTweezersExperiment():
    ID: str
    traces: list[MagneticTweezerTrace] 
    ref_bead_id: str 
    path_to_raw_data: Path | str = Path("")
    

    '''
    methods include:
        - setting a (new) bead as a reference bead
        - subtracting the reference bead's signal from all (other) traces
        - fetching traces based on their ID
        - fetching all traces that have a particular label 
        - fetching all traces that have a section that is labelled with a particular label

        ....
        AND MORE CONVENIENCE FUNCTIONS

    '''
```

### 
After loading your data, you can create a `MagneticTweezersTrace` as follows
```python
import numpy as np 
from data_types.magnetic_tweezer_trace import MagneticTweezerTrace
# here, just demonstrated for the first bead. See below how to deal with the entire set of traces in a more convenient way 
x = bead_positions_xyz[0, :, 0]
y = bead_positions_xyz[0, :, 1]
z = bead_positions_xyz[0, :, 2]

# create the trace 
trace = MagneticTweezerTrace(t=time, x=x,y=y,z=z, ID="bead_1")
# You now can find the z-position of the first bead by calling
print(trace.z)
```
We can now add labels to the entire trace, or to specific sections of the trace as follows
```python
trace.add_label("pretty trace")

# Say, you want to analyze just the start of the trace for some reason
start_section = 0 
end_section = 100
trace.add_section(start_frame_number=start_section, end_frame_number=end_section, label="before adding reagents")

# This will store the section in a dictionary with a key of (start_frame_number, end_frame_number) and value "before adding reagents" (i.e. the chosen label).

# Process just a part of the trace

def your_very_important_function(z: NumpyArray, t: NumpyArray) -> NumpyArray:
    '''calculate something based on the heigth of a bead and return a new array'''

for (section,label) in trace.sections.items():
    if label == "before adding reagents":
        ''' 
        retreive the important part of the trace and apply your very important function to it
        '''
```

Time traces also have some convenience methods available for adding/removing labes, altering labels, adding/removing sections, accessing the section, quickly viewing all sections of a particular label, etc. Also, general arithmatic for shifting, adding, and averaging traces are available.



<span style="color:lightblue"> **NOTE:** see the `README.md` in the `data_types` directory for all the available functions.  </span>

An `Experiment` deals with a data set with multiple traces. For a typical magnetic tweezers experiment, create a `MagneticTweezersExperiment` 
```python 
#NOTE: Similar to the `MagneticTweezersTrace` demonstrated above, many things demonstrated here for a   `MagneticTweezersExperiment` can be used with any implementation of an `Experiment`

from data_types.magnetic_tweezers_experiment import MagneticTweezersExperiment
from data_io.raw_mt import read_raw_mt
# create an experiment with some descriptions. 
# At minimum, it should have an identifier. 
# Other information can be provided later. 
mt_experiment = MagneticTweezersExperiment(
    ID="simple identifier. For instance '500 µM NTP'",
    
    # A dictionary with any information you want to use to specify the experimental conditions. This is optional, not need to instanciate an Experiment. 
    experimental_conditions={
        "protein_X_uM" : 1.,
        "protein_Y_uM" : 2.,
        "NTP_uM": 500.,
        "force_pN": 25.,
        ...
    }
    ref_bead_nr = 1 # say, the first bead is the reference bead
)

# load the raw data. 
FILEPATH = "path to raw data"
mt_experiment.load_raw_data(path=FILEPATH, use_method=read_raw_mt) # will store the raw data as class attribute

# create the series of `MagneticTweezerTrace` instances 
mt_experiment.create_traces_from_raw_data()

# traces are stored in a list with objects of type MagneticTweezerTrace 
mt_experiment.traces : list[MagneticTweezerTrace]


# perform reference substraction 
mt_experiment.substrace_reference_bead() #NOTE: you can use this function to change reference bead 

# access the 50th trace for further inspection (just an example)
trace_50 = mt_experiment.fetch_trace(trace_id="trace_50") 

```
Now you can access functions to assign a label to a (set of) trace(s), or to a part of a trace, simple access to all traces with a particular label, or access a particular part of all traces. 
For some of the specific implementations (for particular assays) there might be even functions that can set the experiment name from the filename for instance. 

<span style="color:lightblue">NOTE: See the `README.md` inside `data_types` for all available methods and their functions. There are much more than demonstrated in this bare bones example</span>

Typically the `MagneticTweezerExperiment` class will be your entry point for dealing with experimental data. 
To conveniently deal with a series of `Experiments`, create an `ExperimentSeries`. 
For typical magnetic tweezer experiments 

```python 
from data_types.magnetic_tweezers_experiment_series import MagneticTweezerExperimentSeries
from data_types.magnetic_tweezers_experiment import MagneticTweezerExperiment


# example 1: repeat experiments. Starting from the individual experiments

experiment_1 = MagneticTweezersExperiment(ID='first experiment')
experiment_2 = MagneticTweezersExperiment(ID='second experiment')

repeat_experiments = MagneticTweezerExperimentSeries(experiments=[experiment_1, experiment_2])

# oops, forgot to add one more repeat 
experiment_3 = MagneticTweezersExperiment(ID='third experiment')
repeat_experiments.add_experiment(experiment_3)

# example 2: Use the filenames to the raw data sets 
FILEPATHS = ["path/to/file 1", "path/to/file 2"]
EXPERIMENTS = ["first", "second", "third"]
repeat_experiments = MagneticTweezersExperimentSeries()
repeat_experiments.create_experiments_from_raw_data(paths = FILEPATHS, ID_list = EXPERIMENTS)

# Now you can manually create the traces for the individual experiments as shown above. NOTE: For convenience this is done internally, so in most cases don't need to call yourself. 
repeat_experiments.create_traces()



# example 3: Sweep NTP concentration 

COMMON_CONDITIONS = {"force":25.,  "protein_concentration": 0.2} 

CONCENTRATION_SWEEP = {'[NTP]':[0., 10., 100., 1000.]}
FILEPATHS: list[str] = []

concentration_sweep = MagneticTweezersExperimentSeries(paths=FILEPATHS)
# automatically take care of creating instances of `MagneticTweezerExperiment`, with their respective IDs based on the NTP concentration. 
concentration_sweep.create_experiments_from_sweep(dependent_variable=CONCENTRATION_SWEEP, common_conditions=COMMON_CONDITIONS)
```
<span style="color:lightblue">NOTE: See the `README.md` inside `data_types` for all available methods and their functions. There are much more than demonstrated in this bare bones example</span>
