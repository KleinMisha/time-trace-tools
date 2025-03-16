"""
Custom exception definitions that can be used in other parts of code.
Avoids redefining this every time (even though it is just a few lines of code)
"""


class InvalidTimeTraceError(Exception):
    """
    Raise when you are trying to instantiate an invalid TimeTrace or when you are trying to perform an invalid operation on (a set of) TimeTrace(s)
    """

    pass
