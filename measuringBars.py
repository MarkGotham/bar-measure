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

class Compare:
    def __init__(self, preferred, other):
        self.other_renumbered = None
        self.preferred_expanded = None
        self.other_expanded = None

        if isinstance(preferred, str):
            self.preferred_score = converter.parse(preferred)
        elif isinstance(preferred, stream.Stream):
            self.preferred_score = preferred
        else:
            raise ValueError("Not a valid input type")

        if isinstance(other, str):
            self.other_score = converter.parse(other)
        elif isinstance(other, stream.Stream):
            self.other_score = other
        else:
            raise ValueError("Not a valid input type")

        self.preferred_measure_map = stream_to_measure_map(self.preferred_score)
        self.other_measure_map = stream_to_measure_map(self.other_score)

        self.preferred_length = len(self.preferred_measure_map)
        self.other_length = len(self.other_measure_map)

        self.diagnosis = []
        self.diagnose()

    def diagnose(self, attempt_fix: bool = False):
        """
        Attempt to diagnose the differences between two measure maps and
        optionally attempt to align them (if argument "fix" is True).
        """

        mismatch_offsets = [measure for measure in self.preferred_measure_map if measure['offset'] !=
                            self.other_measure_map[measure['measure_count'] - 1].get('offset')]
        mismatch_measure_number = [measure for measure in self.preferred_measure_map if measure['measure_number'] !=
                                   self.other_measure_map[measure['measure_count'] - 1].get('measure_number')]
        mismatch_time_signature = [measure for measure in self.preferred_measure_map if measure['time_signature'] !=
                                   self.other_measure_map[measure['measure_count'] - 1].get('time_signature')]
        mismatch_repeats = [measure for measure in self.preferred_measure_map if measure['has_start_repeat'] !=
                            self.other_measure_map[measure['measure_count'] - 1].get('has_start_repeat') or
                            measure['has_end_repeat'] != self.other_measure_map[measure['measure_count'] - 1].get(
            'has_end_repeat')]

        if not mismatch_offsets and not mismatch_measure_number and not mismatch_time_signature and not mismatch_repeats \
                and self.preferred_length == self.other_length:
            for change in self.diagnosis:
                if change[0] == "Join":
                    print(f"Join measures {change[1]} and {change[1] + 1} in the 2nd.")
                elif change[0] == "Split":
                    print(f"Split measure {change[1]} at offset {change[2]} in the 2nd.")
                elif change[0] == "Expand_Repeats":
                    print("Expand the repeats.")  # Update for which measure map needs expanding
                elif change[0] == "Renumber":
                    print("Renumber the measures in the 2nd.")
                elif change[0] == "repeat_marks":
                    print()
                elif change[0] == "Add":
                    print()
                elif change[0] == "Remove":
                    print()
                else:
                    print()
            return

        if self.preferred_length != self.other_length:
            if not self.preferred_expanded:
                self.try_expand()
            else:
                self.compare_lengths()
                for change in self.diagnosis:
                    if change[0] == "Join":
                        self.perform_join(change)
                    elif change[0] == "Split":
                        self.perform_split(change)
                return

        if mismatch_measure_number:
            if not self.other_renumbered:
                self.try_renumber()
            return

        if mismatch_repeats:
            return
            # TODO

        # TODO for each kind of issue and (if attempt_fix) also proposed solution.

    def perform_split(self, change):
        self.other_measure_map.insert(change[1] + 1, self.other_measure_map[change[1]])
        self.other_measure_map[change[1]]['actual_length'] = change[2]
        self.other_measure_map[change[1] + 1]['actual_length'] = self.other_measure_map[change[1] + 1]['actual_length'] - change[2]
        self.other_measure_map[change[1]]['has_start_repeat'] = False
        self.other_measure_map[change[1]]['has_end_repeat'] = False  # Repeats?
        self.other_measure_map[change[1]]['next_measure'] = [change[1] + 1]
        for measure in self.other_measure_map:
            if measure['measure_number'] > change[1]:
                measure['measure_count'] += 1
                measure['measure_number'] += 1
                for next_measure in measure['next_measure']:
                    if next_measure > change[1]:
                        next_measure += 1

    def perform_join(self, change):
        self.other_measure_map[change[1]]['actual_length'] = self.preferred_measure_map[change[1]]['actual_length']
        for next_measure in self.other_measure_map[change[1]]['next_measure']:
            if next_measure > change[1]:
                next_measure -= 1
        del self.other_measure_map[change[1] + 1]
        for measure in self.other_measure_map:
            if measure['measure_number'] > change[1]:
                measure['measure_count'] -= 1
                measure['measure_number'] -= 1
                for next_measure in measure['next_measure']:
                    if next_measure > change[1]:
                        next_measure -= 1

    def try_expand(self):
        self.preferred_expanded = stream_to_measure_map(self.preferred_score.expandRepeats())  # TODO: Expand repeats without music21
        self.other_expanded = stream_to_measure_map(self.other_score.expandRepeats())
        self.diagnosis.append(("Expand_Repeats", "Both"))  # Update for which measure map needs expanding
        self.preferred_measure_map = self.preferred_expanded
        self.other_measure_map = self.other_expanded
        self.preferred_length = len(self.preferred_measure_map)
        self.other_length = len(self.other_measure_map)
        self.diagnose()

    def try_renumber(self):
        self.other_renumbered = self.other_measure_map
        for measure in self.other_renumbered:
            measure['measure_number'] = self.other_measure_map[measure['measure_count'] - 1]['measure_number']
            self.diagnosis.append(("Renumber", "all"))
        self.other_measure_map = self.other_renumbered
        self.other_length = len(self.other_renumbered)

    def compare_lengths(self):
        preferred_step = 0
        other_step = 0

        for i in range(self.preferred_length):
            if self.preferred_measure_map[i + preferred_step]['actual_length'] != \
                    self.other_measure_map[i + other_step]['actual_length']:
                if self.preferred_measure_map[i + preferred_step]['actual_length'] == \
                        self.other_measure_map[i + other_step]['actual_length'] + \
                        self.other_measure_map[i + other_step + 1]['actual_length']:
                    self.diagnosis.append(("Join", i + other_step))
                    other_step += 1
                elif self.preferred_measure_map[i + preferred_step]['actual_length'] + \
                        self.preferred_measure_map[i + preferred_step + 1]['actual_length'] == \
                        self.other_measure_map[i]['actual_length']:
                    self.diagnosis.append(("Split", i + other_step, self.preferred_measure_map[i + preferred_step]['actual_length']))
                    preferred_step += 1


# ------------------------------------------------------------------------------

def stream_to_measure_map(this_stream: stream.Stream, check_parts_match: bool = True) -> list:
    """
    Maps from a music21 stream
    to a possible version of the "measure map".
    The bulk of the work is done by part_to_measure_map
    (see notes there).
    The additional check_parts_match argument defaults to False but
    if True and the score has multiple parts, it will
    check that those parts return the same measurement information.
    """
    if isinstance(this_stream, stream.Part):
        return part_to_measure_map(this_stream)

    if not isinstance(this_stream, stream.Score):
        raise ValueError("Only accepts a stream.Part or stream.Score")

    measure_map = part_to_measure_map(this_stream.parts[0])

    if not check_parts_match:
        return measure_map

    num_parts = len(this_stream.parts)

    if num_parts < 2:
        return measure_map

    for part in range(1, num_parts):
        part_measure_map = part_to_measure_map(this_stream.parts[part])
        if part_measure_map != measure_map:
            raise ValueError(f"Parts 0 and {part} do not match.")

    return measure_map


def part_to_measure_map(this_part: stream.Part) -> list:
    """
    Mapping from a music21.stream.part
    to a "measure map": currently a list of dicts with the following keys:
        'measure_count': int,  # all represented, in natural numbers
        'offset': int | float,  # quarterLength from beginning
        'measure_number' / tag: int | str,  # constraints are conventional only
        'time_signature': str | music21.meter.TimeSignature.ratioString,
        'nominal_length': int | float  # NB can derive nominal_length from TS but not vice versa
        'actual_length': int | float,  # expressed in quarterLength. Could also be as proportion
        'has_start_repeat': bool,
        'has_end_repeat': bool
    """
    sheet_measure_map = []
    go_back_to = 1
    go_forward_from = 1
    time_sig = this_part.getElementsByClass(stream.Measure)[0].timeSignature.ratioString

    """if this_part.recurse().getElementsByClass(stream.Measure)[0].barDuration.quarterLength != \
            this_part.recurse().getElementsByClass(stream.Measure)[0].duration.quarterLength:
        measure_count = 0
    else:
        measure_count = 1  # Is measure_count or measure_number the preferred end numbering?
        # Is anacrusis accounted for in measure.measureNumber? If not, where do we account for it?"""
    measure_count = 1

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
            # Pitches? music21 reliant! evaluation?
        }

        sheet_measure_map.append(measure_dict)
        measure_count += 1

    return sheet_measure_map


# ------------------------------------------------------------------------------

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

def needleman_wunsch(preferred_measure_map, other_measure_map):
    n = len(preferred_measure_map)
    m = len(other_measure_map)
    gap_penalty = 2
    match_score = 10
    mismatch_score = -5  # prioritise one larger gap rather than lots of smaller gaps?

    dp = [[0 for _ in range(m + 1)] for _ in range(n + 1)]
    for i in range(1, n + 1):
        dp[i][0] = dp[i - 1][0] + gap_penalty
    for j in range(1, m + 1):
        dp[0][j] = dp[0][j - 1] + gap_penalty

    for i in range(1, n + 1):
        for j in range(1, m + 1):
            match = dp[i - 1][j - 1] + (match_score if preferred_measure_map[i - 1] == other_measure_map[j - 1] else mismatch_score)
            delete = dp[i - 1][j] + gap_penalty
            insert = dp[i][j - 1] + gap_penalty
            dp[i][j] = max(match, delete, insert)

    preferred_aligned, other_aligned = [], []
    i, j = n, m
    while i > 0 and j > 0:
        score = dp[i][j]
        diag = dp[i - 1][j - 1]
        up = dp[i][j - 1]
        left = dp[i - 1][j]
        if score == left + gap_penalty:
            preferred_aligned.append(preferred_measure_map[i - 1])
            other_aligned.append(None)
            i -= 1
        elif score == up + gap_penalty:
            preferred_aligned.append(None)
            other_aligned.append(other_measure_map[j - 1])
            j -= 1
        elif score == diag + (match_score if preferred_measure_map[i - 1] == other_measure_map[j - 1] else mismatch_score):
            preferred_aligned.append(preferred_measure_map[i - 1])
            other_aligned.append(other_measure_map[j - 1])
            i -= 1
            j -= 1
    while i > 0:
        preferred_aligned.append(preferred_measure_map[i - 1])
        other_aligned.append(None)
        i -= 1
    while j > 0:
        preferred_aligned.append(None)
        other_aligned.append(other_measure_map[j - 1])
        j -= 1

    return preferred_aligned[::-1], other_aligned[::-1]


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
        path = 'Example/measure_map.csv'  # Direction of slashes?

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
        """measure_map = stream_to_measure_map(converter.parse('./Examples/core.mxl'))

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
                           'has_end_repeat': False, 'next_measure': []}])"""

        """temp1 = stream_to_measure_map(converter.parse('./Examples/core.mxl'))
        temp2 = stream_to_measure_map(converter.parse('./Examples/missing_1st_time.mxl'))
        input1 = [measure['actual_length'] for measure in temp1]
        input2 = [measure['actual_length'] for measure in temp2]
        print(input1)
        input1[2] = 4.0
        del input1[3]
        print(input1)
        output1, output2 = needleman_wunsch(input1, input2)
        print("Alignment 1:", output1)
        print("Alignment 2:", output2)

        Compare.__init__()"""


# ------------------------------------------------------------------------------

if __name__ == '__main__':
    unittest.main()
