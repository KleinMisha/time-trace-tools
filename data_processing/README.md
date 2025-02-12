### Process time traces 
Having created your `TimeTrace`, `Experiment`, or `ExperimentSeries` data processing is handled by a `DataProcessor` that can apply methods to traces 
<span style="color:yellow">NOTE: THINK THIS PART THROUGH MORE. MAINLY WANT FAST WAYS OF INSTANTIATING PIPELINES FOR FREQUENTLY PERFORMED EXPERIMENTAL ASSAYS</span>

```python
from typing import Callable 
class DataProcessor:
    methods: list[Callable]
    traces: list[TimeTrace]

    def register_method(function: Callable) --> None:
    def unregister_method(function: Callable) --> None:

    def apply() --> None: 
        '''
        Applies the set of register methods to all the supplied traces
        '''

```