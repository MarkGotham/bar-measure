"""
===============================
Measuring Bars (measuring_bars.py)
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

from Code.music21_application import stream_to_measure_map


# ------------------------------------------------------------------------------


class Compare:
    def __init__(self, preferred, other):
        self.preferred_measure_map = preferred
        self.other_measure_map = other
        self.other_renumbered = None
        self.expanded_flag = False

        self.output_flag = False

        self.preferred_length = len(self.preferred_measure_map)
        self.other_length = len(self.other_measure_map)

        self.diagnosis = []
        self.attempted_changes = []
        self.diagnose()

    def diagnose(self, attempt_fix: bool = False):
        """
        Attempt to diagnose the differences between two measure maps and
        optionally attempt to align them (if argument "fix" is True).
        """

        self.preferred_length = len(self.preferred_measure_map)
        self.other_length = len(self.other_measure_map)

        mismatch_offsets, mismatch_measure_number, mismatch_time_signature, mismatch_repeats, mismatch_lengths = False, False, False, False, False
        for i in range(min(self.preferred_length, self.other_length)):
            if self.preferred_measure_map[i]['offset'] != self.other_measure_map[i].get('offset'):
                mismatch_offsets = True
            if self.preferred_measure_map[i]['measure_number'] != self.other_measure_map[i].get('measure_number'):
                mismatch_measure_number = True
            if self.preferred_measure_map[i]['time_signature'] != self.other_measure_map[i].get('time_signature'):
                mismatch_time_signature = True
            if self.preferred_measure_map[i]['has_start_repeat'] != self.other_measure_map[i].get('has_start_repeat') \
                    or self.preferred_measure_map[i]['has_end_repeat'] != self.other_measure_map[i].get('has_end_repeat'):
                mismatch_repeats = True
            if self.preferred_measure_map[i]['actual_length'] != self.other_measure_map[i]['actual_length']:
                mismatch_lengths = True

        if not mismatch_offsets and not mismatch_measure_number and not mismatch_time_signature and not \
                mismatch_repeats and not mismatch_lengths and self.preferred_length == self.other_length and \
                not self.output_flag:
            print()
            print("Changes to be made to secondary measure map:")
            for change in self.diagnosis:
                if change[0] == "Join":
                    print(f" - Join measures {change[1]} and {change[1] + 1}.")
                elif change[0] == "Split":
                    print(f" - Split measure {change[1]} at offset {change[2]}.")
                elif change[0] == "Expand_Repeats":
                    print(" - Expand the repeats.")  # Update for which measure map needs expanding?
                elif change[0] == "Renumber":
                    print(" - Renumber the measures in the 2nd.")
                elif change[0] == "Repeat_Marks":
                    print(f" - Add {change[2]} repeat marks to measure {change[1]}.")
                elif change[0] == "Measure_Length":
                    print(f" - Change measure {change[1]}'s actual length to {change[2]}.")
                elif change[0] == "Add":
                    print()
                elif change[0] == "Remove":
                    print()
                else:
                    print()
            print()
            self.output_flag = True
            return self.other_measure_map

        if self.preferred_length != self.other_length:
            self.compare_lengths()
            for change in self.diagnosis:
                if change not in self.attempted_changes:
                    if change[0] == "Join":
                        self.perform_join(change)
                        self.attempted_changes.append(change)
                    elif change[0] == "Split":
                        self.other_measure_map = perform_split(self.other_measure_map, change)
                        self.other_length = len(self.other_measure_map)
                        self.attempted_changes.append(change)
            self.diagnose()
            if self.preferred_length != self.other_length:
                """if self.expanded_flag:  # not self.expanded_flag:
                    self.preferred_measure_map = perform_expand_repeats(self.preferred_measure_map)
                    self.preferred_length = len(self.preferred_measure_map)
                    self.other_measure_map = perform_expand_repeats(self.other_measure_map)
                    self.other_length = len(self.other_measure_map)
                    self.expanded_flag = True
                    self.diagnosis.append(("Expand_Repeats", "Both"))
                    self.diagnose()
                else:
                    # needleman_wunsch"""

        elif mismatch_measure_number:
            if not self.other_renumbered:
                self.try_renumber()
                self.diagnose()

        elif mismatch_repeats:
            for i in range(self.preferred_length):
                if self.preferred_measure_map[i]['has_start_repeat'] != self.other_measure_map[i]['has_start_repeat']:
                    self.diagnosis.append(('Repeat_Marks', self.preferred_measure_map[i]['measure_count'], 'start'))
                if self.preferred_measure_map[i]['has_end_repeat'] != self.other_measure_map[i]['has_end_repeat']:
                    self.diagnosis.append(('Repeat_Marks', self.preferred_measure_map[i]['measure_count'], 'end'))
            perform_repeat_copy(self.preferred_measure_map, self.other_measure_map)
            self.diagnose()

        elif mismatch_lengths:
            for i in range(self.preferred_length):
                if self.preferred_measure_map[i]['actual_length'] != self.other_measure_map[i]['actual_length']:
                    self.diagnosis.append(('Measure_Length', i, self.preferred_measure_map[i]['actual_length']))
            perform_length_copy(self.preferred_measure_map, self.other_measure_map)
            self.diagnose()

        # TODO for each kind of issue and (if attempt_fix) also proposed solution.

        return self.other_measure_map

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

    def try_renumber(self):
        self.other_renumbered = self.other_measure_map
        for measure in self.preferred_measure_map:
            measure['measure_number'] = self.other_measure_map[measure['measure_count'] - 1]['measure_number']
        self.diagnosis.append(("Renumber", "all"))
        self.other_measure_map = self.other_renumbered
        self.other_length = len(self.other_renumbered)

    def compare_lengths(self):
        i = 0

        while i < self.preferred_length - 1 and i < self.other_length - 1:
            if self.preferred_measure_map[i]['actual_length'] == self.other_measure_map[i]['actual_length'] + self.other_measure_map[i + 1]['actual_length']:
                self.diagnosis.append(("Join", i + 1))
            if self.preferred_measure_map[i]['actual_length'] + self.preferred_measure_map[i + 1]['actual_length'] == self.other_measure_map[i]['actual_length']:
                self.diagnosis.append(("Split", i + 1, self.preferred_measure_map[i]['actual_length']))

            i += 1

# ------------------------------------------------------------------------------


def perform_split(other, change):
    """
    Performs split on measure change[1] at offset change[2] on other measure map.
    """
    other.insert(change[1], other[change[1] - 1].copy())  # is change[1] the measure_number or measure_count or index of measure in list?
    other[change[1]]['offset'] += change[2]
    other[change[1] - 1]['actual_length'] = float(change[2])
    other[change[1]]['actual_length'] -= change[2]
    # other[change[1] - 1]['suffix'] = "a"
    # other[change[1]]['suffix'] = "b"
    other[change[1] - 1]['has_start_repeat'] = False
    other[change[1] - 1]['has_end_repeat'] = False  # Repeats?
    other[change[1] - 1]['next_measure'] = [other[change[1]]['measure_count'] + 1]

    for i in range(change[1], len(other)):
        other[i]['measure_count'] += 1
        # other[i]['measure_number'] += 1
        other[i]['next_measure'] = [value + 1 for value in other[i]['next_measure']]

    return other


def perform_repeat_copy(preferred, other):
    assert len(preferred) == len(other)
    for i in range(len(preferred)):
        other[i]['has_start_repeat'] = preferred[i]['has_start_repeat']
        other[i]['has_end_repeat'] = preferred[i]['has_end_repeat']
        other[i]['next_measure'] = preferred[i]['next_measure']
    return other


def perform_length_copy(preferred, other):
    assert len(preferred) == len(other)
    for i in range(len(preferred)):
        other[i]['actual_length'] = preferred[i]['actual_length']
    return other


def perform_expand_repeats(measure_map):
    for measure in measure_map:
        if measure['has_start_repeat'] is True:
            start_measure = measure['measure_count']
        for next_measure in measure['next_measure']:
            if next_measure > measure:
                return
    return measure_map

# ------------------------------------------------------------------------------


def needleman_wunsch(preferred_measure_map, other_measure_map):
    n = len(preferred_measure_map)
    m = len(other_measure_map)
    match_score = 1
    mismatch_score = -1
    gap_penalty = -2  # prioritise one larger gap rather than lots of smaller gaps?
    continue_gap_penalty = -1

    dp = [[0 for _ in range(m + 1)] for _ in range(n + 1)]
    for i in range(1, n + 1):
        dp[i][0] = dp[i - 1][0] + gap_penalty
    for j in range(1, m + 1):
        dp[0][j] = dp[0][j - 1] + gap_penalty

    for i in range(1, n + 1):
        for j in range(1, m + 1):
            match = dp[i - 1][j - 1] + (
                match_score if preferred_measure_map[i - 1] == other_measure_map[j - 1] else mismatch_score)
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
        elif score == diag + (
                match_score if preferred_measure_map[i - 1] == other_measure_map[j - 1] else mismatch_score):
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
