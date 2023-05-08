"""
Evaluation of the modifications over an entire corpus.
"""

from Code.music21_application import *

i = 2
while i < 372:
    score = REPO_FOLDER / 'Real_Cases' / 'Corpus' / 'Scores' / f"{i:03}" / 'short_score.mxl'
    analysis = REPO_FOLDER / 'Real_Cases' / 'Corpus' / 'Analyses' / f"{i:03}" / 'analysis.txt'
    Aligner(score, analysis, attempt_fix=False, write_modifications=True, check_parts_match=False)
    i += 1

# TODO: fix issue of different parts having different numberings... workaround added!
