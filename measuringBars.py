"""
===============================
Measuring Bars (measuringBars.py)
===============================

Mark Gotham, 2022


LICENCE:
===============================

Creative Commons Attribution-ShareAlike 4.0 International License
https://creativecommons.org/licenses/by-sa/4.0/


ABOUT:
===============================

Quick and dirty initial steps to get the ball rolling.
More to follow ;)

"""


# ------------------------------------------------------------------------------

from music21 import converter, stream
import unittest


# ------------------------------------------------------------------------------

def score_to_measure_map(path_to_score: str,
                         check_parts_match: bool = False) -> list:
    """
    Maps from a music21 stream
    to a possible version of the "measure map".
    The bulk of the work is done by part_to_measure_map
    (see notes there).
    The additional check_parts_match argument defaults to False but
    if True and the score has multiple parts, it will
    check that those parts return the same measurement information.
    """
    score = converter.parse(path_to_score)
    part = score.parts[0]
    
    mm = part_to_measure_map(part)
    
    if not check_parts_match:
        return mm
    
    num_parts = len(score.parts)

    if num_parts < 2:
        return mm
    
    for p in range(1, num_parts):
        thisMM = part_to_measure_map(score.part[p])
        if thisMM != mm:
            raise ValueError(f'Parts 0 and {p} do not match.')


def part_to_measure_map(thisPart: stream.Part) -> list:
    """
    Mapping from a music21.stream.part
    to a "measure map" (currently a list of dicts).
    """
    measure_map = []
    measure_count = 1
    
    currentTS = 'Fake'
    
    for m in thisPart.recurse().getElementsByClass(stream.Measure):

        this_measure_dict = {'measure_count': measure_count,
                             'offset': m.offset,
                             'measure_number': m.measureNumber,
                             'nominal_length': m.barDuration.quarterLength,
                             'actual_length': m.duration.quarterLength}

        ts = m.timeSignature
        if ts:
            this_measure_dict['time_signature'] = ts.ratioString
            currentTS = ts.ratioString
        else:
            this_measure_dict['time_signature'] = currentTS

        # TODO: Repeats, first/second time etc
        
        measure_map.append(this_measure_dict)
        measure_count += 1
    
    return measure_map


# ------------------------------------------------------------------------------

class Test(unittest.TestCase):
    """
    First test example. More to follow.
    """

    def testExampleCase(self):
        
        testScore = converter.parse('./Example/measuringBarsExample.mxl')
        
        mm = part_to_measure_map(testScore.parts[0])
        
        self.assertEqual(mm,
            [{'measure_count': 1, 'offset': 0.0, 'measure_number': 0, 'nominal_length': 4.0, 'actual_length': 1.0, 'time_signature': '4/4'},
            {'measure_count': 2, 'offset': 1.0, 'measure_number': 1, 'nominal_length': 4.0, 'actual_length': 4.0, 'time_signature': '4/4'},
            {'measure_count': 3, 'offset': 5.0, 'measure_number': 2, 'nominal_length': 4.0, 'actual_length': 3.0, 'time_signature': '4/4'},
            {'measure_count': 4, 'offset': 8.0, 'measure_number': 3, 'nominal_length': 4.0, 'actual_length': 1.0, 'time_signature': '4/4'},
            {'measure_count': 5, 'offset': 9.0, 'measure_number': 4, 'nominal_length': 4.0, 'actual_length': 4.0, 'time_signature': '4/4'},
            {'measure_count': 6, 'offset': 13.0, 'measure_number': 5, 'nominal_length': 4.0, 'actual_length': 4.0, 'time_signature': '4/4'},
            {'measure_count': 7, 'offset': 17.0, 'measure_number': 6, 'nominal_length': 4.0, 'actual_length': 3.0, 'time_signature': '4/4'},
            {'measure_count': 8, 'offset': 20.0, 'measure_number': 7, 'nominal_length': 4.0, 'actual_length': 4.0, 'time_signature': '4/4'},
            {'measure_count': 9, 'offset': 24.0, 'measure_number': 8, 'nominal_length': 4.0, 'actual_length': 4.0, 'time_signature': '4/4'},
            {'measure_count': 10, 'offset': 28.0, 'measure_number': 9, 'nominal_length': 4.0, 'actual_length': 3.0, 'time_signature': '4/4'}
            ]
        )


# ------------------------------------------------------------------------------

if __name__ == '__main__':
    unittest.main()
