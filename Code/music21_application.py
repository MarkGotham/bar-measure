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
from music21 import bar, converter, stream


# ------------------------------------------------------------------------------

class Aligner:
    def __init__(self, path_to_preferred: os.PathLike, path_to_other: os.PathLike):
        # Paths
        self.path_to_preferred = path_to_preferred
        self.path_to_other = path_to_other

        # Parsed
        self.preferred = converter.parse(self.path_to_preferred)
        self.other = converter.parse(self.path_to_other)

        # MM
        self.preferred_measure_map = stream_to_measure_map(self.preferred)
        self.other_measure_map = stream_to_measure_map(self.other)


def generate_examples(path_to_examples: str = '../Examples/'):
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

        if measure.leftBarline:  # Only way for this to work seems to be to convert to strings? Object equality checks :- known issue with music21
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
            "measure_count": measure_count + 1,
            "offset": measure.offset,
            "measure_number": measure.measureNumber,
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

def fix(part_to_fix: stream.Part, diagnosis: list):
    """
    Having diagnosed the difference(s), attempt to fix.
    """
    pass
    # TODO


def impose_numbering_standard(part_to_fix: stream.Part, standard: str = "Measure Count"):
    """
    Impose a standard for numbering measure.
    TODO Initial implementation for either of the following:

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
    pass
    # TODO


# ------------------------------------------------------------------------------

def write_measure_map(measure_map: list, path: str = None, field_names: list = None, verbose: bool = True,
                      outformat: str = "json"):
    """
    Writes a measure map to a tsv or csv file.
    """
    dictionary_keys = ["measure_count",
                       "offset",
                       "measure_number",
                       "split",
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
                                             "next_measure"]:
                            writer.writerow(data[i])
                            break
            else:
                writer.writerows(data)
    else:
        raise ValueError(f"Unsupported file format '{outformat}' given")

# ------------------------------------------------------------------------------


generate_examples()
generate_examples("../Example_core/")
