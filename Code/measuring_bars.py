"""

NAME:
===============================
Measuring Bars (measuring_bars.py)


LICENCE:
===============================
Creative Commons Attribution-ShareAlike 4.0 International License
https://creativecommons.org/licenses/by-sa/4.0/


ABOUT:
===============================
Platform-neutral functionality for the comparison and alignment of musical sources.
This module focuses exclusively on lightweight measure map files.
Other modules provide format-specific applications (e.g., see music21_application).

"""

import json
from pathlib import Path
from . import REPO_FOLDER


# ------------------------------------------------------------------------------

class Compare:
    def __init__(
        self,
        preferred: list[dict],
        other: list[dict],
        attempt_fix: bool = False,
        write_modifications: bool = False
    ):
        self.preferred_mm = preferred
        self.other_mm = other
        self.expanded_flag = False
        self.renumbered_flag = False
        self.attempt_fix = attempt_fix
        self.write_modifications = write_modifications

        self.preferred_length = len(self.preferred_mm)
        self.other_length = len(self.other_mm)

        self.old_preferred = preferred
        self.old_other = other  # TODO: remove?

        self.diagnosis = []
        self.attempted_changes = []
        self.diagnose()

    def diagnose(self):
        """
        Attempt to diagnose the differences between two measure maps and
        optionally attempt to align them (if argument "fix" is True).
        """

        self.preferred_length = len(self.preferred_mm)
        self.other_length = len(self.other_mm)

        mismatch_qstamps = False
        mismatch_number = False
        mismatch_time_signature = False
        mismatch_repeats = False
        mismatch_actual_lengths = False
        mismatch_nominal_lengths = False
        repeats = False

        for i in range(min(self.preferred_length, self.other_length)):
            if self.preferred_mm[i]["qstamp"] != self.other_mm[i].get("qstamp"):
                mismatch_qstamps = True
            if self.preferred_mm[i]["number"] != self.other_mm[i].get("number"):
                mismatch_number = True
            if self.preferred_mm[i]["time_signature"] != self.other_mm[i].get("time_signature"):
                mismatch_time_signature = True
            if self.preferred_mm[i]["start_repeat"] != self.other_mm[i].get("start_repeat") \
                    or self.preferred_mm[i]["end_repeat"] != self.other_mm[i].get("end_repeat"):
                mismatch_repeats = True
            if self.preferred_mm[i]["actual_length"] != self.other_mm[i]["actual_length"]:
                mismatch_actual_lengths = True
            if self.preferred_mm[i]["nominal_length"] != self.other_mm[i]["nominal_length"]:
                mismatch_nominal_lengths = True

            if self.other_mm[i].get("end_repeat") is True:
                repeats = True

        # print(self.other_mm)

        if all(not x for x in [mismatch_qstamps,
                               mismatch_number,
                               mismatch_time_signature,
                               mismatch_repeats,
                               mismatch_actual_lengths,
                               mismatch_nominal_lengths
                               ]
               ) and not self.preferred_length == self.other_length:
            if self.attempt_fix or self.write_modifications:  # TODO implement write_modifications
                return self.diagnosis
            else:
                return self.other_mm

        if self.preferred_length != self.other_length:
            self.compare_lengths()
            for change in self.diagnosis:
                if change not in self.attempted_changes:
                    if change[0] == "Join":
                        self.other_mm = perform_join(self.other_mm, change)
                        self.other_length = len(self.other_mm)
                        self.attempted_changes.append(change)
                    elif change[0] == "Split":
                        self.other_mm = perform_split(self.other_mm, change)
                        self.other_length = len(self.other_mm)
                        self.attempted_changes.append(change)
            if self.preferred_length == self.other_length:
                self.diagnose()
            else:
                if not self.expanded_flag and repeats:
                    self.preferred_mm = perform_expand_repeats(self.preferred_mm)
                    self.preferred_length = len(self.preferred_mm)
                    self.other_mm = perform_expand_repeats(self.other_mm)
                    self.other_length = len(self.other_mm)
                    self.expanded_flag = True
                    self.diagnosis.append(("Expand_Repeats", "Both"))
                    self.diagnose()
                else:
                    preferred_aligned, other_aligned = needleman_wunsch(self.old_preferred,
                                                                        self.old_other
                                                                        )
                    self.diagnosis.append(
                        ("Needleman-Wunsch", preferred_aligned, other_aligned)
                    )
                    # self.diagnosis.append("test")  # TODO: fix
                    return self.diagnosis
                    # TODO: worst case scenario?

        elif mismatch_repeats:  # Above mismatch_number, fails otherwise
            for i in range(self.preferred_length):
                if self.preferred_mm[i]["start_repeat"] != self.other_mm[i]["start_repeat"]:
                    self.diagnosis.append(
                        ("Repeat_Marks", self.preferred_mm[i]["count"], "start")
                    )
                if self.preferred_mm[i]["end_repeat"] != self.other_mm[i]["end_repeat"]:
                    self.diagnosis.append(
                        ("Repeat_Marks", self.preferred_mm[i]["count"], "end")
                    )
            perform_repeat_copy(self.preferred_mm, self.other_mm)
            self.diagnose()

        elif mismatch_number:
            if not self.renumbered_flag:
                self.other_mm = try_renumber(self.other_mm, self.preferred_mm)
                self.other_length = len(self.other_mm)
                self.diagnosis.append(("Renumber", "all"))
                self.renumbered_flag = True
                self.diagnose()

        elif mismatch_actual_lengths:
            for i in range(self.preferred_length):
                if self.preferred_mm[i]["actual_length"] != self.other_mm[i]["actual_length"]:
                    self.diagnosis.append(
                        ("Measure_Length", i + 1, self.preferred_mm[i]["actual_length"])
                    )
            perform_actual_length_copy(self.preferred_mm, self.other_mm)
            self.diagnose()

        elif mismatch_time_signature:
            for i in range(self.preferred_length):
                if self.preferred_mm[i]["time_signature"] != self.other_mm[i]["time_signature"]:
                    self.diagnosis.append(
                        ("Time_Signature", i + 1, self.preferred_mm[i]["time_signature"])
                    )
            perform_time_signature_copy(self.preferred_mm, self.other_mm)
            self.diagnose()

        elif mismatch_qstamps:
            perform_qstamp_recalculation(self.other_mm)
            self.diagnose()  # TODO: diagnosis?

        elif mismatch_nominal_lengths:
            perform_nominal_length_recalculation(self.other_mm)
            self.diagnose()

        return self.other_mm

    def compare_lengths(self):
        i = 0

        while i < self.preferred_length - 1 and i < self.other_length - 1:
            if self.preferred_mm[i]["actual_length"] == \
                    self.other_mm[i]["actual_length"] + self.other_mm[i + 1]["actual_length"]:
                self.diagnosis.append(
                    ("Join", i + 1)
                )
            if self.preferred_mm[i]["actual_length"] + self.preferred_mm[i + 1]["actual_length"] \
                    == self.other_mm[i]["actual_length"]:
                self.diagnosis.append(
                    ("Split", i + 1, self.preferred_mm[i]["actual_length"])
                )

            i += 1


# ------------------------------------------------------------------------------

def perform_split(other, change):
    """
    Performs a split on the other measure map
    at the measure count stored in change[1]
    at the offset stored in change[2]
    """

    other.insert(change[1], other[
        change[1] - 1].copy())
    other[change[1]]["qstamp"] += change[2]
    other[change[1] - 1]["actual_length"] = float(change[2])
    other[change[1]]["actual_length"] -= change[2]
    # other[change[1] - 1]["suffix"] = "a"
    # other[change[1]]["suffix"] = "b"
    other[change[1] - 1]["start_repeat"] = False
    other[change[1] - 1]["end_repeat"] = False  # Repeats?
    other[change[1] - 1]["next"] = [other[change[1]]["count"] + 1]

    for i in range(change[1], len(other)):
        other[i]["count"] += 1
        for j in range(len(other[i]["next"])):
            if other[i]["next"][j] > other[change[1] - 1]["count"]:
                other[i]["next"][j] += 1

    return other


def perform_join(other, change):
    """
    Performs join on measure change[1] and change[1] + 1 to form one measure on other measure map.
    """

    other[change[1] - 1]["actual_length"] += other[change[1]]["actual_length"]
    other[change[1] - 1]["end_repeat"] = other[change[1]]["end_repeat"]
    other.pop(change[1])

    for i in range(change[1], len(other)):
        other[i]["count"] -= 1
        other[i]["number"] -= 1
        for j in range(len(other[i]["next"])):
            if other[i]["next"][j] > other[change[1] - 1]["count"]:
                other[i]["next"][j] -= 1

    return other


def try_renumber(preferred, other):
    """
    Renumbers measures in other measure map to match the numbering in the preferred measure map
    """

    for measure in preferred:
        other[measure["count"] - 1]["number"] = measure["number"]
    return other


def perform_repeat_copy(preferred, other):
    """
    Copy the repeat markings from the preferred measure map to the other measure map
    """

    assert len(preferred) == len(other)

    for i in range(len(preferred)):
        other[i]["start_repeat"] = preferred[i]["start_repeat"]
        other[i]["end_repeat"] = preferred[i]["end_repeat"]
        other[i]["next"] = preferred[i]["next"]
    return other


def perform_actual_length_copy(preferred, other):
    """
    Copy the actual_length from the preferred measure map to the other measure map
    """

    assert len(preferred) == len(other)

    for i in range(len(preferred)):
        other[i]["actual_length"] = preferred[i]["actual_length"]
    return other


def perform_time_signature_copy(preferred, other):
    """
    Copy the time_signature from the preferred measure map to the other measure map
    """

    assert len(preferred) == len(other)

    for i in range(len(preferred)):
        other[i]["time_signature"] = preferred[i]["time_signature"]
    return other


def perform_nominal_length_recalculation(other):
    """
    Recalculate the nominal_length using the time_signature
    """

    for i in range(len(other)):
        other[i]["nominal_length"] = float(other[i]["time_signature"].split("/")[0])
    return other


def perform_qstamp_recalculation(other):
    """
    Recalculate the offset using the actual_length
    """

    other[0]["qstamp"] = 0.0

    for i in range(1, len(other)):
        other[i]["qstamp"] = other[i - 1]["qstamp"] + other[i - 1]["actual_length"]
    return other


def perform_expand_repeats(measure_map):
    """
    Expand all the repeats in other measure map
    """

    measure_order = [1]
    i = 0
    while i < len(measure_map) - 1:
        if not measure_map[i]["next"]:
            measure_map[i]["next"].append(measure_map[i]["count"] + 1)
        next = measure_map[i]["next"].pop(0)
        measure_order.append(next)
        i = next - 1

    expanded_map = []
    index = 1
    for measure_count in measure_order:
        expanded_map.append(measure_map[measure_count - 1].copy())
        expanded_map[index - 1]["count"] = index
        expanded_map[index - 1]["next"] = [index + 1]
        expanded_map[index - 1]["start_repeat"] = False
        expanded_map[index - 1]["end_repeat"] = False
        index += 1

    return expanded_map


# ------------------------------------------------------------------------------

def needleman_wunsch(preferred_mm, other_mm):
    """
    A standard alignment algorithm of some (limited) use for this use case.
    # TODO: make output easier to interpret for end user?
    """

    n = len(preferred_mm)
    m = len(other_mm)
    match_score = 1
    mismatch_score = -1
    gap_penalty = -1
    continue_gap_penalty = -1  # TODO: needleman_wunsch to prioritise continuing gaps over new gaps

    preferred_comparer = []
    other_comparer = []
    keys = ["actual_length", "time_signature", "start_repeat", "end_repeat"]

    for x in preferred_mm:
        preferred_comparer.append({y: x[y] for y in keys})
    for x in other_mm:
        other_comparer.append({y: x[y] for y in keys})  # TODO: remove?

    matrix = [[0 for _ in range(m + 1)] for _ in range(n + 1)]

    for i in range(1, n + 1):
        matrix[i][0] = matrix[i - 1][0] + gap_penalty
    for j in range(1, m + 1):
        matrix[0][j] = matrix[0][j - 1] + gap_penalty

    for i in range(1, n + 1):
        for j in range(1, m + 1):
            match = matrix[i - 1][j - 1] + (
                match_score
                if preferred_comparer[i - 1] == other_comparer[j - 1]
                else mismatch_score
            )
            delete = matrix[i - 1][j] + gap_penalty
            insert = matrix[i][j - 1] + gap_penalty
            matrix[i][j] = max(match, delete, insert)

    preferred_aligned, other_aligned = [], []
    i, j = n, m
    while i > 0 and j > 0:
        score = matrix[i][j]
        diag = matrix[i - 1][j - 1]
        up = matrix[i][j - 1]
        left = matrix[i - 1][j]
        if score == left + gap_penalty:
            preferred_aligned.append(preferred_mm[i - 1])
            other_aligned.append(None)
            i -= 1
        elif score == up + gap_penalty:
            preferred_aligned.append(None)
            other_aligned.append(other_mm[j - 1])
            j -= 1
        elif score == diag + (
                match_score
                if preferred_comparer[i - 1] == other_comparer[j - 1]
                else mismatch_score
        ):
            preferred_aligned.append(preferred_mm[i - 1])
            other_aligned.append(other_mm[j - 1])
            i -= 1
            j -= 1
    while i > 0:
        preferred_aligned.append(preferred_mm[i - 1])
        other_aligned.append(None)
        i -= 1
    while j > 0:
        preferred_aligned.append(None)
        other_aligned.append(other_mm[j - 1])
        j -= 1

    return preferred_aligned[::-1], other_aligned[::-1]


# ------------------------------------------------------------------------------

def write_diagnosis(
        diagnosis: list[list],
        out_path: Path,
        out_name: str = "other_modifications.txt"
) -> None:
    """Write the diagnosis (suggested modifications to the `other` source) in a text file"""
    with open(out_path / out_name, "w") as file:

        if not diagnosis:
            file.write("No changes required to align these two sources.")
            return

        file.write("Changes to be made to secondary measure map:\n")
        joins = [x[1] for x in diagnosis if x[0] == "Join"]
        for change in diagnosis:
            if change[0] == :
                file.write(f" - Join measures {change[1]} and {change[1] + 1}.\n")
            elif change[0] == "Split":
                file.write(f" - Split measure {change[1]} at offset {change[2]}.\n")
            elif change[0] == "Expand_Repeats":
                file.write(" - Expand the repeats.\n")
            elif change[0] == "Renumber":
                file.write(" - Renumber the measures.\n")
            elif change[0] == "Repeat_Marks":
                file.write(f" - Add {change[2]} repeat marks to measure {change[1]}.\n")
            elif change[0] == "Measure_Length":
                file.write(f" - Change measure {change[1]} actual length to {change[2]}.\n")
            elif change[0] == "Time_Signature":
                file.write(f" - Change measure {change[1]} time signature to {change[2]}.\n")


def one_comparison(
        preferred_path: Path,
        other_path: Path,
        write: bool = True
) -> list:
    with open(preferred_path, "r") as file:
        preferred = json.load(file)
    with open(other_path, "r") as file:
        other = json.load(file)
    diagnosis = Compare(preferred, other).diagnosis

    if write:
        write_diagnosis(
            diagnosis,
            preferred_path.parent,
            "other_modifications.txt"
        )

    return diagnosis


def run_corpus(
        base_path: Path = REPO_FOLDER.parent / "Chorale-Corpus",  # "When-in-Rome" / "Corpus",
        preferred_name: str = "preferred_measure_map.json",
        other_name: str = "other_measure_map.json"
) -> None:
    """
    Run comparisons on a corpus of pre-extracted measure maps.
    Set up with defaults for a local copy of `When in Rome` where the directory structure has
    pairs of corresponding `preferred` and `other`
    sources in the same folder.
    """
    for pref_path in base_path.rglob(preferred_name):
        other_path = pref_path.parent / other_name
        one_comparison(pref_path, other_path)


# ------------------------------------------------------------------------------

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()

    parser.add_argument("--run_corpus", action="store_true", )

    args = parser.parse_args()
    if args.run_corpus:
        run_corpus()
    else:
        parser.print_help()
