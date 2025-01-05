import os
import sys

CURRENT_DIRECTORY = os.path.dirname(__file__)
DIRECTORY = os.path.dirname(CURRENT_DIRECTORY)
sys.path.append(DIRECTORY)
import numpy as np  # noqa: E402
from magnetic_tweezers_trace import MagneticTweezersTrace  # noqa: E402


def test_creating_valid_mt_trace() -> None:
    ID = "valid MT trace"
    t = np.linspace(0, 100, 10)
    x = np.random.random(size=len(t))
    y = np.random.random(size=len(t))
    z = np.random.random(size=len(t))

    mt_trace = MagneticTweezersTrace(ID=ID, t=t, x=x, y=y, z=z)

    print(mt_trace)


def test_creating_invalid_mt_trace() -> None:
    ID = "invalid MT trace"
    t = np.linspace(0, 100, 10)
    x = np.random.random(size=len(t) - 2)
    y = np.random.random(size=len(t) - 2)
    z = np.random.random(size=len(t) - 2)

    # Now should raise NotATimeTraceError if I try to instantiate
    MagneticTweezersTrace(ID, t, x=x, y=y, z=z)


def test_creating_mt_trace_with_label() -> None:
    ID = "MT trace with a label"
    t = np.linspace(0, 100, 10)
    x = np.random.random(size=len(t))
    y = np.random.random(size=len(t))
    z = np.random.random(size=len(t))

    my_label = ["interesting trace"]

    mt_trace = MagneticTweezersTrace(ID, t, x=x, y=y, z=z, labels=my_label)
    print(mt_trace)


def test_adding_labels_to_mt_trace() -> None:
    ID = "MT trace with a label"
    t = np.linspace(0, 100, 10)
    x = np.random.random(size=len(t))
    y = np.random.random(size=len(t))
    z = np.random.random(size=len(t))

    my_label = ["first label"]

    mt_trace = MagneticTweezersTrace(ID, t, x=x, y=y, z=z, labels=my_label)

    mt_trace.add_labels(["second label", "third label"])
    print(mt_trace)


def test_remove_label_mt_trace() -> None:
    ID = "MT trace with a label"
    t = np.linspace(0, 100, 10)
    x = np.random.random(size=len(t))
    y = np.random.random(size=len(t))
    z = np.random.random(size=len(t))

    my_labels = ["first label", "second label", "third label"]

    mt_trace = MagneticTweezersTrace(ID, t, x=x, y=y, z=z, labels=my_labels)
    print("before:")
    print(mt_trace)
    mt_trace.remove_labels(["second label"])


def test_add_first_label_after_instance_creation() -> None:
    ID = "valid MT trace"
    t = np.linspace(0, 100, 10)
    x = np.random.random(size=len(t))
    y = np.random.random(size=len(t))
    z = np.random.random(size=len(t))

    mt_trace = MagneticTweezersTrace(ID=ID, t=t, x=x, y=y, z=z)
    mt_trace.add_labels(["first label"])
    print(mt_trace)


def test_create_mt_trace_with_labeled_section() -> None:
    ID = "valid MT trace"
    t = np.linspace(0, 100, 10)
    x = np.random.random(size=len(t))
    y = np.random.random(size=len(t))
    z = np.random.random(size=len(t))

    my_sections = {(0, 3): ["first label"]}
    mt_trace = MagneticTweezersTrace(
        ID=ID, t=t, x=x, y=y, z=z, section_labels=my_sections
    )
    print(mt_trace)


def test_create_mt_trace_with_labeled_section_after_instance() -> None:
    ID = "valid MT trace"
    t = np.linspace(0, 100, 10)
    x = np.random.random(size=len(t))
    y = np.random.random(size=len(t))
    z = np.random.random(size=len(t))

    mt_trace = MagneticTweezersTrace(ID=ID, t=t, x=x, y=y, z=z)
    mt_trace.add_labelled_section(start_index=0, end_index=3, label="first label")
    print(mt_trace)


def test_add_new_label_to_existing_section() -> None:
    ID = "valid MT trace"
    t = np.linspace(0, 100, 10)
    x = np.random.random(size=len(t))
    y = np.random.random(size=len(t))
    z = np.random.random(size=len(t))

    my_sections = {(0, 3): ["first label"]}
    mt_trace = MagneticTweezersTrace(
        ID=ID, t=t, x=x, y=y, z=z, section_labels=my_sections
    )

    mt_trace.add_labelled_section(start_index=0, end_index=3, label="second label")
    print(mt_trace)


def test_remove_label_from_section() -> None:
    ID = "valid MT trace"
    t = np.linspace(0, 100, 10)
    x = np.random.random(size=len(t))
    y = np.random.random(size=len(t))
    z = np.random.random(size=len(t))

    my_sections = {
        (0, 3): ["first label"],
        (4, 6): ["first label", "second label"],
        (0, 9): ["second label"],
    }
    mt_trace = MagneticTweezersTrace(
        ID=ID, t=t, x=x, y=y, z=z, section_labels=my_sections
    )
    print("before:")
    print(mt_trace)
    mt_trace.remove_labels_from_section(
        start_index=4, end_index=6, labels=["first label"]
    )
    print("after:")
    print(mt_trace)


def test_remove_all_sections_by_label() -> None:
    ID = "valid MT trace"
    t = np.linspace(0, 100, 10)
    x = np.random.random(size=len(t))
    y = np.random.random(size=len(t))
    z = np.random.random(size=len(t))

    my_sections = {
        (0, 3): ["first label"],
        (4, 6): ["first label", "second label"],
        (0, 9): ["second label"],
    }
    mt_trace = MagneticTweezersTrace(
        ID=ID, t=t, x=x, y=y, z=z, section_labels=my_sections
    )
    print("before:")
    print(mt_trace)
    mt_trace.remove_all_sections_by_label(label="second label")
    print("after:")
    print(mt_trace)


def test_remove_section() -> None:
    ID = "valid MT trace"
    t = np.linspace(0, 100, 10)
    x = np.random.random(size=len(t))
    y = np.random.random(size=len(t))
    z = np.random.random(size=len(t))

    my_sections = {
        (0, 3): ["first label"],
        (4, 6): ["first label", "second label"],
        (0, 9): ["second label"],
    }
    mt_trace = MagneticTweezersTrace(
        ID=ID, t=t, x=x, y=y, z=z, section_labels=my_sections
    )
    print("before:")
    print(mt_trace)
    mt_trace.remove_all_labels_from_section(start_index=0, end_index=9)
    print("after:")
    print(mt_trace)


def main() -> int:
    # create a valid trace
    test_creating_valid_mt_trace()
    print("==" * 80)
    print("\n" * 2)

    # create a trace including a label
    test_creating_mt_trace_with_label()
    print("==" * 80)
    print("\n" * 2)

    # try adding a label
    test_adding_labels_to_mt_trace()
    print("==" * 80)
    print("\n" * 2)

    # try creating a trace first, then add the label
    test_add_first_label_after_instance_creation()
    print("==" * 80)
    print("\n" * 2)

    # try removing a label
    # try creating a trace first, then add the label
    test_remove_label_mt_trace()
    print("==" * 80)
    print("\n" * 2)

    # try creating a labelled section
    test_create_mt_trace_with_labeled_section()
    print("==" * 80)
    print("\n" * 2)

    # try doing this after instantiating the object without any
    test_create_mt_trace_with_labeled_section_after_instance()
    print("==" * 80)
    print("\n" * 2)

    # try adding a label to a section
    test_add_new_label_to_existing_section()
    print("==" * 80)
    print("\n" * 2)

    # try removing a label from a specific section
    test_remove_label_from_section()
    print("==" * 80)
    print("\n" * 2)

    # try removing all sections with a particular label
    test_remove_all_sections_by_label()
    print("==" * 80)
    print("\n" * 2)

    # try removing a section with all its labels
    test_remove_section()
    print("==" * 80)
    print("\n" * 2)
    return 0


if __name__ == "__main__":
    main()
