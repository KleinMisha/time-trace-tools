"""
Custom exception definitions that can be used in other parts of code.
Avoids redefining this every time (even though it is just a few lines of code)
"""


class InvalidTimeTraceError(Exception):
    """
    Raise when you are trying to instantiate an invalid TimeTrace
    """

    pass


class InvalidExperimentError(Exception):
    """
    Raise when you are trying to instantiate an invalid Experiment
    """

    pass
