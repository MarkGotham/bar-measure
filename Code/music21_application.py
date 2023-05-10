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
This module implements demonstration using music21.
"""

# ------------------------------------------------------------------------------

import csv
import json
import os
from pathlib import *

from music21 import *
import Code.measuring_bars

REPO_FOLDER = Path(__file__).parent.parent


# ------------------------------------------------------------------------------

class Aligner:
    def __init__(self, path_to_preferred: Path, path_to_other: Path, write: bool = True, outpath: str = None, attempt_fix: bool = False, write_modifications: bool = False, check_parts_match: bool = True):
        # Paths
        self.path_to_preferred = path_to_preferred
        self.path_to_other = path_to_other

        # Parsed
        self.preferred = converter.parse(self.path_to_preferred)
        if self.path_to_other.suffix == '.txt':
            self.other = converter.parse(self.path_to_other, format='Romantext')
        else:
            self.other = converter.parse(self.path_to_other)

        for part in self.preferred.getElementsByClass(stream.Part):
            impose_numbering_standard(part, "Full Measure")
        for part in self.other.getElementsByClass(stream.Part):
            impose_numbering_standard(part, "Full Measure")  # TODO: Have at start?

        # MM
        self.preferred_measure_map = stream_to_measure_map(self.preferred, check_parts_match)
        self.other_measure_map = stream_to_measure_map(self.other, check_parts_match)

        if write:
            if outpath is None:
                outpath1 = path_to_preferred.parent
                outpath2 = path_to_other.parent
            preferred_outpath = outpath1 / 'preferred_measure_map.json'
            other_outpath = outpath2 / 'other_measure_map.json'
            write_measure_map(self.preferred_measure_map, path=preferred_outpath)
            write_measure_map(self.other_measure_map, path=other_outpath)

        this_compare_object = Code.measuring_bars.Compare(self.preferred_measure_map, self.other_measure_map, attempt_fix=attempt_fix, write_modifications=write_modifications)
        Error = [item for item in this_compare_object.diagnosis if item[0] == "Needleman-Wunsch"]
        # print(this_compare_object.diagnosis)  # TODO: remove
        """if 'test' in this_compare_object.diagnosis:
            this_compare_object.diagnosis.remove('test')
            Error = Code.measuring_bars.needleman_wunsch(stream_to_measure_map(self.preferred, check_parts_match), stream_to_measure_map(self.other, check_parts_match))
            print(stream_to_measure_map(self.preferred, check_parts_match))
            print(stream_to_measure_map(self.other, check_parts_match))
            for x in range(len(Error[0])):
                print(f"Preferred: {Error[0][x]}")
                print(f"Other: {Error[1][x]}")
                print("")"""  # TODO: remove

        if write_modifications:
            with open(path_to_other.parent / 'other_modifications.txt', "w") as file:
                if Error:
                    for x in range(len(Error[0][1])):
                        """print(f"Preferred: {Error[0][1][x]}")
                        print(f"Other: {Error[0][2][x]}")
                        print("")"""  # TODO: remove
                    file.write("Could not align the two sources. Best alignment based on Needleman-Wunsch algorithm:\n")
                    file.write(f"Preferred measure map aligned: {Error[0][1]}\n")
                    file.write(f"Other measure map aligned: {Error[0][2]}\n")
                else:
                    file.write("Changes to be made to secondary measure map:\n")
                    for change in this_compare_object.diagnosis:
                        if change[0] == "Join":
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
                            file.write(f" - Change measure {change[1]}'s actual length to {change[2]}.\n")
                        elif change[0] == "Time_Signature":
                            file.write(f" - Change measure {change[1]}'s time signature to {change[2]}.\n")

        if attempt_fix and not Error:
            for change in this_compare_object.diagnosis:  # TODO: multiple parts?
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

            self.other.write('musicxml', path_to_other.parent / "modified_other_score.mxl")
            self.preferred.write('musicxml', path_to_preferred.parent / "modified_preferred_score.mxl")  # TODO: impose numbering standard on all preferred?

            # self.other.parts[0].show('text')
            # self.preferred.parts[0].show('text')

        if not attempt_fix and not write_modifications:
            print(this_compare_object.diagnosis)

        # removeDuplicates(self.other)
        # self.other.show()


def generate_examples(path_to_examples: str = '../Examples/'):
    """
    Generates json files of the measure map for each of our example mxl file in a specified folder
    """

    for file in os.listdir(path_to_examples):
        if file.endswith(".mxl"):
            score = converter.parse(path_to_examples + file)
            measure_map = stream_to_measure_map(score)
            write_measure_map(measure_map, path_to_examples + file.removesuffix(".mxl") + "_measure_map.json")


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
        "measure_count": int,  # all represented, in natural numbers
        "offset": int | float,  # quarterLength from beginning
        "measure_number" / tag: int | str,  # constraints are conventional only
        "time_signature": str | music21.meter.TimeSignature.ratioString,
        "nominal_length": int | float  # NB can derive nominal_length from TS but not vice versa
        "actual_length": int | float,  # expressed in quarterLength. Could also be as proportion
        "has_start_repeat": bool,
        "has_end_repeat": bool
        "next_measure": lst of str
    """

    sheet_measure_map = []
    go_back_to = 1
    go_forward_from = 1
    time_sig = this_part.getElementsByClass(stream.Measure)[0].timeSignature.ratioString
    measure_count = 1

    for measure in this_part.recurse().getElementsByClass(stream.Measure):
        has_end_repeat = False
        has_start_repeat = False
        next_measure = []

        if measure.timeSignature:
            time_sig = measure.timeSignature.ratioString

        if measure.leftBarline:  # TODO: Replace with normal equality checks
            if str(measure.leftBarline) == str(bar.Repeat(direction="start")):
                has_start_repeat = True
        if measure.rightBarline:
            if str(measure.rightBarline) == str(bar.Repeat(direction="end")):
                has_end_repeat = True

        if has_start_repeat:  # Crude method to add next measure information including for multiple endings from repeats
            go_back_to = measure_count
        elif measure.leftBarline:
            if measure.leftBarline.type == "regular" and sheet_measure_map[measure_count - 2]["has_end_repeat"]:
                sheet_measure_map[go_forward_from - 1]["next_measure"].append(measure_count)
            elif measure.leftBarline.type == "regular":
                go_forward_from = measure_count - 1
        if has_end_repeat:
            next_measure.append(go_back_to)
        if measure_count + 1 <= len(this_part.recurse().getElementsByClass(stream.Measure)) and \
                not (has_end_repeat and measure_count > go_forward_from != 1):
            next_measure.append(measure_count + 1)

        measure_dict = {
            "measure_count": measure_count,
            "offset": measure.offset,
            "measure_number": measure.measureNumber,
            # "suffix": measure.suffix,
            "nominal_length": measure.barDuration.quarterLength,
            "actual_length": measure.duration.quarterLength,
            "time_signature": time_sig,
            "has_start_repeat": has_start_repeat,
            "has_end_repeat": has_end_repeat,
            "next_measure": next_measure
        }

        sheet_measure_map.append(measure_dict)
        measure_count += 1

    return sheet_measure_map


# ------------------------------------------------------------------------------


def split_measure(part_to_fix: stream.Part, diagnosis: tuple):
    """
    Split one measure on a part defined by the tuple in the form ("split", measure_count, offset)
    """

    assert diagnosis[0] == "Split"
    assert len(diagnosis) == 3
    assert isinstance(diagnosis[1], int)
    assert isinstance(diagnosis[2], float)

    measure = part_to_fix.getElementsByClass(stream.Measure)[diagnosis[1] - 1]
    offset = measure.offset
    first_part, second_part = measure.splitAtQuarterLength(diagnosis[2])
    # second_part.removeClasses()  # TODO?
    second_part.number = first_part.measureNumber
    first_part.numberSuffix = 'a'
    second_part.numberSuffix = 'b'
    part_to_fix.insert(offset + diagnosis[2], second_part)
    removeDuplicates(part_to_fix)  # stream.tools.removeDuplicates(part_to_fix)


def join_measures(part_to_fix: stream.Part, diagnosis: tuple) -> stream.Part:
    """
    Join two measures into one on a part (`part_to_fix`)
    defined by the `diagnosis` tuple in the form ("Join", measure_count)
    where the `measure_count` is the index of the first measure to be joined to the one that
    immediately follows.

    Note: it bears repeating that this is
    enforced for consecutive measures only and that
    the indexing is based on `measure_count`, i.e., not number.
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
        target_measure.insert(base_ql + x.offset, x)

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
        measures[-1].rightBarline = bar.Barline(type='final')
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
    if diagnosis[2] == 'start':
        measure.leftBarline = bar.Repeat(direction="start")
    elif diagnosis[2] == 'end':
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
                measure.numberSuffix = 'a'
            elif measure.quarterLength + measure_list[index - 1].quarterLength == measure_list[index - 1].barDuration.quarterLength and index != 0:
                measure_list[index].number = count
                measure_list[index].numberSuffix = 'b'
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

def write_measure_map(measure_map: list, path: str = None, field_names: list = None, verbose: bool = True,
                      outformat: str = "json"):
    """
    Writes a measure map to a tsv or csv file.
    """

    dictionary_keys = ["measure_count",
                       "offset",
                       "measure_number",
                       # "suffix",
                       "nominal_length",
                       "actual_length",
                       "time_signature",
                       "has_start_repeat",
                       "has_end_repeat",
                       "next_measure"]
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
        path = "./measure_map." + outformat

    if outformat == "json":
        with open(path, 'w') as file:
            json.dump(data, file, indent=4)
    elif outformat == "csv" or "tsv":
        with open(path, "w", encoding="UTF8", newline="") as file:
            if outformat == "csv":
                writer = csv.DictWriter(file, fieldnames=field_names, quoting=csv.QUOTE_NONNUMERIC)
            else:
                writer = csv.DictWriter(file, fieldnames=field_names, quoting=csv.QUOTE_NONNUMERIC, delimiter='\t',
                                        lineterminator='\n')
            writer.writeheader()
            if not verbose:
                writer.writerow(data[0])
                for i in range(1, len(data)):
                    for name in dictionary_keys:
                        if measure_map[i].get(name) != measure_map[i - 1].get(name) and \
                                name not in ["measure_count", "offset", "measure_number",
                                             "next_measure", "suffix"]:
                            writer.writerow(data[i])
                            break
            else:
                writer.writerows(data)
    else:
        raise ValueError(f"Unsupported file format '{outformat}' given")


# ------------------------------------------------------------------------------

def removeDuplicates(thisStream: stream.Stream,
                     classesToRemove: tuple = (meter.TimeSignature, key.KeySignature, clef.Clef),
                     inPlace: bool = True
                     ) -> stream.Stream:
    """
    Duplicate of music21's removeDuplicates function, included here until it is available via stable release
    TODO: remove
    """

    from music21.base import Music21Object

    supportedClasses = (meter.TimeSignature, key.KeySignature, clef.Clef)

    removalDict: dict[stream.Stream, list[Music21Object]] = {}

    if not inPlace:
        thisStream = thisStream.coreCopyAsDerivation('removeDuplicates')

    if isinstance(thisStream, stream.Score):
        if len(thisStream.parts) > 0:
            for p in thisStream.parts:
                removeDuplicates(p, classesToRemove=classesToRemove, inPlace=True)

    for thisClass in classesToRemove:

        if not any(issubclass(thisClass, supportedClass) for supportedClass in supportedClasses):
            raise ValueError(f'Invalid class. Only {supportedClasses} are supported.')

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

# ------------------------------------------------------------------------------
