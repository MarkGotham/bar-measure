import json
import os
from dataclasses import dataclass
from numbers import Number
from typing import Protocol, runtime_checkable, Optional, List


@runtime_checkable
class PMeasure(Protocol):
    ID: str
    """Any unique string to identify this measure."""
    count: int
    """A simple count of measure units in the described source, using natural numbers starting with 1."""
    qstamp: Optional[float]
    """The symbolic time to have elapsed since the start of the source, measured in quarter notes."""
    number: Optional[int]
    """A number assigned to this measure, which typically follows musical convention, for instance starting with natural 
    numbers (1, 2, 3...), except in the case of anacruses which start instead on (0, 1, 2...)."""
    name: Optional[str]
    """A label for the measure. Typically used for distinguishing between measures with the same number (as in '16a', 
    '16b', '16c') or rehearsal marks."""
    time_signature: Optional[str]
    """A label for the time signature. Typically this takes the form of `<int>/<int>', as for example in '3/8'. For 
    unmetered entries we propose 'null', in which case the 'actual_length' must be specified."""
    nominal_length: Optional[float]
    """The default duration derived from the given 'time_signature', in quarter notes."""
    actual_length: Optional[float]
    """The actual duration of the measure, in quarter notes."""
    start_repeat: Optional[bool]
    """Typical usage is with the bool type, with 'true' indicating a start repeat at the beginning of the measure."""
    end_repeat: Optional[bool]
    """Typical usage is with the bool type, with 'true' indicating an end repeat at the end of the measure."""
    next: Optional[list[int]]
    """A list of measure IDs that follow this measure."""

@dataclass(kw_only=True)
class Measure(PMeasure):
    ID: Optional[str] = None
    count: Optional[int] = None
    qstamp: Optional[Number] = None
    number: Optional[int] = None
    name: Optional[str] = None
    time_signature: Optional[str] = None
    nominal_length: Optional[Number] = None
    actual_length: Optional[Number] = None
    start_repeat: Optional[bool] = None
    end_repeat: Optional[bool] = None
    next: Optional[list[int]] = None

    def __post_init__(self):
        if self.ID is None and self.count is None:
            raise ValueError("Either ID or count must be set")
        if self.ID is None:
            self.ID = str(self.count)
        if self.count is not None:
            self.count = int(self.count)
        if self.qstamp is not None:
            assert isinstance(self.qstamp, Number), (f"qstamp must be a number, got {type(self.qstamp)!r}: "
                                                     f"{self.qstamp}!r")
            assert self.qstamp >= 0, f"qstamp must be positive, got {self.qstamp!r}"
        if self.number is not None:
            self.number = int(self.number)
        if self.name is not None:
            self.name = str(self.name)
        if self.time_signature is not None:
            self.time_signature = str(self.time_signature)
        if self.nominal_length is not None:
            assert isinstance(self.nominal_length, Number), (f"nominal_length must be a number, got "
                                                             f"{type(self.nominal_length)!r}: {self.nominal_length!r}")
            assert self.nominal_length >= 0, f"nominal_length must be positive, got {self.nominal_length!r}"
        if self.actual_length is not None:
            assert isinstance(self.actual_length, Number), (f"actual_length must be a number, got "
                                                            f"{type(self.actual_length)!r}: {self.actual_length!r}")
            assert self.actual_length >= 0, f"actual_length must be positive, got {self.actual_length!r}"
        if self.start_repeat is not None:
            self.start_repeat = bool(self.start_repeat)
        if self.end_repeat is not None:
            self.end_repeat = bool(self.end_repeat)
        if self.next is not None:
            self.next = list(self.next)

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

if __name__ == '__main__':
    parent = os.path.dirname(os.path.dirname(__file__))
    mm_paths = collect_measure_maps(parent)
    for mm_path in mm_paths:
        print(mm_path)
        with open(mm_path, 'r', encoding='utf-8') as f:
            mm = json.load(f)
        for measure in mm:
            try:
                Measure(**measure)
            except Exception as e:
                print(f"Validation of {measure} failed with:\n{e!r}")

