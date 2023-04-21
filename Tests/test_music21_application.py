"""
Test the application to music21.
"""

from unittest import TestCase
from Code.music21_application import *


class Test(TestCase):

    def test_example_case(self):
        measure_map = stream_to_measure_map(converter.parse('../Example_core/core.mxl'))

        self.assertEqual([{'measure_count': 1, 'offset': 0.0, 'measure_number': 0, 'nominal_length': 4.0,
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
                           'has_end_repeat': False, 'next_measure': []}], measure_map)

    def test_split_measure(self):
        s = corpus.parse("bach/bwv66.6").parts[0]
        self.assertEqual(11, len(s))
        split_measure(s, ("Split", 6, 3.0))
        self.assertEqual(12, len(s))

    def test_join_measure(self):
        s = converter.parse("../Examples/expanded_repeats.mxl").parts[0]
        self.assertEqual(16, len(s))
        # join_measure(s, ("Join", 2))
        # self.assertEqual(15, len(s))
        # TODO: implement join_measure

    def test_numbering_standards(self):
        s = converter.parse("../Example_core/core.mxl").parts[0]
        self.assertEqual(0, s.getElementsByClass(stream.Measure)[0].measureNumber)
        impose_numbering_standard(s, "Measure Count")
        self.assertEqual(1, s.getElementsByClass(stream.Measure)[0].measureNumber)

        impose_numbering_standard(s, "Full Measure")
        self.assertEqual(2, s.getElementsByClass(stream.Measure)[3].measureNumber)

    def test_copy_repeats(self):
        s = converter.parse("../Examples/no_repeats.mxl").parts[0]
        copy_repeat_marks(s, ("Repeat_Marks", 3, "end"))
        copy_repeat_marks(s, ("Repeat_Marks", 4, "start"))
        copy_repeat_marks(s, ("Repeat_Marks", 7, "end"))

    def test_copy_length(self):
        s = converter.parse("../Example_core/core.mxl").parts[0]
        self.assertEqual(3.0, s.getElementsByClass("Measure")[2].duration.quarterLength)
        copy_length(s, ("Measure_Length", 3, 4.0))
        self.assertEqual(4.0, s.getElementsByClass("Measure")[2].duration.quarterLength)

    def test_expand_repeats(self):
        s = converter.parse("../Example_core/core.mxl")
        expand_repeats(s)
        # TODO: fix
        # self.assertEqual(part_to_measure_map(converter.parse("../Examples/expanded_repeats.mxl").parts[0]), part_to_measure_map(s))

    def test_real_case(self):
        score = REPO_FOLDER / 'Real_Cases' / 'Marias_Kirchgang' / 'score.mxl'
        analysis = REPO_FOLDER / 'Real_Cases' / 'Marias_Kirchgang' / 'analysis.txt'

        Aligner(score, analysis, attempt_fix=True)
