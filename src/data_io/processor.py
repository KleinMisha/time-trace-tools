"""
Reading / writing Transformations done in the ExperimentProcessor


-  Misha Klein, June 2025
"""

import importlib
from dataclasses import asdict, is_dataclass
from pathlib import Path
from typing import Type

import toml

from src.data_processing.processor import ExperimentProcessor
from src.data_processing.transformation import Transformation

FilePath = Path | str


class InvalidTransformationError(Exception):
    """defines custom exception"""

    ...


def export_processor_to_toml(path: FilePath, processor: ExperimentProcessor) -> None:
    """
    Serializes the Transformation dataclasses and writes "instructions needed to reproduce analysis" into a TOML file.
    """

    # serialize the Transformation objects (use the state index to infer which Transformations are actually used )
    transformation_info = []
    for transformation in processor.transformations[: processor.state_index]:
        if not is_dataclass(transformation):
            raise InvalidTransformationError(
                f"{transformation.__class__.__name__} is not a dataclass. Cannot apply dataclasses.asdict() to it."
            )
        serialized = asdict(transformation)
        # importlib can use the following string to dynamically import the proper class name
        serialized["type"] = (
            f"{type(transformation).__module__}.{type(transformation).__qualname__}"
        )
        transformation_info.append(serialized)

    analysis_info = {
        "original_data": processor.original_experiment.path_to_raw_data,
        "transformations": transformation_info,
    }

    with open(path, "w") as toml_file:
        toml.dump(analysis_info, toml_file)


def import_class_from_module(import_path: str) -> Type[Transformation]:
    """Dynamic import equivalent to  `from module import class_name` using importlib"""
    module_path, class_name = import_path.rsplit(".", 1)
    module = importlib.import_module(module_path)
    return getattr(module, class_name)


def read_transformations_from_toml(path: FilePath) -> list[Transformation]:
    """
    Deserialize the instructions in the TOML file to recreate the Transformation history.
    Register the resulting list of Transformations at an ExperimentProcessor to recreate the analysis.
    """

    with open(path, "r") as f:
        analysis_info = toml.load(f)

    # parse / deserialize its content to instantiate the correct Transformation instances
    transformation_pipeline = []
    for transformation_info in analysis_info["transformations"]:
        class_import_path = transformation_info.pop("type")
        constructor = import_class_from_module(class_import_path)
        transformation = constructor(**transformation_info)
        transformation_pipeline.append(transformation)

    return transformation_pipeline
