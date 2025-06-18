from dataclasses import dataclass

from src.data_types.type_definitions import TimeTraceType


@dataclass
class MockTransformation:
    # trace identifiers you want to modify
    target_traces: list[str]

    def apply(self, trace_list: list[TimeTraceType]) -> list[TimeTraceType]:
        """
        Does not perform actual useful transform, just to test if it correctly applies only to specified traces
        """
        new_traces = []
        for trace in trace_list:
            if not hasattr(trace, "applied"):
                trace.__setattr__("applied", False)

            if trace.ID in self.target_traces:
                trace.__setattr__("applied", True)
            new_traces.append(trace)
        return new_traces
