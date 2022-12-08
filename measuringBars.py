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

def score_to_parts(path_to_score: str, check_parts_match: bool = True) -> list:
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
        part_measure_map = part_to_measure_map(score.parts[part])
        if part_measure_map != measure_map:
            raise ValueError(f"Parts 0 and {part} do not match.")


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
        'has_start_repeat': bool,
        'has_end_repeat': bool
    """
    sheet_measure_map = []
    measure_count = 1
    go_back_to = 1
    go_forward_from = 1
    time_sig = this_part.getElementsByClass(stream.Measure)[0].timeSignature.ratioString

    for measure in this_part.recurse().getElementsByClass(stream.Measure):
        has_end_repeat = False
        has_start_repeat = False
        next_measure = []

        if measure.timeSignature:
            time_sig = measure.timeSignature.ratioString

        if measure.leftBarline:  # Only way for this to work seems to be to convert to strings? Object equality checks :- known issue with music21
            if str(measure.leftBarline) == str(bar.Repeat(direction='start')):
                has_start_repeat = True
        if measure.rightBarline:
            if str(measure.rightBarline) == str(bar.Repeat(direction='end')):
                has_end_repeat = True

        if has_start_repeat:  # Crude method to add next measure information including for multiple endings from repeats
            go_back_to = measure_count
        elif measure.leftBarline:
            if measure.leftBarline.type == 'regular' and sheet_measure_map[measure_count - 2]['has_end_repeat']:
                sheet_measure_map[go_forward_from - 1]['next_measure'].append(measure_count)
            elif measure.leftBarline.type == 'regular':
                go_forward_from = measure_count - 1
        if has_end_repeat:
            next_measure.append(go_back_to)
        if measure_count + 1 <= len(this_part.recurse().getElementsByClass(stream.Measure)) and \
                not (has_end_repeat and measure_count > go_forward_from != 1):
            next_measure.append(measure_count + 1)

        measure_dict = {
            'measure_count': measure_count,
            'offset': measure.offset,
            'measure_number': measure.measureNumber,
            'nominal_length': measure.barDuration.quarterLength,
            'actual_length': measure.duration.quarterLength,
            'time_signature': time_sig,
            'has_start_repeat': has_start_repeat,
            'has_end_repeat': has_end_repeat,
            'next_measure': next_measure
        }

        sheet_measure_map.append(measure_dict)
        measure_count += 1

    return sheet_measure_map


# ------------------------------------------------------------------------------

def diagnose(preferred_part: str, other_part: str, attempt_fix: bool = True):
    """
    Attempt to diagnose the differences between two measure maps and
    optionally attempt to align them (if argument "fix" is True).
    """
    preferred_measure_map = score_to_parts(preferred_part)
    other_measure_map = score_to_parts(other_part)

    mismatch_offsets = [measure for measure in preferred_measure_map if measure['offset'] !=
                        other_measure_map[measure['measure_count'] - 1].get('offset')]
    mismatch_measure_number = [measure for measure in preferred_measure_map if measure['measure_number'] !=
                               other_measure_map[measure['measure_count'] - 1].get('measure_number')]
    mismatch_length = [measure for measure in preferred_measure_map if measure['nominal_length'] !=
                       other_measure_map[measure['measure_count'] - 1].get('nominal_length')]
    mismatch_time_signature = [measure for measure in preferred_measure_map if measure['time_signature'] !=
                               other_measure_map[measure['measure_count'] - 1].get('time_signature')]

    if not mismatch_offsets and not mismatch_measure_number and not mismatch_length and not mismatch_time_signature:
        print("These two measure maps seem to be identical.")

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

def write_measure_map_to_sv(measure_map: list, path: str = None, field_names: list = None, verbose: bool = True):
    """
    Writes a measure map to a tsv or csv file.
    """
    dictionary_keys = ['measure_count', 'offset', 'measure_number', 'nominal_length', 'actual_length', 'time_signature',
                       'has_start_repeat', 'has_end_repeat', 'next_measure']
    data = []

    if field_names is None:
        field_names = dictionary_keys
    elif not set(field_names).issubset(set(dictionary_keys)):
        raise ValueError("field_names contains key not stored in the measure map.")
    for i in range(len(measure_map)):
        data.append({})
        for given_key in field_names:
            data[i][given_key] = measure_map[i].get(given_key)

    if path is None:
        path = 'Example/measure_map.csv'

    with open(path, 'w', encoding='UTF8', newline='') as file:
        writer = csv.DictWriter(file, fieldnames=field_names, quoting=csv.QUOTE_NONNUMERIC)
        writer.writeheader()
        if not verbose:
            writer.writerow(data[0])
            for i in range(1, len(data)):
                for name in dictionary_keys:
                    if measure_map[i].get(name) != measure_map[i - 1].get(name) and \
                            name not in ['measure_count', 'offset', 'measure_number', 'next_measure']:
                        writer.writerow(data[i])
                        break
        else:
            writer.writerows(data)


# ------------------------------------------------------------------------------

class Test(unittest.TestCase):
    """
    First test example. More to follow.
    """

    def test_example_case(self):
        measure_map = score_to_parts('./Example/measuringBarsExample.mxl')

        self.assertEqual(measure_map,
                         [{'measure_count': 1, 'offset': 0.0, 'measure_number': 0, 'nominal_length': 4.0,
                           'actual_length': 1.0, 'time_signature': '4/4', 'has_start_repeat': False,
                           'has_end_repeat': False, 'next_measure': [2]},
                          {'measure_count': 2, 'offset': 1.0, 'measure_number': 1, 'nominal_length': 4.0,
                           'actual_length': 4.0, 'time_signature': '4/4', 'has_start_repeat': False,
                           'has_end_repeat': False, 'next_measure': [3]},
                          {'measure_count': 3, 'offset': 5.0, 'measure_number': 2, 'nominal_length': 4.0,
                           'actual_length': 3.0, 'time_signature': '4/4', 'has_start_repeat': False,
                           'has_end_repeat': True, 'next_measure': [1, 4]},
                          {'measure_count': 4, 'offset': 8.0, 'measure_number': 3, 'nominal_length': 4.0,
                           'actual_length': 1.0, 'time_signature': '4/4', 'has_start_repeat': True,
                           'has_end_repeat': False, 'next_measure': [5]},
                          {'measure_count': 5, 'offset': 9.0, 'measure_number': 4, 'nominal_length': 4.0,
                           'actual_length': 4.0, 'time_signature': '4/4', 'has_start_repeat': False,
                           'has_end_repeat': False, 'next_measure': [6, 8]},
                          {'measure_count': 6, 'offset': 13.0, 'measure_number': 5, 'nominal_length': 4.0,
                           'actual_length': 4.0, 'time_signature': '4/4', 'has_start_repeat': False,
                           'has_end_repeat': False, 'next_measure': [7]},
                          {'measure_count': 7, 'offset': 17.0, 'measure_number': 6, 'nominal_length': 4.0,
                           'actual_length': 3.0, 'time_signature': '4/4', 'has_start_repeat': False,
                           'has_end_repeat': True, 'next_measure': [4]},
                          {'measure_count': 8, 'offset': 20.0, 'measure_number': 7, 'nominal_length': 4.0,
                           'actual_length': 4.0, 'time_signature': '4/4', 'has_start_repeat': False,
                           'has_end_repeat': False, 'next_measure': [9]},
                          {'measure_count': 9, 'offset': 24.0, 'measure_number': 8, 'nominal_length': 4.0,
                           'actual_length': 4.0, 'time_signature': '4/4', 'has_start_repeat': False,
                           'has_end_repeat': False, 'next_measure': [10]},
                          {'measure_count': 10, 'offset': 28.0, 'measure_number': 9, 'nominal_length': 4.0,
                           'actual_length': 3.0, 'time_signature': '4/4', 'has_start_repeat': False,
                           'has_end_repeat': False, 'next_measure': []}])

        write_measure_map_to_sv(measure_map)
        print(score_to_parts('./Example/measuringBarsExample.mxl'))
        """
        diagnose('./Example/measuringBarsExample.mxl', './Example/measuringBarsExample2.mxl')
        temp = converter.parse('./Example/measuringBarsExample.mxl')
        for measure in temp.parts[0].getElementsByClass(stream.Measure):
            print(measure.leftBarline, measure.rightBarline)
        """


# ------------------------------------------------------------------------------

if __name__ == '__main__':
    unittest.main()
