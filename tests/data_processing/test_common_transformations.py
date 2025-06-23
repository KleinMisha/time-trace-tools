import numpy as np
import pytest

from src.data_processing.common_transformations import (
    SelectFrames,
    SelectTimeWindow,
    SelectTraces,
    SelectTracesByLabels,
    ShiftToOrigin,
)
from src.data_processing.processor import ExperimentProcessor
from tests.data_types.mock_experiment import (
    MockExperiment,
    create_mock_dataset,
    parse_mock_dataset,
)

NUMBER_MOCK_TRACES = 100


@pytest.fixture
def experiment(number_of_traces: int = NUMBER_MOCK_TRACES) -> MockExperiment:
    """
    generate a mock Experiment
    """
    exp = MockExperiment(ID="mock")
    data = create_mock_dataset(number_traces=number_of_traces)
    one, two, time = parse_mock_dataset(data)
    exp._raw_data = one, two, time
    exp.create_traces_from_raw_data()
    return exp


def test_select_traces(experiment: MockExperiment) -> None:
    """tests that SelectTraces returns a shorter list of traces (with only the targets kept)"""
    processor = ExperimentProcessor(experiment)

    # select only the first half of the traces
    first_half_of_traces = [f"trace_{i + 1}" for i in range(NUMBER_MOCK_TRACES // 2)]
    processor.add_transformation(SelectTraces(target_traces=first_half_of_traces))
    processor.run()
    selected_traces = [trace.ID for trace in processor._current_experiment.traces]
    assert selected_traces == first_half_of_traces


def test_select_traces_by_labels(experiment: MockExperiment) -> None:
    """tests finding only the traces with a specific label"""
    # set the labels. Give the first half the label "first label"
    # Give the fist quarter of the traces the label "second label"
    first_half_of_traces = [f"trace_{i + 1}" for i in range(NUMBER_MOCK_TRACES // 2)]
    first_quarter_of_traces = [f"trace_{i + 1}" for i in range(NUMBER_MOCK_TRACES // 4)]
    for trace in experiment.traces:
        if trace.ID in first_quarter_of_traces:
            trace.labels = ["first_label", "second_label"]
        elif trace.ID in first_half_of_traces:
            trace.labels = ["first_label"]

    # prep and perform the selection on the combination of labels. Should result only in traces in the first quarter
    processor = ExperimentProcessor(experiment)
    processor.add_transformation(
        SelectTracesByLabels(
            target_traces=[trace.ID for trace in experiment.traces],
            target_labels=["first_label", "second_label"],
        )
    )
    processor.run()
    selected_traces = [trace.ID for trace in processor._current_experiment.traces]
    assert selected_traces != first_half_of_traces
    assert selected_traces == first_quarter_of_traces


def test_select_frames(experiment: MockExperiment) -> None:
    """chop the first half of the traces"""
    number_of_time_points = len(experiment.traces[0])
    first_frame = 0
    midway_the_trace = number_of_time_points // 2
    first_half_of_traces = [f"trace_{i + 1}" for i in range(NUMBER_MOCK_TRACES // 2)]

    # prep and perform analysis
    processor = ExperimentProcessor(experiment)
    processor.add_transformation(
        SelectFrames(
            target_traces=first_half_of_traces,
            start_frame=first_frame,
            end_frame=midway_the_trace,
        )
    )
    processor.run()

    # check that only the first half of the traces got cropped, the remainder is passed on without transforming it
    for trace in processor._current_experiment.traces:
        if trace.ID in first_half_of_traces:
            assert len(trace) == number_of_time_points // 2
        else:
            assert len(trace) == number_of_time_points


def test_select_time_window(experiment: MockExperiment) -> None:
    """select the second 25% of each trace, using the corresponding time points"""
    duration: float = experiment.traces[0].t[-1]
    quarter_index = np.argmin(np.abs(experiment.traces[0].t - (duration / 4)))
    quarter_of_the_trace = experiment.traces[0].t[quarter_index]
    half_index = np.argmin(np.abs(experiment.traces[0].t - (duration / 2)))
    midway_the_trace = experiment.traces[0].t[half_index]

    first_half_of_traces = [f"trace_{i + 1}" for i in range(NUMBER_MOCK_TRACES // 2)]

    # prep and perform analysis
    processor = ExperimentProcessor(experiment)
    processor.add_transformation(
        SelectTimeWindow(
            target_traces=first_half_of_traces,
            start_time=quarter_of_the_trace,
            end_time=midway_the_trace,
        )
    )
    processor.run()

    # check that only the first half of the traces got cropped, the remainder is passed on without transforming it
    for trace in processor._current_experiment.traces:
        frame_duration = np.unique(np.diff(trace.t))[0]
        time_range = trace.t[0], trace.t[-1]
        if trace.ID in first_half_of_traces:
            # The actual time point of t= duration/2 might not exist, so just round the numbers to see if it indeed picked something within a frame
            assert round(abs(time_range[0] - quarter_of_the_trace), 3) <= round(
                frame_duration, 3
            )
            assert round(abs(time_range[1] - midway_the_trace), 3) <= round(
                frame_duration, 3
            )
        else:
            assert time_range == (0.0, duration)


def test_shift_to_origin(experiment: MockExperiment) -> None:
    """positive case: test new traces are indeed starting from the origin (along the specified axis)"""

    # apply to all traces
    trace_ids = [trace.ID for trace in experiment.traces]

    # original traces already start at t=0, so let's change this first
    for trace in experiment.traces:
        trace.t += 10.0  # anything other than 0.0 will do

    # prep and perform analysis
    processor = ExperimentProcessor(experiment)
    processor.add_transformation(
        ShiftToOrigin(target_traces=trace_ids, coordinate="value_one")
    )
    processor.run()

    # check shift worked
    for trace in processor._current_experiment.traces:
        assert (trace.t[0] == 0.0) and (trace.value_one[0] == 0.0)


def test_shift_to_origin_invalid_coordinate(experiment: MockExperiment) -> None:
    """negative case: check that you raise an exception trying to operate on an axis that is not available"""

    # apply to all traces
    trace_ids = [trace.ID for trace in experiment.traces]

    # prepare analysis
    processor = ExperimentProcessor(experiment)
    processor.add_transformation(
        ShiftToOrigin(target_traces=trace_ids, coordinate="value_three")
    )

    # check operation fails
    with pytest.raises(
        AttributeError,
        match="Trace trace_1 does not have a value-array named value_three",
    ):
        processor.run()


def test_shift_does_not_affect_original_trace(experiment: MockExperiment) -> None:
    """
    double-check that original traces remain unaffected. Mainly because Transformation is a Protocol, not an ABC inherited by ShiftToOrigin.
    Hence, cannot generally check only the target_traces are effected. Especially on this transform where you actually modify the values, it is extra important to keep the original in tact.
    """

    # apply to all traces
    trace_ids = [trace.ID for trace in experiment.traces]

    # original traces already start at t=0, so let's change this first
    for trace in experiment.traces:
        trace.t += 10.0  # anything other than 0.0 will do

    # prep and perform analysis
    processor = ExperimentProcessor(experiment)
    processor.add_transformation(
        ShiftToOrigin(target_traces=trace_ids, coordinate="value_one")
    )
    processor.run()

    # Now check that the original traces remained unaffected
    # check shift worked
    # NOTE: I could've explicitly tested for the value I know it should be, but does not matter
    for trace in processor.original_experiment.traces:
        assert (trace.t[0] != 0.0) and (trace.value_one[0] != 0.0)
