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
                "measure_number": 8,
                "nominal_length": 4.0,
                "actual_length": 2.0,
                "time_signature": "4/4",
                "has_start_repeat": False,
                "has_end_repeat": False,
                "next_measure": [11]}
            ]

        output = perform_split(fake_measure_map, ("Split", 1, 2))
        self.assertEqual(resulting_measure_map, output)

    def test_join(self):
        fake_measure_map = [{
                "measure_count": 9,
                "offset": 24.0,
                "measure_number": 8,
                "nominal_length": 4.0,
                "actual_length": 3.0,
                "time_signature": "4/4",
                "has_start_repeat": False,
                "has_end_repeat": False,
                "next_measure": [10]},
            {
                "measure_count": 10,
                "offset": 26.0,
                "measure_number": 9,
                "nominal_length": 4.0,
                "actual_length": 1.0,
                "time_signature": "4/4",
                "has_start_repeat": False,
                "has_end_repeat": True,
                "next_measure": [11]},
            {
                "measure_count": 11,
                "offset": 28.0,
                "measure_number": 10,
                "nominal_length": 4.0,
                "actual_length": 4.0,
                "time_signature": "4/4",
                "has_start_repeat": False,
                "has_end_repeat": False,
                "next_measure": [12]}
        ]
        resulting_measure_map = [{
                "measure_count": 9,
                "offset": 24.0,
                "measure_number": 8,
                "nominal_length": 4.0,
                "actual_length": 4.0,
                "time_signature": "4/4",
                "has_start_repeat": False,
                "has_end_repeat": True,
                "next_measure": [10]},
            {
                "measure_count": 10,
                "offset": 28.0,
                "measure_number": 9,
                "nominal_length": 4.0,
                "actual_length": 4.0,
                "time_signature": "4/4",
                "has_start_repeat": False,
                "has_end_repeat": False,
                "next_measure": [11]}
        ]

        output = perform_join(fake_measure_map, ("Join", 1))
        self.assertEqual(resulting_measure_map, output)

    def test_renumbering(self):
        preferred_measure_map = [{
                "measure_count": 1,
                "offset": 0.0,
                "measure_number": 0,
                "nominal_length": 4.0,
                "actual_length": 1.0,
                "time_signature": "4/4",
                "has_start_repeat": False,
                "has_end_repeat": False,
                "next_measure": [2]},
            {
                "measure_count": 2,
                "offset": 1.0,
                "measure_number": 1,
                "nominal_length": 4.0,
                "actual_length": 4.0,
                "time_signature": "4/4",
                "has_start_repeat": False,
                "has_end_repeat": False,
                "next_measure": [3]},
            {
                "measure_count": 3,
                "offset": 5.0,
                "measure_number": 2,
                "nominal_length": 4.0,
                "actual_length": 4.0,
                "time_signature": "4/4",
                "has_start_repeat": False,
                "has_end_repeat": False,
                "next_measure": [4]}
        ]
        other_measure_map = [{
                "measure_count": 1,
                "offset": 0.0,
                "measure_number": 1,
                "nominal_length": 4.0,
                "actual_length": 1.0,
                "time_signature": "4/4",
                "has_start_repeat": False,
                "has_end_repeat": False,
                "next_measure": [2]},
            {
                "measure_count": 2,
                "offset": 1.0,
                "measure_number": 2,
                "nominal_length": 4.0,
                "actual_length": 4.0,
                "time_signature": "4/4",
                "has_start_repeat": False,
                "has_end_repeat": False,
                "next_measure": [3]},
            {
                "measure_count": 3,
                "offset": 5.0,
                "measure_number": 3,
                "nominal_length": 4.0,
                "actual_length": 4.0,
                "time_signature": "4/4",
                "has_start_repeat": False,
                "has_end_repeat": False,
                "next_measure": [4]}
        ]

        self.assertNotEqual(preferred_measure_map, other_measure_map)
        output = try_renumber(preferred_measure_map, other_measure_map)
        self.assertEqual(preferred_measure_map, output)

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
        self.assertEqual(preferred_measure_map, other_measure_map)

    def test_expand(self):
        measure_map = [{
                "measure_count": 1,
                "offset": 0.0,
                "measure_number": 1,
                "nominal_length": 4.0,
                "actual_length": 4.0,
                "time_signature": "4/4",
                "has_start_repeat": True,
                "has_end_repeat": False,
                "next_measure": [2, 4]},
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
                "next_measure": [1]},
            {
                "measure_count": 4,
                "offset": 4.0,
                "measure_number": 4,
                "nominal_length": 4.0,
                "actual_length": 4.0,
                "time_signature": "4/4",
                "has_start_repeat": False,
                "has_end_repeat": False,
                "next_measure": [5]}
        ]
        expanded_measure_map = [{
                "measure_count": 1,
                "offset": 0.0,
                "measure_number": 1,
                "nominal_length": 4.0,
                "actual_length": 4.0,
                "time_signature": "4/4",
                "has_start_repeat": False,
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
                "has_end_repeat": False,
                "next_measure": [4]},
            {
                "measure_count": 4,
                "offset": 0.0,
                "measure_number": 1,
                "nominal_length": 4.0,
                "actual_length": 4.0,
                "time_signature": "4/4",
                "has_start_repeat": False,
                "has_end_repeat": False,
                "next_measure": [5]},
            {
                "measure_count": 5,
                "offset": 4.0,
                "measure_number": 4,
                "nominal_length": 4.0,
                "actual_length": 4.0,
                "time_signature": "4/4",
                "has_start_repeat": False,
                "has_end_repeat": False,
                "next_measure": [6]}
        ]

        output = perform_expand_repeats(measure_map)
        self.assertEqual(expanded_measure_map, output)

    def test_lengths(self):
        preferred_measure_map = [{
                "measure_count": 1,
                "offset": 0.0,
                "measure_number": 0,
                "nominal_length": 4.0,
                "actual_length": 1.0,
                "time_signature": "4/4",
                "has_start_repeat": False,
                "has_end_repeat": False,
                "next_measure": [2]},
            {
                "measure_count": 2,
                "offset": 1.0,
                "measure_number": 1,
                "nominal_length": 4.0,
                "actual_length": 3.0,
                "time_signature": "4/4",
                "has_start_repeat": False,
                "has_end_repeat": False,
                "next_measure": [3]},
            {
                "measure_count": 3,
                "offset": 4.0,
                "measure_number": 2,
                "nominal_length": 4.0,
                "actual_length": 4.0,
                "time_signature": "4/4",
                "has_start_repeat": False,
                "has_end_repeat": False,
                "next_measure": [4]}
        ]
        other_measure_map = [{
                "measure_count": 1,
                "offset": 0.0,
                "measure_number": 0,
                "nominal_length": 4.0,
                "actual_length": 4.0,
                "time_signature": "4/4",
                "has_start_repeat": False,
                "has_end_repeat": False,
                "next_measure": [2]},
            {
                "measure_count": 2,
                "offset": 1.0,
                "measure_number": 1,
                "nominal_length": 4.0,
                "actual_length": 4.0,
                "time_signature": "4/4",
                "has_start_repeat": False,
                "has_end_repeat": False,
                "next_measure": [3]},
            {
                "measure_count": 3,
                "offset": 4.0,
                "measure_number": 2,
                "nominal_length": 4.0,
                "actual_length": 3.0,
                "time_signature": "4/4",
                "has_start_repeat": False,
                "has_end_repeat": False,
                "next_measure": [4]}
        ]

        self.assertNotEqual(preferred_measure_map, other_measure_map)
        output = perform_actual_length_copy(preferred_measure_map, other_measure_map)
        self.assertEqual(preferred_measure_map, output)

    def test_time_signature(self):
        preferred_measure_map = [{
            "measure_count": 1,
            "offset": 0.0,
            "measure_number": 1,
            "nominal_length": 4.0,
            "actual_length": 3.0,
            "time_signature": "3/4",
            "has_start_repeat": False,
            "has_end_repeat": False,
            "next_measure": [2]}]
        other_measure_map = [{
            "measure_count": 1,
            "offset": 0.0,
            "measure_number": 1,
            "nominal_length": 4.0,
            "actual_length": 3.0,
            "time_signature": "4/4",
            "has_start_repeat": False,
            "has_end_repeat": False,
            "next_measure": [2]}]
        self.assertNotEqual(preferred_measure_map, other_measure_map)
        output = perform_time_signature_copy(preferred_measure_map, other_measure_map)
        self.assertEqual(preferred_measure_map, output)

    def test_nominal_lengths(self):
        measure_map = [{
            "measure_count": 1,
            "offset": 0.0,
            "measure_number": 1,
            "nominal_length": 4.0,
            "actual_length": 3.0,
            "time_signature": "3/4",
            "has_start_repeat": False,
            "has_end_repeat": False,
            "next_measure": [2]}]
        resulting_measure_map = [{
            "measure_count": 1,
            "offset": 0.0,
            "measure_number": 1,
            "nominal_length": 3.0,
            "actual_length": 3.0,
            "time_signature": "3/4",
            "has_start_repeat": False,
            "has_end_repeat": False,
            "next_measure": [2]}]
        self.assertNotEqual(measure_map, resulting_measure_map)
        output = perform_nominal_length_recalculation(measure_map)
        self.assertEqual(resulting_measure_map, output)

    def test_offset(self):
        measure_map = [{
                "measure_count": 1,
                "offset": 3.0,
                "measure_number": 0,
                "nominal_length": 4.0,
                "actual_length": 1.0,
                "time_signature": "4/4",
                "has_start_repeat": False,
                "has_end_repeat": False,
                "next_measure": [2]},
            {
                "measure_count": 2,
                "offset": 34.0,
                "measure_number": 1,
                "nominal_length": 4.0,
                "actual_length": 3.0,
                "time_signature": "4/4",
                "has_start_repeat": False,
                "has_end_repeat": False,
                "next_measure": [3]},
            {
                "measure_count": 3,
                "offset": 54.0,
                "measure_number": 2,
                "nominal_length": 4.0,
                "actual_length": 4.0,
                "time_signature": "4/4",
                "has_start_repeat": False,
                "has_end_repeat": False,
                "next_measure": [4]}
        ]
        resulting_measure_map = [{
                "measure_count": 1,
                "offset": 0.0,
                "measure_number": 0,
                "nominal_length": 4.0,
                "actual_length": 1.0,
                "time_signature": "4/4",
                "has_start_repeat": False,
                "has_end_repeat": False,
                "next_measure": [2]},
            {
                "measure_count": 2,
                "offset": 1.0,
                "measure_number": 1,
                "nominal_length": 4.0,
                "actual_length": 3.0,
                "time_signature": "4/4",
                "has_start_repeat": False,
                "has_end_repeat": False,
                "next_measure": [3]},
            {
                "measure_count": 3,
                "offset": 4.0,
                "measure_number": 2,
                "nominal_length": 4.0,
                "actual_length": 4.0,
                "time_signature": "4/4",
                "has_start_repeat": False,
                "has_end_repeat": False,
                "next_measure": [4]}
        ]
        self.assertNotEqual(measure_map, resulting_measure_map)
        output = perform_offset_recalculation(measure_map)
        self.assertEqual(resulting_measure_map, output)

    def test_real_cases(self):
        """score = REPO_FOLDER / 'Real_Cases' / 'Marias_Kirchgang' / 'score.mxl'
        analysis = REPO_FOLDER / 'Real_Cases' / 'Marias_Kirchgang' / 'analysis.txt'  # 3x splits required

        Aligner(score, analysis)"""

        with open(REPO_FOLDER / 'Real_Cases' / 'Marias_Kirchgang' / 'preferred_measure_map.json', 'r') as file:
            preferred = json.load(file)
        with open(REPO_FOLDER / 'Real_Cases' / 'Marias_Kirchgang' / 'other_measure_map.json', 'r') as file:
            other = json.load(file)
        self.assertNotEqual(preferred, other)
        output = Compare(preferred, other).diagnose()
        self.assertEqual(preferred, output)
