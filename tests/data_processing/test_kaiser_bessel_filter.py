"""
To make files shorter, gathered all tests related to KaiserBesselFilter in particular in this file
"""

from itertools import product

import numpy as np
import pytest
from numpy.typing import NDArray
from scipy.fft import fft, fftfreq

from src.data_processing.filtering import KaiserBesselFilter
from src.data_processing.processor import ExperimentProcessor
from tests.data_types.mock_experiment import (
    MockExperiment,
    parse_mock_dataset,
)
from tests.data_types.mock_time_trace import MockTimeTrace

MockSignal = tuple[NDArray[np.floating], NDArray[np.floating], float, float]


# define simple constant here
ACQUISITION_FREQUENCY = 58.0
DURATION = 1800.0
TIME_POINTS = int(DURATION * ACQUISITION_FREQUENCY)
NUMBER_OF_TRACES = 100


def create_mock_signal(
    cutoff_frequency: float, transition_width: float = 5.0
) -> MockSignal:
    """Define a simple signal composed of two sine waves of different frequencies"""
    # create a signal with two frequency components, one inside the passband, one inside the stopband (outside the passband)
    t = np.linspace(0, DURATION, TIME_POINTS, endpoint=False)
    freq_pass = cutoff_frequency * 0.5
    freq_stop = cutoff_frequency + 2.0 * transition_width
    sine_pass = np.sin(2 * np.pi * freq_pass * t)
    sine_stop = np.sin(2 * np.pi * freq_stop * t)
    x = sine_pass + sine_stop
    return t, x, freq_pass, freq_stop


def calculate_amplitude(x: NDArray[np.floating], freq: float) -> float:
    """Use FFT to determine amplitude at (around) specified frequency"""
    # Use |X(f)| as the amplitude of frequency component f. With X(f) the Fourier transform of x(t)
    fft_x = np.asarray(fft(x))
    frequencies = fftfreq(len(x), d=1 / int(ACQUISITION_FREQUENCY))

    # Normalize to get amplitude spectrum
    amplitude_spectrum = np.abs(fft_x) / len(x)

    # get the amplitude at sampled frequency closest to target
    idx_freq = np.argmin(np.abs(frequencies - freq))
    return amplitude_spectrum[idx_freq]


def calculate_attenuation(
    x: NDArray[np.floating], freq_pass: float, freq_stop: float
) -> float:
    """Use |X(freq_stop)|/|X(freq_pass)| to determine attenuation in decibel"""
    # Check frequency spectrum of filtered signal using FFT
    amplitude_stopband = calculate_amplitude(x, freq_stop)
    amplitude_passband = calculate_amplitude(x, freq_pass)

    # Determine attenuation and convert into decibel
    attenuation_dB = 20 * np.log10(amplitude_stopband / amplitude_passband)
    return attenuation_dB


def create_mock_experiment(
    cutoff_frequency: float,
    transition_width: float = 0.01 * 0.5 * ACQUISITION_FREQUENCY,
) -> MockExperiment:
    """
    Create a mock experiment with signals as mock_signals (sine waves, to be used for testing filters)
    """
    exp = MockExperiment(ID="mock")
    t, signal, *_ = create_mock_signal(cutoff_frequency, transition_width)
    x = signal.copy()
    y = signal.copy()
    mock_traces = [
        MockTimeTrace(ID="mock", t=t, value_one=x, value_two=y)
        for _ in range(NUMBER_OF_TRACES)
    ]

    data_table = [t]
    for trace in mock_traces:
        data_table.append(trace.value_one)
        data_table.append(trace.value_two)

    data = np.array(data_table).T
    one, two, time = parse_mock_dataset(data)
    exp._raw_data = one, two, time
    exp.create_traces_from_raw_data()
    return exp


@pytest.mark.parametrize(
    "cutoff_frequency, attenuation_factor",
    list(product([0.5, 1.0, 2.0], [10, 100])),
)
def test_kaiser_bessel_output_size(
    cutoff_frequency: float, attenuation_factor: float
) -> None:
    """
    check that filtered signal has the same length as the raw signal.
    NOTE: SciPy filters perform convolution after some zero-padding, and then crop the final result to return a signal of the same length as the original.
    """
    time_before, signal_before, *_ = create_mock_signal(cutoff_frequency)
    acq_freq = ACQUISITION_FREQUENCY
    kb_filter = KaiserBesselFilter(
        target_traces=[""],
        coordinate="",
        acquisition_frequency=acq_freq,
        cutoff_frequency=cutoff_frequency,
    )

    time_after, signal_after = kb_filter.filter(time_before, signal_before)

    assert len(time_before) == len(time_after)
    assert len(signal_before) == len(signal_after)


@pytest.mark.parametrize(
    "cutoff_frequency, attenuation_factor",
    list(product([0.5, 1.0, 2.0], [10, 100])),
)
def test_kaiser_bessel_attenuation_at_high_frequencies(
    cutoff_frequency: float, attenuation_factor: float
) -> None:
    """
    Check that filtered signal has less energy at a frequency in stopband compared to passband
    """
    t, x, freq_pass, freq_stop = create_mock_signal(cutoff_frequency)
    acq_freq = ACQUISITION_FREQUENCY
    kb_filter = KaiserBesselFilter(
        target_traces=[""],
        coordinate="",
        acquisition_frequency=acq_freq,
        cutoff_frequency=cutoff_frequency,
    )

    _, x_filtered = kb_filter.filter(t, x)
    attenuation_dB = calculate_attenuation(x_filtered, freq_pass, freq_stop)
    assert attenuation_dB < -attenuation_factor + 5.0


@pytest.mark.parametrize(
    "cutoff_frequency, attenuation_factor",
    list(product([0.5, 1.0, 2.0], [10, 100])),
)
def test_kaiser_bessel_attenuation_wrt_original(
    cutoff_frequency: float, attenuation_factor: float
) -> None:
    """
    Check if the filter actually attenuates the signal above the cutoff when compared to the raw signal.
    """
    # create raw signal
    t, x_raw, freq_pass, freq_stop = create_mock_signal(cutoff_frequency)
    acq_freq = ACQUISITION_FREQUENCY
    kb_filter = KaiserBesselFilter(
        target_traces=[""],
        coordinate="",
        acquisition_frequency=acq_freq,
        cutoff_frequency=cutoff_frequency,
    )

    # filter the signal
    _, x_filtered = kb_filter.filter(t, x_raw)

    # check that the filter actually did its job correctly
    attenuation_before = calculate_attenuation(x_raw, freq_pass, freq_stop)
    assert attenuation_before >= -attenuation_factor + 5.0
    attenuation_after = calculate_attenuation(x_filtered, freq_pass, freq_stop)
    assert (attenuation_after - attenuation_before) <= -attenuation_factor + 5.0


def test_kaiser_bessel_within_processor() -> None:
    """
    NOTE: Strictly no longer required as ExperimentProcessor has its own unit tests already.
          Since this is the first serious Transformation I implementing, I wanted to perform these checks to make sure

    integrated in the Experiment processor, test the following:
    1. Does my pipeline run?
    2. Does it correctly not overwrite the original signal?
    """
    # create mock data here
    cutoff_frequency = 0.5
    attenuation_factor = 10.0
    mock_experiment = create_mock_experiment(cutoff_frequency, attenuation_factor)

    # set up analysis
    processor = ExperimentProcessor(mock_experiment)
    processor.add_transformation(
        KaiserBesselFilter(
            target_traces=[trace.ID for trace in mock_experiment.traces],
            coordinate="value_one",
            acquisition_frequency=ACQUISITION_FREQUENCY,
            cutoff_frequency=cutoff_frequency,
            stopband_attenuation_dB=attenuation_factor,
        )
    )

    # perform analysis
    processor.run()

    # Perform similar checks as before, just to make sure things went OK in the context of the ExperimentProcessor
    traces_before_filtering = processor.original_experiment.traces
    filtered_experiment = processor.get_current_experiment()
    traces_after_filtering = filtered_experiment.traces
    freq_pass = cutoff_frequency * 0.2
    freq_stop = cutoff_frequency + 5.0

    for before, after in zip(traces_before_filtering, traces_after_filtering):
        attenuation_before = calculate_attenuation(
            before.value_one, freq_pass, freq_stop
        )
        attenuation_after = calculate_attenuation(after.value_one, freq_pass, freq_stop)

        # Sanity check: signal before filtering should contain significant energy in stopband
        assert attenuation_before > -attenuation_factor + 5.0
        # Now test performance of filter
        assert (attenuation_after - attenuation_before) <= -attenuation_factor + 5.0
