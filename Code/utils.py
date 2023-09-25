from __future__ import annotations

import os
from fractions import Fraction
from typing import List


def collect_measure_maps(directory: str) -> List[str]:
    """Returns all filepaths under the given directory that end with '.measuremap.json'."""
    directory = os.path.abspath(os.path.expanduser(directory))
    filepaths = []
    for folder, subfolders, filenames in os.walk(directory):
        subfolders[:] = [s for s in subfolders if not s.startswith('.')]
        for filename in filenames:
            if filename.endswith('.measuremap.json'):
                filepaths.append(os.path.join(directory, folder, filename))
    return filepaths


def time_signature2nominal_length(time_signature: str) -> float:
    """Converts the given time signature into a fraction and then into the corresponding length in quarter notes."""
    assert isinstance(time_signature, str), (f"time_signature must be a string, got {type(time_signature)!r}: "
                                             f"{time_signature!r}")
    try:
        ts_frac = Fraction(time_signature)
    except ValueError:
        raise ValueError(f"Invalid time signature: {time_signature!r}")
    return ts_frac * 4.0
