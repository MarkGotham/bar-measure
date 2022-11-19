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

from music21 import converter, stream
import unittest


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

    mm = part_to_measure_map(part)

    if not check_parts_match:
        return mm

    num_parts = len(score.parts)

    if num_parts < 2:
        return mm

    for p in range(1, num_parts):
        thisMM = part_to_measure_map(score.part[p])
        if thisMM != mm:
            raise ValueError(f'Parts 0 and {p} do not match.')


def part_to_measure_map(thisPart: stream.Part) -> list:
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
    measure_map = []
    measure_count = 1

    currentTS = 'Fake'

    for m in thisPart.recurse().getElementsByClass(stream.Measure):

        this_measure_dict = {'measure_count': measure_count,
                             'offset': m.offset,
                             'measure_number': m.measureNumber,
                             'nominal_length': m.barDuration.quarterLength,
                             'actual_length': m.duration.quarterLength}

        ts = m.timeSignature
        if ts:
            this_measure_dict['time_signature'] = ts.ratioString
            currentTS = ts.ratioString
        else:
            this_measure_dict['time_signature'] = currentTS

        # TODO: Repeats, first/second time etc

        measure_map.append(this_measure_dict)
        measure_count += 1

    return measure_map


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

def write_measure_map_to_sv(measure_map: dict, verbose: bool = False):
    """
    Writes a measure map to a tsv or csv file.
    """
    pass
    # TODO


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
                              'nominal_length': 4.0, 'actual_length': 1.0, 'time_signature': '4/4'},
                             {'measure_count': 2, 'offset': 1.0, 'measure_number': 1,
                              'nominal_length': 4.0, 'actual_length': 4.0, 'time_signature': '4/4'},
                             {'measure_count': 3, 'offset': 5.0, 'measure_number': 2,
                              'nominal_length': 4.0, 'actual_length': 3.0, 'time_signature': '4/4'},
                             {'measure_count': 4, 'offset': 8.0, 'measure_number': 3,
                              'nominal_length': 4.0, 'actual_length': 1.0, 'time_signature': '4/4'},
                             {'measure_count': 5, 'offset': 9.0, 'measure_number': 4,
                              'nominal_length': 4.0, 'actual_length': 4.0, 'time_signature': '4/4'},
                             {'measure_count': 6, 'offset': 13.0, 'measure_number': 5,
                              'nominal_length': 4.0, 'actual_length': 4.0, 'time_signature': '4/4'},
                             {'measure_count': 7, 'offset': 17.0, 'measure_number': 6,
                              'nominal_length': 4.0, 'actual_length': 3.0, 'time_signature': '4/4'},
                             {'measure_count': 8, 'offset': 20.0, 'measure_number': 7,
                              'nominal_length': 4.0, 'actual_length': 4.0, 'time_signature': '4/4'},
                             {'measure_count': 9, 'offset': 24.0, 'measure_number': 8,
                              'nominal_length': 4.0, 'actual_length': 4.0, 'time_signature': '4/4'},
                             {'measure_count': 10, 'offset': 28.0, 'measure_number': 9,
                              'nominal_length': 4.0, 'actual_length': 3.0, 'time_signature': '4/4'}
                         ]
                         )


# ------------------------------------------------------------------------------

if __name__ == '__main__':
    unittest.main()
