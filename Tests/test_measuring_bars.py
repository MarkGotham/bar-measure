"""
Test the measure map processing.
"""

from unittest import TestCase
from Code.measuring_bars import *
from Code.music21_application import *
from pathlib import Path
import json

from . import REPO_FOLDER


class Test(TestCase):
    def test_split(self):
        before = [
            {
                "count": 9,
                "qstamp": 24.0,
                "number": 8,
                "nominal_length": 4.0,
                "actual_length": 4.0,
                "time_signature": "4/4",
                "start_repeat": False,
                "end_repeat": False,
                "next": [10]}
        ]
        after = [
            {
                "count": 9,
                "qstamp": 24.0,
                "number": 8,
                "nominal_length": 4.0,
                "actual_length": 2.0,
                "time_signature": "4/4",
                "start_repeat": False,
                "end_repeat": False,
                "next": [10]},
            {
                "count": 10,
                "qstamp": 26.0,
                "number": 8,
                "nominal_length": 4.0,
                "actual_length": 2.0,
                "time_signature": "4/4",
                "start_repeat": False,
                "end_repeat": False,
                "next": [11]}
        ]

        output = perform_split(before, ("Split", 1, 2))
        self.assertEqual(after, output)

    def test_join(self):
        before = [
            {
                "count": 9,
                "qstamp": 24.0,
                "number": 8,
                "nominal_length": 4.0,
                "actual_length": 3.0,
                "time_signature": "4/4",
                "start_repeat": False,
                "end_repeat": False,
                "next": [10]},
            {
                "count": 10,
                "qstamp": 26.0,
                "number": 9,
                "nominal_length": 4.0,
                "actual_length": 1.0,
                "time_signature": "4/4",
                "start_repeat": False,
                "end_repeat": True,
                "next": [11]},
            {
                "count": 11,
                "qstamp": 28.0,
                "number": 10,
                "nominal_length": 4.0,
                "actual_length": 4.0,
                "time_signature": "4/4",
                "start_repeat": False,
                "end_repeat": False,
                "next": [12]}
        ]
        after = [
            {
                "count": 9,
                "qstamp": 24.0,
                "number": 8,
                "nominal_length": 4.0,
                "actual_length": 4.0,
                "time_signature": "4/4",
                "start_repeat": False,
                "end_repeat": True,
                "next": [10]},
            {
                "count": 10,
                "qstamp": 28.0,
                "number": 9,
                "nominal_length": 4.0,
                "actual_length": 4.0,
                "time_signature": "4/4",
                "start_repeat": False,
                "end_repeat": False,
                "next": [11]}
        ]

        output = perform_join(before, ("Join", 1))
        self.assertEqual(after, output)

    def test_renumbering(self):
        preferred_map = [
            {
                "count": 1,
                "qstamp": 0.0,
                "number": 0,
                "nominal_length": 4.0,
                "actual_length": 1.0,
                "time_signature": "4/4",
                "start_repeat": False,
                "end_repeat": False,
                "next": [2]},
            {
                "count": 2,
                "qstamp": 1.0,
                "number": 1,
                "nominal_length": 4.0,
                "actual_length": 4.0,
                "time_signature": "4/4",
                "start_repeat": False,
                "end_repeat": False,
                "next": [3]},
            {
                "count": 3,
                "qstamp": 5.0,
                "number": 2,
                "nominal_length": 4.0,
                "actual_length": 4.0,
                "time_signature": "4/4",
                "start_repeat": False,
                "end_repeat": False,
                "next": [4]}
        ]
        other_map = [{
            "count": 1,
            "qstamp": 0.0,
            "number": 1,
            "nominal_length": 4.0,
            "actual_length": 1.0,
            "time_signature": "4/4",
            "start_repeat": False,
            "end_repeat": False,
            "next": [2]},
            {
                "count": 2,
                "qstamp": 1.0,
                "number": 2,
                "nominal_length": 4.0,
                "actual_length": 4.0,
                "time_signature": "4/4",
                "start_repeat": False,
                "end_repeat": False,
                "next": [3]},
            {
                "count": 3,
                "qstamp": 5.0,
                "number": 3,
                "nominal_length": 4.0,
                "actual_length": 4.0,
                "time_signature": "4/4",
                "start_repeat": False,
                "end_repeat": False,
                "next": [4]}
        ]

        self.assertNotEqual(preferred_map, other_map)
        output = try_renumber(preferred_map, other_map)
        self.assertEqual(preferred_map, output)

    def test_repeats(self):
        preferred_map = [
            {
                "count": 9,
                "qstamp": 24.0,
                "number": 8,
                "nominal_length": 4.0,
                "actual_length": 4.0,
                "time_signature": "4/4",
                "start_repeat": True,
                "end_repeat": False,
                "next": [10]}
        ]
        other_map = [
            {
                "count": 9,
                "qstamp": 24.0,
                "number": 8,
                "nominal_length": 4.0,
                "actual_length": 4.0,
                "time_signature": "4/4",
                "start_repeat": False,
                "end_repeat": False,
                "next": [10]}
        ]

        perform_repeat_copy(preferred_map, other_map)
        self.assertEqual(preferred_map, other_map)

    def test_expand(self):
        before = [
            {
                "count": 1,
                "qstamp": 0.0,
                "number": 1,
                "nominal_length": 4.0,
                "actual_length": 4.0,
                "time_signature": "4/4",
                "start_repeat": True,
                "end_repeat": False,
                "next": [2, 4]},
            {
                "count": 2,
                "qstamp": 0.0,
                "number": 2,
                "nominal_length": 4.0,
                "actual_length": 4.0,
                "time_signature": "4/4",
                "start_repeat": False,
                "end_repeat": False,
                "next": [3]},
            {
                "count": 3,
                "qstamp": 4.0,
                "number": 3,
                "nominal_length": 4.0,
                "actual_length": 4.0,
                "time_signature": "4/4",
                "start_repeat": False,
                "end_repeat": True,
                "next": [1]},
            {
                "count": 4,
                "qstamp": 4.0,
                "number": 4,
                "nominal_length": 4.0,
                "actual_length": 4.0,
                "time_signature": "4/4",
                "start_repeat": False,
                "end_repeat": False,
                "next": [5]}
        ]
        after = [
            {
                "count": 1,
                "qstamp": 0.0,
                "number": 1,
                "nominal_length": 4.0,
                "actual_length": 4.0,
                "time_signature": "4/4",
                "start_repeat": False,
                "end_repeat": False,
                "next": [2]},
            {
                "count": 2,
                "qstamp": 0.0,
                "number": 2,
                "nominal_length": 4.0,
                "actual_length": 4.0,
                "time_signature": "4/4",
                "start_repeat": False,
                "end_repeat": False,
                "next": [3]},
            {
                "count": 3,
                "qstamp": 4.0,
                "number": 3,
                "nominal_length": 4.0,
                "actual_length": 4.0,
                "time_signature": "4/4",
                "start_repeat": False,
                "end_repeat": False,
                "next": [4]},
            {
                "count": 4,
                "qstamp": 0.0,
                "number": 1,
                "nominal_length": 4.0,
                "actual_length": 4.0,
                "time_signature": "4/4",
                "start_repeat": False,
                "end_repeat": False,
                "next": [5]},
            {
                "count": 5,
                "qstamp": 4.0,
                "number": 4,
                "nominal_length": 4.0,
                "actual_length": 4.0,
                "time_signature": "4/4",
                "start_repeat": False,
                "end_repeat": False,
                "next": [6]}
        ]

        output = perform_expand_repeats(before)
        self.assertEqual(after, output)

    def test_lengths(self):
        preferred_map = [
            {
                "count": 1,
                "qstamp": 0.0,
                "number": 0,
                "nominal_length": 4.0,
                "actual_length": 1.0,
                "time_signature": "4/4",
                "start_repeat": False,
                "end_repeat": False,
                "next": [2]},
            {
                "count": 2,
                "qstamp": 1.0,
                "number": 1,
                "nominal_length": 4.0,
                "actual_length": 3.0,
                "time_signature": "4/4",
                "start_repeat": False,
                "end_repeat": False,
                "next": [3]},
            {
                "count": 3,
                "qstamp": 4.0,
                "number": 2,
                "nominal_length": 4.0,
                "actual_length": 4.0,
                "time_signature": "4/4",
                "start_repeat": False,
                "end_repeat": False,
                "next": [4]}
        ]
        other_map = [
            {
                "count": 1,
                "qstamp": 0.0,
                "number": 0,
                "nominal_length": 4.0,
                "actual_length": 4.0,
                "time_signature": "4/4",
                "start_repeat": False,
                "end_repeat": False,
                "next": [2]},
            {
                "count": 2,
                "qstamp": 1.0,
                "number": 1,
                "nominal_length": 4.0,
                "actual_length": 4.0,
                "time_signature": "4/4",
                "start_repeat": False,
                "end_repeat": False,
                "next": [3]},
            {
                "count": 3,
                "qstamp": 4.0,
                "number": 2,
                "nominal_length": 4.0,
                "actual_length": 3.0,
                "time_signature": "4/4",
                "start_repeat": False,
                "end_repeat": False,
                "next": [4]}
        ]

        self.assertNotEqual(preferred_map, other_map)
        output = perform_actual_length_copy(preferred_map, other_map)
        self.assertEqual(preferred_map, output)

    def test_time_signature(self):
        preferred_map = [
            {
                "count": 1,
                "qstamp": 0.0,
                "number": 1,
                "nominal_length": 4.0,
                "actual_length": 3.0,
                "time_signature": "3/4",
                "start_repeat": False,
                "end_repeat": False,
                "next": [2]}]
        other_map = [
            {
                "count": 1,
                "qstamp": 0.0,
                "number": 1,
                "nominal_length": 4.0,
                "actual_length": 3.0,
                "time_signature": "4/4",
                "start_repeat": False,
                "end_repeat": False,
                "next": [2]}]

        self.assertNotEqual(preferred_map, other_map)
        output = perform_time_signature_copy(preferred_map, other_map)
        self.assertEqual(preferred_map, output)

    def test_nominal_lengths(self):
        before = [
            {
                "count": 1,
                "qstamp": 0.0,
                "number": 1,
                "nominal_length": 4.0,
                "actual_length": 3.0,
                "time_signature": "3/4",
                "start_repeat": False,
                "end_repeat": False,
                "next": [2]}]
        after = [{
            "count": 1,
            "qstamp": 0.0,
            "number": 1,
            "nominal_length": 3.0,
            "actual_length": 3.0,
            "time_signature": "3/4",
            "start_repeat": False,
            "end_repeat": False,
            "next": [2]}]
        self.assertNotEqual(before, after)
        output = perform_nominal_length_recalculation(before)
        self.assertEqual(after, output)

    def test_qstamp(self):
        before = [
            {
                "count": 1,
                "qstamp": 3.0,
                "number": 0,
                "nominal_length": 4.0,
                "actual_length": 1.0,
                "time_signature": "4/4",
                "start_repeat": False,
                "end_repeat": False,
                "next": [2]},
            {
                "count": 2,
                "qstamp": 34.0,
                "number": 1,
                "nominal_length": 4.0,
                "actual_length": 3.0,
                "time_signature": "4/4",
                "start_repeat": False,
                "end_repeat": False,
                "next": [3]},
            {
                "count": 3,
                "qstamp": 54.0,
                "number": 2,
                "nominal_length": 4.0,
                "actual_length": 4.0,
                "time_signature": "4/4",
                "start_repeat": False,
                "end_repeat": False,
                "next": [4]}
        ]
        after = [
            {
                "count": 1,
                "qstamp": 0.0,
                "number": 0,
                "nominal_length": 4.0,
                "actual_length": 1.0,
                "time_signature": "4/4",
                "start_repeat": False,
                "end_repeat": False,
                "next": [2]},
            {
                "count": 2,
                "qstamp": 1.0,
                "number": 1,
                "nominal_length": 4.0,
                "actual_length": 3.0,
                "time_signature": "4/4",
                "start_repeat": False,
                "end_repeat": False,
                "next": [3]},
            {
                "count": 3,
                "qstamp": 4.0,
                "number": 2,
                "nominal_length": 4.0,
                "actual_length": 4.0,
                "time_signature": "4/4",
                "start_repeat": False,
                "end_repeat": False,
                "next": [4]}
        ]
        self.assertNotEqual(before, after)
        output = perform_qstamp_recalculation(before)
        self.assertEqual(after, output)

    def test_real_cases(self):
        base_path = REPO_FOLDER / "Real_Cases" / "Marias_Kirchgang"

        with open(base_path / "preferred_measure_map.json", "r") as file:
            preferred = json.load(file)
        with open(base_path / "other_measure_map.json", "r") as file:
            other = json.load(file)
        self.assertNotEqual(preferred, other)
        output = Compare(preferred, other).diagnose()
        self.assertEqual(preferred, output)
