"""
Test the measure map processing.
"""

from unittest import TestCase
from Code.measuring_bars import *
from Code.music21_application import *
from pathlib import Path
import json

REPO_FOLDER = Path(__file__).parent.parent


class Test(TestCase):

    """def test_measure_map(self):
        with open(REPO_FOLDER / 'Example_core' / 'core_measure_map.json', 'r') as file:
            preferred = json.load(file)
        with open(REPO_FOLDER / 'Examples' / 'split_join_and_repeat_measure_map.json', 'r') as file:
            other = json.load(file)
        output = Compare(preferred, other).diagnose()
        self.assertEqual(output, preferred)

    def test_split(self):
        fake_measure_map = [{
                "measure_count": 9,
                "offset": 24.0,
                "measure_number": 8,
                "nominal_length": 4.0,
                "actual_length": 4.0,
                "time_signature": "4/4",
                "has_start_repeat": False,
                "has_end_repeat": False,
                "next_measure": [10]}
            ]

        resulting_measure_map = [{
                "measure_count": 9,
                "offset": 24.0,
                "measure_number": 8,
                "nominal_length": 4.0,
                "actual_length": 2.0,
                "time_signature": "4/4",
                "has_start_repeat": False,
                "has_end_repeat": False,
                "next_measure": [10]},
            {
                "measure_count": 10,
                "offset": 26.0,
                "measure_number": 9,
                "nominal_length": 4.0,
                "actual_length": 2.0,
                "time_signature": "4/4",
                "has_start_repeat": False,
                "has_end_repeat": False,
                "next_measure": [11]}
            ]

        output = perform_split(fake_measure_map, ("Split", 1, 2))
        self.assertEqual(output, resulting_measure_map)

    def test_repeats(self):
        preferred_measure_map = [{
            "measure_count": 9,
            "offset": 24.0,
            "measure_number": 8,
            "nominal_length": 4.0,
            "actual_length": 4.0,
            "time_signature": "4/4",
            "has_start_repeat": True,
            "has_end_repeat": False,
            "next_measure": [10]}
        ]

        other_measure_map = [{
            "measure_count": 9,
            "offset": 24.0,
            "measure_number": 8,
            "nominal_length": 4.0,
            "actual_length": 4.0,
            "time_signature": "4/4",
            "has_start_repeat": False,
            "has_end_repeat": False,
            "next_measure": [10]}
        ]

        perform_repeat_copy(preferred_measure_map, other_measure_map)

    def test_expand(self):
        fake_measure_map = [{
                "measure_count": 1,
                "offset": 0.0,
                "measure_number": 1,
                "nominal_length": 4.0,
                "actual_length": 4.0,
                "time_signature": "4/4",
                "has_start_repeat": True,
                "has_end_repeat": False,
                "next_measure": [2]},
            {
                "measure_count": 2,
                "offset": 0.0,
                "measure_number": 2,
                "nominal_length": 4.0,
                "actual_length": 4.0,
                "time_signature": "4/4",
                "has_start_repeat": False,
                "has_end_repeat": False,
                "next_measure": [3]},
            {
                "measure_count": 3,
                "offset": 4.0,
                "measure_number": 3,
                "nominal_length": 4.0,
                "actual_length": 4.0,
                "time_signature": "4/4",
                "has_start_repeat": False,
                "has_end_repeat": True,
                "next_measure": [1, 4]}
        ]
        # print(perform_expand_repeats(fake_measure_map))"""

    def test_lengths(self):
        print()

    def test_real_cases(self):
        score = REPO_FOLDER / 'Real_Cases' / 'Marias_Kirchgang' / 'score.mxl'
        analysis = REPO_FOLDER / 'Real_Cases' / 'Marias_Kirchgang' / 'analysis.txt'  # 3x splits required

        Aligner(score, analysis)

        with open(REPO_FOLDER / 'Real_Cases' / 'Marias_Kirchgang' / 'preferred_measure_map.json', 'r') as file:
            preferred = json.load(file)
        with open(REPO_FOLDER / 'Real_Cases' / 'Marias_Kirchgang' / 'other_measure_map.json', 'r') as file:
            other = json.load(file)
        self.assertNotEqual(preferred, other)
        output = Compare(preferred, other).diagnose()
        self.assertEqual(output, preferred)
