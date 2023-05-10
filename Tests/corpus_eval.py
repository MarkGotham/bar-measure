"""
Evaluation of the modifications over an entire corpus.
"""

from Code.music21_application import *


def corpus():
    i = 1
    while i < 372:
        # print(i)
        score = REPO_FOLDER / 'Real_Cases' / 'Corpus' / 'Scores' / f"{i:03}" / 'short_score.mxl'
        analysis = REPO_FOLDER / 'Real_Cases' / 'Corpus' / 'Analyses' / f"{i:03}" / 'analysis.txt'
        Aligner(score, analysis, attempt_fix=True, write_modifications=True, check_parts_match=False, write=True)
        i += 1


def individual(i):
    score = REPO_FOLDER / 'Real_Cases' / 'Corpus' / 'Scores' / f"{i:03}" / 'short_score.mxl'
    analysis = REPO_FOLDER / 'Real_Cases' / 'Corpus' / 'Analyses' / f"{i:03}" / 'analysis.txt'
    # converter.parse(analysis).show()
    Aligner(score, analysis, attempt_fix=True, write_modifications=True, check_parts_match=False, write=True)


# corpus()
# individual(52)

# TODO: fix issue of different parts having different numberings... workaround added!
