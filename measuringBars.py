"""
===============================
Measuring Bars (measuringBars.py)
===============================

Mark Gotham, 2022


LICENCE:
===============================

Creative Commons Attribution-ShareAlike 4.0 International License
https://creativecommons.org/licenses/by-sa/4.0/


ABOUT:
===============================

Quick and dirty initial steps to get the ball rolling.
More to follow ;)

"""

# ------------------------------------------------------------------------------

from music21 import *
import unittest
import csv


# ------------------------------------------------------------------------------

def score_to_measure_map(path_to_score: str,
                         check_parts_match: bool = False) -> list:
    """
    Maps from a music21 stream
    to a possible version of the "measure map".
    The bulk of the work is done by part_to_measure_map
    (see notes there).
    The additional check_parts_match argument defaults to False but
    if True and the score has multiple parts, it will
    check that those parts return the same measurement information.
    """
    score = converter.parse(path_to_score)
    part = score.parts[0]

    measure_map = part_to_measure_map(part)

    if not check_parts_match:
        return measure_map

    num_parts = len(score.parts)

    if num_parts < 2:
        return measure_map

    for part in range(1, num_parts):
        part_measure_map = part_to_measure_map(score.part[part])
        if part_measure_map != measure_map:
            raise ValueError(f'Parts 0 and {part} do not match.')


def part_to_measure_map(this_part: stream.Part) -> list:
    """
    Mapping from a music21.stream.part
    to a "measure map": currently a list of dicts with the following keys:
        'measure_count': int,  # all represented, in natural numbers
        'offset': int | float,  # quarterLength from beginning
        'measure_number' / tag: int | str,  # constraints are conventional only
        'time_signature': str | music21.meter.TimeSignature,
        'nominal_length': int | float  # NB can derive nominal_length from TS but not vice versa
        'actual_length': int | float,  # expressed in quarterLength. Could also be as proportion
        TODO:
        'has_start_repeat': bool,
        'has_end_repeat': bool
    TODO: any others? 'has_ending': bool?
    """
    sheet_measure_map = []
    measure_count = 1

    has_end_repeat = False
    has_start_repeat = False

    time_sig = this_part.getElementsByClass(stream.Measure)[0].timeSignature.ratioString

    for measure in this_part.recurse().getElementsByClass(stream.Measure):
        if measure.timeSignature:
            time_sig = measure.timeSignature.ratioString

        if measure.leftBarline:
            if measure.leftBarline == bar.Repeat(direction='start'):
                has_start_repeat = True
        if measure.rightBarline:
            if measure.rightBarline == bar.Repeat(direction='end'):
                has_end_repeat = True

        measure_dict = {
            "measure_count": measure_count,
            "offset": measure.offset,
            "measure_number": measure.measureNumber,
            "nominal_length": measure.barDuration.quarterLength,
            "actual_length": measure.duration.quarterLength,
            "time_signature": time_sig,
            "has_start_repeat": has_start_repeat,
            "has_end_repeat": has_end_repeat
        }
        sheet_measure_map.append(measure_dict)
        measure_count += 1

        # TODO: Repeats, first/second time etc

    return sheet_measure_map


# ------------------------------------------------------------------------------

def diagnose(preferred_part: stream.Part,
             other_part: stream.Part,
             attempt_fix: bool = True):
    """
    Attempt to diagnose the differences between two measure maps and
    optionally attempt to align them (if argument "fix" is True).
    """
    preferred_measure_map = part_to_measure_map(preferred_part)
    other_measure_map = part_to_measure_map(other_part)

    if preferred_measure_map == other_measure_map:
        print("The two measure maps are identical, no change needed. Done.")
        return

    if len(preferred_measure_map) == len(other_measure_map):
        print("Different total number of measures, change needed ... ")
        pass
        # TODO for each kind of issue and (if attempt_fix) also proposed solution.


def fix(part_to_fix: stream.Part):
    """
    Having diagnosed the difference(s), attempt to fix one part by:
    - re-numbering the bars
    - expanding/contracting repeats
    etc
    """
    pass
    # TODO


def impose_numbering_standard(part_to_fix: stream.Part):
    """
    Impose the relatively standard practice of numbering measure:
    - 0 for an initial anacrusis
    - 1, 2, 3, ... for each subsequent full measures
    - etc.
    This can be used as a fix for known issues, or
    preemptively to attempt to enforce identical numbering in the first place
    (before even extracting the measure maps).
    """
    pass
    # TODO


# ------------------------------------------------------------------------------

def write_measure_map_to_sv(measure_map: list, path: str = None, field_names: list = None, verbose: bool = False):
    """
    Writes a measure map to a tsv or csv file.
    """
    if field_names is None:
        field_names = ['measure_count', 'offset', 'measure_number', 'nominal_length', 'actual_length', 'time_signature',
                       'has_end_repeat', 'has_start_repeat']
    # elif:
    # if field_names don't match/not subset
    data = measure_map
    if path is None:
        path = 'Example/measure_map.csv'
    with open(path, 'w', encoding='UTF8', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=field_names)
        writer.writeheader()
        writer.writerows(data)

    # Verbose - only sig diff measures


# ------------------------------------------------------------------------------

class Test(unittest.TestCase):
    """
    First test example. More to follow.
    """

    def testExampleCase(self):
        testScore = converter.parse('./Example/measuringBarsExample.mxl')

        mm = part_to_measure_map(testScore.parts[0])

        self.assertEqual(mm,
                         [
                             {'measure_count': 1, 'offset': 0.0, 'measure_number': 0,
                              'nominal_length': 4.0, 'actual_length': 1.0, 'time_signature': '4/4',
                              'has_end_repeat': False,
                              'has_start_repeat': False, },
                             {'measure_count': 2, 'offset': 1.0, 'measure_number': 1,
                              'nominal_length': 4.0, 'actual_length': 4.0, 'time_signature': '4/4',
                              'has_end_repeat': False,
                              'has_start_repeat': False, },
                             {'measure_count': 3, 'offset': 5.0, 'measure_number': 2,
                              'nominal_length': 4.0, 'actual_length': 3.0, 'time_signature': '4/4',
                              'has_end_repeat': False,
                              'has_start_repeat': False, },
                             {'measure_count': 4, 'offset': 8.0, 'measure_number': 3,
                              'nominal_length': 4.0, 'actual_length': 1.0, 'time_signature': '4/4',
                              'has_end_repeat': False,
                              'has_start_repeat': False, },
                             {'measure_count': 5, 'offset': 9.0, 'measure_number': 4,
                              'nominal_length': 4.0, 'actual_length': 4.0, 'time_signature': '4/4',
                              'has_end_repeat': False,
                              'has_start_repeat': False, },
                             {'measure_count': 6, 'offset': 13.0, 'measure_number': 5,
                              'nominal_length': 4.0, 'actual_length': 4.0, 'time_signature': '4/4',
                              'has_end_repeat': False,
                              'has_start_repeat': False, },
                             {'measure_count': 7, 'offset': 17.0, 'measure_number': 6,
                              'nominal_length': 4.0, 'actual_length': 3.0, 'time_signature': '4/4',
                              'has_end_repeat': False,
                              'has_start_repeat': False, },
                             {'measure_count': 8, 'offset': 20.0, 'measure_number': 7,
                              'nominal_length': 4.0, 'actual_length': 4.0, 'time_signature': '4/4',
                              'has_end_repeat': False,
                              'has_start_repeat': False, },
                             {'measure_count': 9, 'offset': 24.0, 'measure_number': 8,
                              'nominal_length': 4.0, 'actual_length': 4.0, 'time_signature': '4/4',
                              'has_end_repeat': False,
                              'has_start_repeat': False, },
                             {'measure_count': 10, 'offset': 28.0, 'measure_number': 9,
                              'nominal_length': 4.0, 'actual_length': 3.0, 'time_signature': '4/4',
                              'has_end_repeat': False,
                              'has_start_repeat': False, }
                         ]
                         )

        write_measure_map_to_sv(mm)


# ------------------------------------------------------------------------------

if __name__ == '__main__':
    unittest.main()
