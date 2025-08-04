"""
test the ExperimentProcessor
"""

import pytest

from time_trace_tools.data_processing.processor import ExperimentProcessor
from tests.data_processing.mock_transformation import MockTransformation
from tests.data_types.mock_experiment import (
    MockExperiment,
    create_mock_dataset,
    parse_mock_dataset,
)


@pytest.fixture
def number_of_traces() -> int:
    return 100


@pytest.fixture
def experiment(number_of_traces: int) -> MockExperiment:
    """
    generate a mock Experiment
    """
    exp = MockExperiment(ID="mock")
    data = create_mock_dataset(number_traces=number_of_traces)
    one, two, time = parse_mock_dataset(data)
    exp._raw_data = one, two, time
    exp.create_traces_from_raw_data()
    return exp


def test_creating_processor(experiment: MockExperiment) -> None:
    """create a processor without any registered transformations"""
    processor = ExperimentProcessor(experiment)
    assert isinstance(processor, ExperimentProcessor)
    assert processor.transformations == []


def test_registering_transformation(experiment: MockExperiment) -> None:
    """register a new transformation (for simplicity, apply it to all traces for now)"""
    transformation = MockTransformation([])
    processor = ExperimentProcessor(experiment)
    processor.add_transformation(transformation)
    assert processor.transformations == [transformation]
    assert processor.state_index == 1


def test_registering_multiple_transformations(experiment: MockExperiment) -> None:
    """register multiple transformations"""
    # apply to the first 50 traces
    transformation_1 = MockTransformation(
        [trace.ID for trace in experiment.traces[:50]]
    )

    # apply to the remaining traces
    transformation_2 = MockTransformation(
        [trace.ID for trace in experiment.traces[50:]]
    )

    # set up analysis
    processor = ExperimentProcessor(experiment)
    processor.add_transformation(transformation_1)
    processor.add_transformation(transformation_2)
    assert processor.transformations == [transformation_1, transformation_2]


def test_add_transformations_list(experiment: MockExperiment) -> None:
    """use the .add_transformations() to register an iterable of transformations"""
    # apply to the first 50 traces
    transformation_1 = MockTransformation(
        [trace.ID for trace in experiment.traces[:50]]
    )

    # apply to the remaining traces
    transformation_2 = MockTransformation(
        [trace.ID for trace in experiment.traces[50:]]
    )

    # set up analysis
    processor = ExperimentProcessor(experiment)
    processor.add_transformations([transformation_1, transformation_2])
    assert processor.transformations == [transformation_1, transformation_2]


def test_add_transformations_other_iterable(experiment: MockExperiment) -> None:
    """Quick check to test if it keeps working with other common iterables."""
    # apply to the first 50 traces
    transformation_1 = MockTransformation(
        [trace.ID for trace in experiment.traces[:50]]
    )

    # apply to the remaining traces
    transformation_2 = MockTransformation(
        [trace.ID for trace in experiment.traces[50:]]
    )

    # set up analysis

    as_list = [transformation_1, transformation_2]
    as_tuple = tuple(as_list)
    as_dict_values = dict(first=transformation_1, second=transformation_2).values()
    as_generator = (transformation for transformation in as_list)

    transformation_iterables = [as_list, as_tuple, as_dict_values, as_generator]
    for workflow in transformation_iterables:
        processor = ExperimentProcessor(experiment)
        processor.add_transformations(workflow)
        assert processor.transformations == [transformation_1, transformation_2]


def test_apply_empty_pipeline(experiment: MockExperiment) -> None:
    """run processor before registering Transformations. Should just result in the original experiment"""
    processor = ExperimentProcessor(experiment)
    processor.run()
    before = processor.original_experiment
    after = processor.get_current_experiment()

    trace_ids = [trace.ID for trace in before.traces]
    for trace_id in trace_ids:
        before_trace = before.fetch_trace(trace_id)
        after_trace = after.fetch_trace(trace_id)
        assert before_trace == after_trace


def test_undo_all_transformations(experiment: MockExperiment) -> None:
    """Undo all registered transformations, then run to confirm the final traces are equal to the initial traces"""
    # apply to the first 50 traces
    transformation_1 = MockTransformation(
        [trace.ID for trace in experiment.traces[:50]]
    )

    # apply to the remaining traces
    transformation_2 = MockTransformation(
        [trace.ID for trace in experiment.traces[50:]]
    )

    # set up analysis
    processor = ExperimentProcessor(experiment)
    processor.add_transformation(transformation_1)
    processor.add_transformation(transformation_2)

    # perform analysis
    processor.run()
    processor.undo()
    processor.undo()
    processor.run()
    assert processor.state_index == 0
    before = processor.original_experiment
    after = processor.get_current_experiment()

    trace_ids = [trace.ID for trace in before.traces]
    for trace_id in trace_ids:
        before_trace = before.fetch_trace(trace_id)
        after_trace = after.fetch_trace(trace_id)
        assert before_trace == after_trace


def test_do_not_modify_original_experiment(experiment: MockExperiment) -> None:
    """Original traces / experiment should not get modified"""
    # apply to the first 50 traces
    transformation_1 = MockTransformation(
        [trace.ID for trace in experiment.traces[:50]]
    )

    # set up analysis
    processor = ExperimentProcessor(experiment)
    processor.add_transformation(transformation_1)

    # perform analysis
    processor.run()

    original_traces = processor.original_experiment.traces
    for trace in original_traces:
        assert not hasattr(trace, "applied")


def test_applying_all_transformations(experiment: MockExperiment) -> None:
    """Use the .run() method to apply the transformations"""
    # apply to the first 50 traces
    transformation_1 = MockTransformation(
        [trace.ID for trace in experiment.traces[:50]]
    )

    # apply to the remaining traces
    transformation_2 = MockTransformation(
        [trace.ID for trace in experiment.traces[50:]]
    )

    # set up analysis
    processor = ExperimentProcessor(experiment)
    processor.add_transformation(transformation_1)
    processor.add_transformation(transformation_2)

    # perform analysis
    processor.run()
    assert processor.state_index == 2

    modified_experiment = processor.get_current_experiment()
    modified_traces = modified_experiment.traces
    for trace in modified_traces:
        assert trace.__getattribute__("applied")


def test_undo_last_transformation(experiment: MockExperiment) -> None:
    """Use .undo() to revert last transformation, then .run() again to see effect"""
    # apply to the first 50 traces
    transformation_1 = MockTransformation(
        [trace.ID for trace in experiment.traces[:50]]
    )

    # apply to the remaining traces
    transformation_2 = MockTransformation(
        [trace.ID for trace in experiment.traces[50:]]
    )

    # set up analysis
    processor = ExperimentProcessor(experiment)
    processor.add_transformation(transformation_1)
    processor.add_transformation(transformation_2)

    # perform analysis
    processor.run()

    # undo last transformation
    processor.undo()
    assert processor.state_index == 1

    # re-run
    processor.run()

    # Now only the first 50 traces should have .applied == True, others should be .applied==False
    modified_experiment = processor.get_current_experiment()
    modified_traces = modified_experiment.traces
    for trace in modified_traces[:50]:
        assert trace.__getattribute__("applied")

    for trace in modified_traces[50:]:
        assert not hasattr(trace, "applied")


def test_redo_transformation(experiment: MockExperiment) -> None:
    """first undo, then redo the final transformation once again"""
    # apply to the first 50 traces
    transformation_1 = MockTransformation(
        [trace.ID for trace in experiment.traces[:50]]
    )

    # apply to the remaining traces
    transformation_2 = MockTransformation(
        [trace.ID for trace in experiment.traces[50:]]
    )

    # set up analysis
    processor = ExperimentProcessor(experiment)
    processor.add_transformation(transformation_1)
    processor.add_transformation(transformation_2)

    # perform analysis
    processor.run()

    # undo last transformation
    processor.undo()

    # redo last transformation
    processor.redo()
    assert processor.state_index == 2

    # All traces should once again have .applied == True
    modified_experiment = processor.get_current_experiment()
    modified_traces = modified_experiment.traces
    for trace in modified_traces:
        assert trace.__getattribute__("applied")
