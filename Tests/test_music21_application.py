"""
Test the application to music21.
"""

from unittest import TestCase
from Code.music21_application import *


class Test(TestCase):

    def test_example_case(self):
        measure_map = stream_to_measure_map(converter.parse('../Example_core/core.mxl'))

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

    def test_split_measure(self):
        s = corpus.parse("bach/bwv66.6").parts[0]
        self.assertEqual(len(s), 11)
        split_measure(s, ("Split", 6, 3.0))
        self.assertEqual(len(s), 12)

    def test_numbering_standards(self):
        s = converter.parse("../Example_core/core.mxl").parts[0]
        self.assertEqual(s.getElementsByClass(stream.Measure)[0].measureNumber, 0)
        impose_numbering_standard(s, "Measure Count")
        self.assertEqual(s.getElementsByClass(stream.Measure)[0].measureNumber, 1)

        impose_numbering_standard(s, "Full Measure")
        self.assertEqual(s.getElementsByClass(stream.Measure)[3].measureNumber, 2)

        # TODO

