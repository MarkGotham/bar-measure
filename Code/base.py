from __future__ import annotations
import json
import os
import warnings
from dataclasses import dataclass, asdict
from numbers import Number
 from typing import Protocol, runtime_checkable, Optional, Sequence, List, Iterator

from Code.utils import time_signature2nominal_length, collect_measure_maps


# region Measure

@runtime_checkable
class PMeasure(Protocol):
    ID: str
    """Any unique string to identify this measure."""
    count: int
    """A simple count of measure units in the described source, using natural numbers starting with 1."""
    qstamp: Optional[float]
    """The symbolic time to have elapsed since the start of the source, measured in quarter notes."""
    number: Optional[int]
    """A number assigned to this measure, which typically follows musical convention, for instance starting with 
    natural 
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
        if self.ID is not None:
            self.ID = str(self.ID)
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

    def get_actual_length(self) -> float:
        """Returns the actual length of the measure in quarter notes, falling back to .get_nominal_length() if the
        actual_length is not specified.

        Raises:
            ValueError:
                If neither the actual_length nor the nominal_length is specified.

        """
        if self.actual_length is not None:
            return float(self.actual_length)
        return time_signature2nominal_length(self.time_signature)

    def get_default_successor(
            self,
            ignore_ids: bool = False
    ) -> Measure:
        """Generates the successor in the MeasureMap based on default values. This method is at the heart of the
        compressed measure map: An entry that is identical to <predecessor>.get_default_successor() can be omitted
        because it can be perfectly restored."""
        return make_default_successor(self, ignore_ids=ignore_ids)

    def get_nominal_length(self) -> float:
        """Returns the nominal length of the measure in quarter notes, falling back to the length implied by the time
        signature if the nominal_length is not specified.

        Raises:
            ValueError:
                If neither the nominal_length nor the time_signature is specified or if the time_signature string
                does not correspond to a fraction.

        """
        if self.nominal_length is not None:
            return float(self.nominal_length)
        if self.time_signature is None:
            raise ValueError(
                f"Cannot compute the nominal_length because neither 'nominal_length' nor "
                f"'time_signature' is specified."
            )
        return time_signature2nominal_length(self.time_signature)  # ValueError if not a fraction


def make_default_successor(
        measure: Measure,
        ignore_ids: bool = False
) -> Measure:
    """Generates the successor in the MeasureMap based on default values. This method is at the heart of the
    compressed measure map: An entry that is identical to <predecessor>.get_default_successor() can be omitted
    because it can be perfectly restored."""
    if not isinstance(measure, Measure):
        raise TypeError(f"measure must be a Measure, got {type(measure)!r}: {measure!r}")
    successor_values = asdict(measure)
    if successor_values["qstamp"] is not None:
        # in order to compute the subsequent qstamp, we need to know the nominal length of the current measure
        try:
            actual_length = measure.get_actual_length()
        except ValueError as e:
            raise ValueError(
                f"Cannot compute the successor's 'qstamp' because the nominal_length is not "
                f"specified and cannot be determined from 'time_signature' = {measure.time_signature}."
            ) from e
        successor_values["qstamp"] += actual_length
    if successor_values['actual_length'] is not None:
        successor_values['actual_length'] = measure.get_nominal_length()
    if ignore_ids:
        successor_values['ID'] = None
    count_field_is_present = successor_values['count'] is not None
    number_field_is_present = successor_values['number'] is not None
    if count_field_is_present:
        successor_values['count'] += 1
    if number_field_is_present:
        successor_values['number'] += 1
    if successor_values['name'] is not None:
        assert number_field_is_present, "Cannot created default 'name' field because 'number' is not specified."
        successor_values['name'] = str(successor_values['number'])
    if successor_values['start_repeat'] is not None:
        successor_values['start_repeat'] = False
    if successor_values['end_repeat'] is not None:
        successor_values['end_repeat'] = False
    if successor_values['next'] is not None:
        if successor_values['next'] == []:
            warnings.warn(f"Encountered 'next' field containing an empty list, which should not happen.")
            if count_field_is_present:
                successor_values['next'] = [successor_values['count'] + 1]
            elif number_field_is_present and not ignore_ids:
                successor_values['next'] = [str(successor_values['number'] + 1)]
            else:
                pass  # leave empty
        else:
            old_next_value = successor_values['next'][0]
            if isinstance(old_next_value, int):
                assert count_field_is_present, "Cannot created default 'next' field with integers because 'count' is " \
                                               "not specified."
                successor_values['next'] = [successor_values['count'] + 1]
            elif isinstance(old_next_value, str):
                assert number_field_is_present, ("Cannot created default 'next' field with strings because 'number' is "
                                                 "not specified.")
                successor_values['next'] = [str(successor_values['number'] + 1)]
            else:
                raise TypeError(f"Unexpected type of 'next' field item: {type(old_next_value)!r}: {old_next_value!r}")
    successor = Measure(**successor_values)
    return successor


# endregion Measure
# region MeasureMap

@runtime_checkable
class PMeasureMap(Protocol):
    entries: Sequence[PMeasure]

    def __iter__(self) -> Iterator[PMeasure]:
        ...


@dataclass()
class MeasureMap(PMeasureMap):
    entries: List[Measure]

    def __post_init__(self):
        assert len(self.entries) > 1, "A MeasureMap must contain at least two entries."
        if any(not isinstance(entry, Measure) for entry in self.entries):
            raise TypeError(f"Entries must be of type Measure.")

    def __iter__(self) -> Iterator[Measure]:
        yield from self.entries

    @classmethod
    def from_dicts(
            cls,
            sequence_of_dicts: dict
    ):
        entries = [Measure(**d) for d in sequence_of_dicts]
        return cls(entries)

    @classmethod
    def from_json_file(
            cls,
            filepath: str
    ):
        with open(filepath, 'r', encoding='utf-8') as f:
            mm_json = json.load(f)
        return cls.from_dicts(mm_json)


if __name__ == '__main__':
    parent = os.path.dirname(os.path.dirname(__file__))
    mm_paths = collect_measure_maps(parent)
    for mm_path in mm_paths:
        print(mm_path)
        MM = MeasureMap.from_json_file(mm_path)
        # prototype of compression algorithm:
        previous_measure = None
        for measure in MM:
            if previous_measure is None:
                previous_measure = measure
                continue
            default_successor = previous_measure.get_default_successor()
            if measure == default_successor:
                print(f"MC {measure.count} can be re-generated from its predecessor.")
            else:
                print(
                    f"MC {measure.count} cannot be re-generated from its predecessor.\n"
                    f"Displaying (predecessor MC {previous_measure.count}, default successor, actual successor MC"
                    f" {measure.count}):"
                    f"\n\t{previous_measure}\n\t{default_successor}\n\t{measure}"
                    )
            previous_measure = measure
