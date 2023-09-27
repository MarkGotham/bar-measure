"""

NAME:
===============================
music21 Application (music21_application.py)


LICENCE:
===============================
Creative Commons Attribution-ShareAlike 4.0 International License
https://creativecommons.org/licenses/by-sa/4.0/


ABOUT:
===============================
The measure map processing is platform neutral.
This module implements demonstration using music21:
- creation of measure maps from files in any format that music21 can parse (e.g., musicXML),
- attempts to fix score in-place based on the measure map diagnosis comparison

"""

# ------------------------------------------------------------------------------

import csv
import json
from pathlib import Path

from music21 import bar, clef, converter, key, meter, stream
from typing import Dict

from . import measuring_bars
from . import REPO_FOLDER


# ------------------------------------------------------------------------------

class Aligner:
    def __init__(
        self,
        path_to_preferred: Path,
        path_to_other: Path,
        impose_numbering_first: bool = True,
        write_maps: bool = True,
        write_diagnosis: bool = True,
        attempt_fix: bool = False,
        check_parts_match: bool = True
    ):

        # Paths
        self.path_to_preferred = path_to_preferred
        self.path_to_other = path_to_other

        # Parse preferred
        if self.path_to_preferred.suffix in [".txt", ".rntxt"]:
            self.preferred = converter.parse(self.path_to_preferred, format="Romantext")
        else:
            self.preferred = converter.parse(self.path_to_preferred)

        # Parse other
        if self.path_to_other.suffix in [".txt", ".rntxt"]:
            self.other = converter.parse(self.path_to_other, format="Romantext")
        else:
            self.other = converter.parse(self.path_to_other)

        if impose_numbering_first:
            for part in self.preferred.getElementsByClass(stream.Part):
                impose_numbering_standard(part, "Full Measure")
            for part in self.other.getElementsByClass(stream.Part):
                impose_numbering_standard(part, "Full Measure")  # TODO: Have at start?

        # Prepare MMs
        self.preferred_measure_map = stream_to_measure_map(self.preferred, check_parts_match)
        self.other_measure_map = stream_to_measure_map(self.other, check_parts_match)

        if write_maps:
            self.write_mm()  # before changes in place

        # Comparison
        self.comparison = measuring_bars.Compare(
            self.preferred_measure_map,
            self.other_measure_map,
            attempt_fix=attempt_fix,
            # write_modifications=write_modifications  # doesn't do anything
        )
        self.error = [x for x in self.comparison.diagnosis if x[0] == "Needleman-Wunsch"]

        if self.attempt_fix and not self.error:
            self.attempt_fix()

        if write_diagnosis:
            measuring_bars.write_diagnosis(
                self.comparison.diagnosis,
                outpath=self.path_to_preferred.parent
            )

    def write_mm(self, outpath: Path = None):
        """Write the measure maps"""
        if outpath is not None:
            preferred_outpath = outpath / "preferred.measuremap.json"
            other_outpath = outpath / "other.measuremap.json"
        else:
            preferred_outpath = self.path_to_preferred.parent / "preferred.measuremap.json"
            other_outpath = self.path_to_other.parent / "other.measuremap.json"

        write_measure_map(self.preferred_measure_map, outpath=preferred_outpath)
        write_measure_map(self.other_measure_map, outpath=other_outpath)

    def attempt_fix(self):
        for change in self.comparison.diagnosis:  # TODO: multiple parts?
            for part in self.other.getElementsByClass(stream.Part):
                if change[0] == "Join":
                    join_measures(part, change)
                elif change[0] == "Split":
                    split_measure(part, change)
                elif change[0] == "Expand_Repeats":
                    expand_repeats(self.other)
                elif change[0] == "Renumber":
                    impose_numbering_standard(part, "Full Measure")
                elif change[0] == "Repeat_Marks":
                    copy_repeat_marks(part, change)
                elif change[0] == "Measure_Length":
                    copy_length(part, change)
                elif change[0] == "Time_Signature":
                    copy_time_signature(part, change)
                    removeDuplicates(part)

    def write_modified(self):
        self.other.write("mxl", self.path_to_other.parent / "modified_other.mxl")
        self.preferred.write("mxl", self.path_to_preferred.parent / "modified_preferred.mxl")


def generate_examples(
        path_to_examples: Path = REPO_FOLDER / "Examples"):
    """
    Generates json files of the measure map for each of our example mxl file in a specified folder
    """

    for file in path_to_examples.rglob("*.mxl"):
        score = converter.parse(file)
        measure_map = stream_to_measure_map(score)
        write_measure_map(
            measure_map,
            outpath=path_to_examples / (file.stem + ".measuremap.json")
        )


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
        "count": int,  # all represented, in natural numbers
        "qstamp": int | float,  # quarterLength from beginning
        "number" / tag: int | str,  # constraints are conventional only
        "time_signature": str | music21.meter.TimeSignature.ratioString,
        "nominal_length": int | float  # NB can derive nominal_length from TS but not vice versa
        "actual_length": int | float,  # expressed in quarterLength. Could also be as proportion
        "start_repeat": bool,
        "end_repeat": bool
        "next": lst of str
    """

    sheet_measure_map = []
    go_back_to = 1
    go_forward_from = 1
    time_sig = this_part.getElementsByClass(stream.Measure)[0].timeSignature.ratioString
    count = 1

    for measure in this_part.recurse().getElementsByClass(stream.Measure):
        end_repeat = False
        start_repeat = False
        next = []

        if measure.timeSignature:
            time_sig = measure.timeSignature.ratioString

        if measure.leftBarline:  # TODO: Replace with normal equality checks
            if str(measure.leftBarline) == str(bar.Repeat(direction="start")):
                start_repeat = True
        if measure.rightBarline:
            if str(measure.rightBarline) == str(bar.Repeat(direction="end")):
                end_repeat = True

        if start_repeat:  # Crude method to add next measure information including for multiple endings from repeats
            go_back_to = count
        elif measure.leftBarline:
            if measure.leftBarline.type == "regular" and sheet_measure_map[count - 2]["end_repeat"]:
                sheet_measure_map[go_forward_from - 1]["next"].append(count)
            elif measure.leftBarline.type == "regular":
                go_forward_from = count - 1
        if end_repeat:
            next.append(go_back_to)
        if count + 1 <= len(this_part.recurse().getElementsByClass(stream.Measure)) and \
                not (end_repeat and count > go_forward_from != 1):
            next.append(count + 1)

        measure_dict = {
            "count": count,
            "qstamp": measure.qstamp,
            "number": measure.measureNumber,
            # "suffix": measure.suffix,
            "nominal_length": measure.barDuration.quarterLength,
            "actual_length": measure.duration.quarterLength,
            "time_signature": time_sig,
            "start_repeat": start_repeat,
            "end_repeat": end_repeat,
            "next": next
        }

        sheet_measure_map.append(measure_dict)
        count += 1

    return sheet_measure_map


# ------------------------------------------------------------------------------

def split_measure(part_to_fix: stream.Part, diagnosis: tuple):
    """
    Split one measure on a part defined by the tuple in the form ("split", count, qstamp)
    """

    assert diagnosis[0] == "Split"
    assert len(diagnosis) == 3
    assert isinstance(diagnosis[1], int)
    assert isinstance(diagnosis[2], float)

    measure = part_to_fix.getElementsByClass(stream.Measure)[diagnosis[1] - 1]
    qstamp = measure.qstamp
    first_part, second_part = measure.splitAtQuarterLength(diagnosis[2])
    # second_part.removeClasses()  # TODO?
    second_part.number = first_part.measureNumber
    first_part.numberSuffix = "a"
    second_part.numberSuffix = "b"
    part_to_fix.insert(qstamp + diagnosis[2], second_part)
    removeDuplicates(part_to_fix)  # stream.tools.removeDuplicates(part_to_fix)


def join_measures(part_to_fix: stream.Part, diagnosis: tuple) -> stream.Part:
    """
    Join two measures into one on a part (`part_to_fix`)
    defined by the `diagnosis` tuple in the form ("Join", count)
    where the `count` is the index of the first measure to be joined to the one that
    immediately follows.

    Note: it bears repeating that this is
    enforced for consecutive measures only and that
    the indexing is based on `count`, i.e., not number.
    This behaviour may change, e.g., to admit an option for specifying measure by number.
    """

    assert diagnosis[0] == "Join"
    assert len(diagnosis) == 2
    assert isinstance(diagnosis[1], int)

    measures = part_to_fix.getElementsByClass(stream.Measure)
    target_measure = measures[diagnosis[1] - 1]
    source_measure = measures[diagnosis[1]]  # NB enforced consecutive
    base_ql = target_measure.quarterLength

    for x in source_measure:
        target_measure.insert(base_ql + x.qstamp, x)

    part_to_fix.remove(source_measure)

    return part_to_fix


def expand_repeats(part_to_fix: stream.Stream):
    """
    Expand all the repeats in a part
    """

    expanded = part_to_fix.expandRepeats()
    for part in expanded.getElementsByClass(stream.Part):
        measures = part.getElementsByClass(stream.Measure)
        for measure in measures:
            if measure.measureNumber > 0:
                measure.leftBarline = None
                measure.rightBarline = None
        measures[-1].rightBarline = bar.Barline(type="final")
    # TODO: music21 keeps repeat Clef and TimeSig
    removeDuplicates(expanded)  # stream.tools.removeDuplicates(expanded_part)
    # expanded_part.show()
    return expanded


def copy_repeat_marks(part_to_fix: stream.Part, diagnosis: tuple):
    """
    Copy the repeat markings from the preferred part to the other part
    """

    assert diagnosis[0] == "Repeat_Marks"
    assert len(diagnosis) == 3
    assert isinstance(diagnosis[1], int)
    assert isinstance(diagnosis[2], str)

    measure = part_to_fix.getElementsByClass(stream.Measure)[diagnosis[1] - 1]
    if diagnosis[2] == "start":
        measure.leftBarline = bar.Repeat(direction="start")
    elif diagnosis[2] == "end":
        measure.rightBarline = bar.Repeat(direction="end")


def copy_length(part_to_fix: stream.Part, diagnosis: tuple):
    """
    Copy the actual_length from the preferred part to the other part
    """

    assert diagnosis[0] == "Measure_Length"
    assert len(diagnosis) == 3
    assert isinstance(diagnosis[1], int)
    assert isinstance(diagnosis[2], float)

    measure = part_to_fix.getElementsByClass(stream.Measure)[diagnosis[1] - 1]
    measure.duration.quarterLength = diagnosis[2]


def copy_time_signature(part_to_fix: stream.Part, diagnosis: tuple):
    """
    Copy the time_signature from the preferred part to the other part
    """

    assert diagnosis[0] == "Time_Signature"
    assert len(diagnosis) == 3
    assert isinstance(diagnosis[1], int)
    assert isinstance(diagnosis[2], str)

    measure = part_to_fix.getElementsByClass(stream.Measure)[diagnosis[1] - 1]
    measure.timeSignature = meter.TimeSignature(diagnosis[2])


def impose_numbering_standard(part_to_fix: stream.Part, standard: str = None):
    """
    Impose a standard for numbering measure.

    1 = "Measure Count"
    Simple natural number count for each measure, regardless of length.

    2 = "Full measures"
    - One count per full measure
    - 0 for an initial anacrusis
    - 1, 2, 3, ... for each subsequent full measures
    - Split measures = same count: Xa and Xb.

    This can be used as a fix for known issues, or
    preemptively to attempt to enforce identical numbering in the first place
    (before even extracting the measure maps).
    """

    measure_list = part_to_fix.getElementsByClass(stream.Measure)
    if standard == "Full Measure":
        count = 0
        for index in range(len(measure_list) - 1):
            measure = measure_list[index]
            if measure.quarterLength + measure_list[index + 1].quarterLength == measure.barDuration.quarterLength:
                count += 1
                measure.number = count
                measure.numberSuffix = "a"
            elif measure.quarterLength + measure_list[index - 1].quarterLength == measure_list[index - 1].barDuration.quarterLength and index != 0:
                measure_list[index].number = count
                measure_list[index].numberSuffix = "b"
            elif measure_list[index].duration.quarterLength != measure_list[index].barDuration and index == 0:
                measure_list[0].number = count
            else:
                count += 1
                measure.number = count
            # print(measure)
        count += 1
        measure_list[-1].number = count
    elif standard == "Measure Count":
        count = 1
        for measure in measure_list:
            measure.number = count
            count += 1
    else:
        raise ValueError("Invalid measuring standard.")

    return part_to_fix


# ------------------------------------------------------------------------------

def write_measure_map(
        measure_map: list,
        field_names: list = None,
        verbose: bool = True,
        outpath: Path = None,
        outformat: str = "json"
) -> None:
    """
    Writes a measure map to a tabular (tsv or csv) or json file.
    """

    dictionary_keys = [
        "count",
        "qstamp",
        "number",
        # "suffix",
        "nominal_length",
        "actual_length",
        "time_signature",
        "start_repeat",
        "end_repeat",
        "next"
    ]

    data = []

    if field_names is None:
        field_names = dictionary_keys
    elif not set(field_names).issubset(set(dictionary_keys)):
        raise ValueError("field_names contains key not stored in the measure map.")

    for i in range(len(measure_map)):
        data.append({})
        for given_key in field_names:
            data[i][given_key] = measure_map[i].get(given_key)

    if outpath is None:
        path = Path(".") / f"measure_map.{outformat}"

    if outformat == "json":
        with open(outpath, "w") as file:
            json.dump(data, file, indent=4)

    elif outformat == "csv" or "tsv":
        with open(outpath, "w", encoding="UTF8", newline="") as file:

            delimiter = ","
            if outformat == "tsv":
                delimiter = "\t"

            writer = csv.DictWriter(file,
                                    fieldnames=field_names,
                                    quoting=csv.QUOTE_NONNUMERIC
                                    )
            writer.writeheader()
            if not verbose:
                writer.writerow(data[0])
                for i in range(1, len(data)):
                    for name in dictionary_keys:
                        if measure_map[i].get(name) != measure_map[i - 1].get(name) and \
                                name not in ["count", "qstamp", "number", "next", "suffix"]:
                            writer.writerow(data[i])
                            break
            else:
                writer.writerows(data)
    else:
        raise ValueError(f"Unsupported file format: {outformat}")


# ------------------------------------------------------------------------------

def removeDuplicates(
        thisStream: stream.Stream,
        classesToRemove: tuple = (meter.TimeSignature, key.KeySignature, clef.Clef),
        inPlace: bool = True
) -> stream.Stream:
    """
    Duplicate of music21's removeDuplicates function,
    included here until it is available via stable release
    TODO: remove
    """

    from music21.base import Music21Object

    supportedClasses = (meter.TimeSignature, key.KeySignature, clef.Clef)

    removalDict: Dict[stream.Stream, list[Music21Object]] = {}

    if not inPlace:
        thisStream = thisStream.coreCopyAsDerivation("removeDuplicates")

    if isinstance(thisStream, stream.Score):
        if len(thisStream.parts) > 0:
            for p in thisStream.parts:
                removeDuplicates(p, classesToRemove=classesToRemove, inPlace=True)

    for thisClass in classesToRemove:

        if not any(issubclass(thisClass, supportedClass) for supportedClass in supportedClasses):
            raise ValueError(f"Invalid class. Only {supportedClasses} are supported.")

        allStates = thisStream.recurse().getElementsByClass(thisClass)

        if len(allStates) < 2:  # Not used, or doesn't change
            continue

        currentState = allStates[0]  # First to initialize: can't be a duplicate
        for thisState in allStates[1:]:
            if thisState == currentState:
                if thisState.activeSite in removalDict:  # May be several in same (e.g., measure)
                    removalDict[thisState.activeSite].append(thisState)
                else:
                    removalDict[thisState.activeSite] = [thisState]
            else:
                currentState = thisState

    for activeSiteKey, valuesToRemove in removalDict.items():
        activeSiteKey.remove(valuesToRemove, recurse=True)

    return thisStream


def run_corpus(
    base_path: Path = REPO_FOLDER.parent / "When-in-Rome" / "Corpus",
    preferred_name: str = "score.mxl",
    other_name: str = "analysis.txt"
) -> None:
    """
    Run measure map comparisons on a corpus.
    Set up with defaults for a local copy of `When in Rome` where the directory structure has
    pairs of corresponding `preferred` and `other`
    sources in the same folder.
    """
    for pref in base_path.rglob(preferred_name):
        other = pref.parent / other_name
        Aligner(pref, other, attempt_fix=True, write_maps=True, check_parts_match=False, write_diagnosis=True)


# ------------------------------------------------------------------------------

if __name__ == "__main__":
    run_corpus()