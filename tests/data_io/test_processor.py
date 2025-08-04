"""
src/data_io/processor.py contains the functions to read/write transformation instructions to be used with an ExperimentProcessor
"""

import re
import tempfile
from pathlib import Path

import pytest
import toml

from tests.data_processing.mock_transformation import MockTransformation
from tests.data_types.mock_experiment import (
    MockExperiment,
    create_mock_dataset,
    parse_mock_dataset,
)
from time_trace_tools.data_io.processor import (
    InvalidTransformationError,
    export_processor_to_toml,
    read_transformations_from_toml,
)
from time_trace_tools.data_processing.processor import ExperimentProcessor
from time_trace_tools.data_types.type_definitions import TimeTraceType


class BadTransformation:
    """Mock a transformation that is not a dataclass. Hence cannot be serialized using dataclasses.asdict()."""

    def __init__(self, target_traces: list[str]) -> None:
        self.target_traces = target_traces

    def apply(self, trace_list: list[TimeTraceType]) -> list[TimeTraceType]:
        """dummy operation. Does not matter, shouldn't be able to write this into a file anyways"""
        return trace_list


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


@pytest.fixture
def processor(experiment: MockExperiment, number_of_traces: int) -> ExperimentProcessor:
    """
    generate an ExperimentProcessor with a registered MockExperiment and MockTransformations.
    """
    transformation_1 = MockTransformation(
        [trace.ID for trace in experiment.traces[: (number_of_traces // 2)]]
    )
    transformation_2 = MockTransformation(
        [trace.ID for trace in experiment.traces[(number_of_traces // 2) :]]
    )
    mock_processor = ExperimentProcessor(experiment)
    mock_processor.add_transformations([transformation_1, transformation_2])
    return mock_processor


def test_export_processor_to_toml(
    processor: ExperimentProcessor, number_of_traces: int
) -> None:
    """
    Write a series of MockTransformation operations performed on a MockExperiment to TOML file, then read it back to check contents.
    NOTE: only tests the format of the written data
    """
    with tempfile.NamedTemporaryFile(mode="w+", suffix=".toml") as tmp:
        # create temporary file
        tmp_path = Path(tmp.name)
        export_processor_to_toml(tmp_path, processor)

        # reset pointer to start of file, otherwise Python will read in an empty set of data
        tmp.seek(0)

        # read this newly created file and test
        written_data = toml.load(tmp)

    assert "original_data" in written_data
    assert "transformations" in written_data
    assert isinstance(written_data["transformations"], list)
    assert written_data["transformations"][0]["target_traces"] == [
        f"trace_{i + 1}" for i in range(number_of_traces // 2)
    ]
    assert written_data["transformations"][0]["type"].endswith("MockTransformation")
    assert written_data["transformations"][1]["target_traces"] == [
        f"trace_{i + 1}" for i in range(number_of_traces // 2, number_of_traces)
    ]
    assert written_data["transformations"][1]["type"].endswith("MockTransformation")


def test_exporting_not_a_dataclass(experiment: MockExperiment) -> None:
    """Attempt to write a Transformation that is not a dataclass to file"""
    bad_transformation = BadTransformation(["trace_1", "trace_2"])
    processor = ExperimentProcessor(experiment)
    processor.add_transformation(bad_transformation)
    with pytest.raises(
        InvalidTransformationError,
        match=re.escape(
            "BadTransformation is not a dataclass. Cannot apply dataclasses.asdict() to it."
        ),
    ):
        with tempfile.NamedTemporaryFile("w+", suffix=".toml") as tmp:
            export_processor_to_toml(tmp.name, processor)


def test_read_transformations_from_toml(
    processor: ExperimentProcessor, number_of_traces: int
) -> None:
    """Read an example (temporary) file and check we indeed get a valid set of transformations after parsing."""
    with tempfile.NamedTemporaryFile(mode="w+", suffix=".toml") as tmp:
        tmp_path = Path(tmp.name)
        export_processor_to_toml(tmp_path, processor)
        tmp.seek(0)
        parsed_data = read_transformations_from_toml(tmp_path)

    for item in parsed_data:
        assert isinstance(item, MockTransformation)

    if isinstance(parsed_data[0], MockTransformation):
        assert parsed_data[0].target_traces == [
            f"trace_{i + 1}" for i in range(number_of_traces // 2)
        ]
    if isinstance(parsed_data[1], MockTransformation):
        assert parsed_data[1].target_traces == [
            f"trace_{i + 1}" for i in range(number_of_traces // 2, number_of_traces)
        ]


def test_recreate_analysis_from_toml(
    processor: ExperimentProcessor, experiment: MockExperiment
) -> None:
    """Round-trip test. Tests the writing to file, then loading back the set of transformations and applying them afterwards."""
    with tempfile.NamedTemporaryFile(mode="w+", suffix=".toml") as tmp:
        tmp_path = Path(tmp.name)
        export_processor_to_toml(tmp_path, processor)
        tmp.seek(0)
        transformations = read_transformations_from_toml(tmp_path)

    # now re-apply the transformations and check things worked
    new_processor = ExperimentProcessor(
        experiment
    )  # NOTE: Create a new ExperimentProcessor to mimic the use-case. You'd not have an existing processor already.
    new_processor.add_transformations(transformations)
    new_processor.run()

    assert new_processor.state_index == 2
    modified_experiment = new_processor.get_current_experiment()
    modified_traces = modified_experiment.traces
    for trace in modified_traces:
        assert trace.__getattribute__("applied")
