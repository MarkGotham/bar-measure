# MOVE ALONG PLEASE [The `bar-measure` repo]

Move along please!
This repo is now only for archive an re-direct.
It was the catalyst for, and has been superseded by,
[this org](https://github.com/measure-map)
and especially [this repo](https://github.com/measure-map/pyMeasureMap).
Move along now, nothing to see here. 

## Motivation

The measurement of musical time in bars (US: measures)
seems as though it should be straight forward and yet a few common variants 
constitute a major stumbling block for reliable alignment between sources
and a significant detraction from the comparison and/or integration of datasets.

## "Measure Map"

This repo seeks to provide an interoperable solution that is effective for the majority of issues 
encountered in existing datasets of symbolic music.

This solution centres on the "Measure Map": 
a syntax for encoding in a stand-alone document how time is measured in an external source (symbolic, audio, analysis, etc.).

## Goals

1. Identify how two sources are set out,
1. Diagnose differences,
1. Optionally (if user requests), change one source to fit together with the other. This is potentially destructive, so default = False.

All of the data for this comes from attributes of the bars themselves, not their content.

Evaluation is planned to include comparison between the actual content of the sources (e.g., with pitch class profile matching on each bar).
- For an effectively aligned pair the match metrics will be high.
- Without the ‘fix’
  - some simple files will happen to match well anyway
  - more complex ones will likely slip off in terms of alignment.

It should be both easy and meaningful to demonstrate the benefit of the system in this way.

## Philosophy

The best possible solution will (as far as possible) be:
- As simple as possible
  - but not simpler ;)
- Platform/library independent (interoperable) …
  - but also implemented/demonstrated in places like music21
- Able to handle most credible variants / use cases
  - but probably not even aiming for absolutely all.
- Able to implement musical conventions clearly (e.g., m5, m6, m7a, m7b)
  - without taking a stand for or against particular editorial styles.

## Scope and Limits

We limit ourselves to sources that a user defines to be equivalent (i.e., variants of the 
"same" source).

### Main topics within scope:

- Anacrusis:
  - by convention, when the first bar is "anacrustic" (incomplete) is should be numbered labelled 0.
  - This is not to be relied upon in practice.
- Repeats:
  - typically at the end of a bar, 
  - nominally sometimes ‘within’ but
   - even then usually encoded with a 'split' bar (two, shorter ones that add up to a whole).
- First/second time bars:
  - Typically labelled '15a', '15b'
- Re-starts:
  - E.g., theme and variations movements
  - some editions number continuously while others re-start numbering from 1 (or 0) each time.
- Special cases such as cadenzas notated variably in:
  - One very long measure
  - Many (often irregular) shorter ones
- Complex repeat structures
  - E.g., da capo movements: "Menuetto Da capo" or "Da capo arias".

### Out of scope (for now):
- material clearly present in one source and absent from another, e.g., Vivaldi _Gloria_ variants
- material/bars/rhythms/notation so altered as to be inappropriate for comparing in this bar-only way e.g., Stravinsky’s initial vs 1940s revisions of works like _Petrushka_.
- visual/display issues such as show/hide options on barlines. We are interested in the underlying representation of the data.

## FAQ

Language, dependency, formats
- Python, building on top of the [music21 library](https://github.com/cuthbertLab/music21/)
- The focus is on compatibility with the interoperable musicXML standard,
- It also admits the (many) other formats that music21 can parse.
- Alignment with audio is one stated goal, but via the measure map: audio formats themselves are not explicitly addressed here.

Are all these the puns intended? Yes ;)
- Pairing "measure" and "bars" (`measuringBars` / `bar-measure`) captures something of the terminological ambiguity in even taking about this, and that's a pretty decent analogy for the musical-computational problems at stake.
- a working "Measure Map" is every bit as valuable as a "Treasure Map" ;)

## External links

- [discussions](https://gitlab.com/algomus.fr/dezrann/dezrann/-/issues/1030#note_1122509147) with @magiraud
- [music21 issue](https://github.com/cuthbertLab/music21/issues/1406)
