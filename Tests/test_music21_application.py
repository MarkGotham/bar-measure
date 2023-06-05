"""
Test the application to music21.
"""

from unittest import TestCase
from . import EG_CORE, EG_FOLDER, REPO_FOLDER
from Code.music21_application import *


class Test(TestCase):

    def test_example_case(self):
        measure_map = stream_to_measure_map(converter.parse(EG_CORE / "core.mxl"))

        self.assertEqual(
            measure_map,
            [
                {"count": 1,
                 "qstamp": 0.0,
                 "number": 0,
                 "nominal_length": 4.0,
                 "actual_length": 1.0,
                 "time_signature": "4/4",
                 "start_repeat": False,
                 "end_repeat": False,
                 "next": [2]},
                {"count": 2,
                 "qstamp": 1.0,
                 "number": 1,
                 "nominal_length": 4.0,
                 "actual_length": 4.0,
                 "time_signature": "4/4",
                 "start_repeat": False,
                 "end_repeat": False,
                 "next": [3]},
                {"count": 3,
                 "qstamp": 5.0,
                 "number": 2,
                 "nominal_length": 4.0,
                 "actual_length": 3.0,
                 "time_signature": "4/4",
                 "start_repeat": False,
                 "end_repeat": True,
                 "next": [1, 4]},
                {"count": 4,
                 "qstamp": 8.0,
                 "number": 3,
                 "nominal_length": 4.0,
                 "actual_length": 1.0,
                 "time_signature": "4/4",
                 "start_repeat": True,
                 "end_repeat": False,
                 "next": [5]},
                {"count": 5,
                 "qstamp": 9.0,
                 "number": 4,
                 "nominal_length": 4.0,
                 "actual_length": 4.0,
                 "time_signature": "4/4",
                 "start_repeat": False,
                 "end_repeat": False,
                 "next": [6, 8]},
                {"count": 6,
                 "qstamp": 13.0,
                 "number": 5,
                 "nominal_length": 4.0,
                 "actual_length": 4.0,
                 "time_signature": "4/4",
                 "start_repeat": False,
                 "end_repeat": False,
                 "next": [7]},
                {"count": 7,
                 "qstamp": 17.0,
                 "number": 6,
                 "nominal_length": 4.0,
                 "actual_length": 3.0,
                 "time_signature": "4/4",
                 "start_repeat": False,
                 "end_repeat": True,
                 "next": [4]},
                {"count": 8,
                 "qstamp": 20.0,
                 "number": 7,
                 "nominal_length": 4.0,
                 "actual_length": 4.0,
                 "time_signature": "4/4",
                 "start_repeat": False,
                 "end_repeat": False,
                 "next": [9]},
                {"count": 9,
                 "qstamp": 24.0,
                 "number": 8,
                 "nominal_length": 4.0,
                 "actual_length": 4.0,
                 "time_signature": "4/4",
                 "start_repeat": False,
                 "end_repeat": False,
                 "next": [10]},
                {"count": 10,
                 "qstamp": 28.0,
                 "number": 9,
                 "nominal_length": 4.0,
                 "actual_length": 3.0,
                 "time_signature": "4/4",
                 "start_repeat": False,
                 "end_repeat": False,
                 "next": []}
            ]
        )

    def test_split_measure(self):
        from music21 import corpus
        s = corpus.parse("bach/bwv66.6").parts[0]
        self.assertEqual(11, len(s))
        split_measure(s, ("Split", 6, 3.0))
        self.assertEqual(12, len(s))

    def test_join_measure(self):
        s = converter.parse(EG_CORE / "core.mxl").parts[0]
        self.assertEqual(10, len(s.getElementsByClass(stream.Measure)))
        join_measures(s, ("Join", 1))
        self.assertEqual(9, len(s.getElementsByClass(stream.Measure)))

    def test_numbering_standards(self):
        s = converter.parse(EG_CORE / "core.mxl").parts[0]
        self.assertEqual(0, s.getElementsByClass(stream.Measure)[0].measureNumber)
        impose_numbering_standard(s,
                                  "Measure Count")
        self.assertEqual(1, s.getElementsByClass(stream.Measure)[0].measureNumber)

        impose_numbering_standard(s, "Full Measure")
        self.assertEqual(2, s.getElementsByClass(stream.Measure)[3].measureNumber)

    def test_copy_repeats(self):
        s = converter.parse(EG_FOLDER / "no_repeats.mxl").parts[0]
        copy_repeat_marks(s, ("Repeat_Marks", 3, "end"))
        copy_repeat_marks(s, ("Repeat_Marks", 4, "start"))
        copy_repeat_marks(s, ("Repeat_Marks", 7, "end"))

    def test_copy_length(self):
        s = converter.parse(EG_CORE / "core.mxl").parts[0]
        self.assertEqual(3.0, s.getElementsByClass("Measure")[2].duration.quarterLength)
        copy_length(s, ("Measure_Length", 3, 4.0))
        self.assertEqual(4.0, s.getElementsByClass("Measure")[2].duration.quarterLength)

    def test_copy_time_signature(self):
        s = converter.parse(EG_CORE / "core.mxl").parts[0]
        self.assertEqual("4/4", s.getElementsByClass("Measure")[0].timeSignature.ratioString)
        copy_time_signature(s, ("Time_Signature", 1, "3/4"))
        self.assertEqual("3/4", s.getElementsByClass("Measure")[0].timeSignature.ratioString)

    def test_expand_repeats(self):
        s = converter.parse(EG_CORE / "core.mxl").parts[0]
        expand_repeats(s)
        # TODO: fix
        # self.assertEqual(part_to_measure_map(converter.parse("../Examples/expanded_repeats.mxl").parts[0]), part_to_measure_map(s))

    def test_real_case(self):
        score = REPO_FOLDER / "Real_Cases" / "Marias_Kirchgang" / "score.mxl"
        analysis = REPO_FOLDER / "Real_Cases" / "Marias_Kirchgang" / "analysis.txt"

        Aligner(score, analysis, attempt_fix=True)
