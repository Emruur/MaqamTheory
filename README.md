# Makam Theory — A Listener's Course

A self-contained static website for learning Turkish makam theory (Rast,
Nihavend, Uşşak, Hüseyni, Hicaz) with synthesized microtonal audio and staff
notation using authentic Arel–Ezgi–Uzdilek (AEU) accidentals.

Each makam chapter also includes a **live keyboard instrument** (home-row keys
A S D F… play the makam's perdeler via Web Audio at exact comma pitches, with
a transposable root A–G — G-tonic makams go down, A-tonic makams go up — and
12-TET "piano twin" keys on the row above each microtonal perde) and a
**notated song excerpt** with matching audio (Kâtibim, Yine Bir Gülnihal, Uzun
İnce Bir Yoldayım, Çanakkale İçinde, Ada Sahillerinde), transcribed from the
SymbTr-derived ABC corpus of the Turkish Makam Database
(ifdo.ca/~seymour/runabc/makams).

## Using the site

Open `index.html` directly in a browser, or serve it:

```sh
python3 -m http.server   # then http://localhost:8000
```

## Regenerating the assets

All audio (`audio/*.wav`) and notation (`img/*.svg`) are generated:

```sh
python3 tools/generate_audio.py --check   # verify theory data + synth pitch
python3 tools/generate_audio.py           # write all WAVs in 3 voices
python3 tools/generate_notation.py        # write ~40 SVG files
```

Audio is rendered in three timbres, switched site-wide by the ♪ picker in the
page header: warm synth (`audio/`), breathy ney (`audio/ney/`), and plucked
oud (`audio/pluck/`). The live keyboard instrument follows the same picker.

Requires Python 3 and numpy (audio only). All pitch math lives in
`tools/makam_data.py`: pitches are Holdrian commas above written C4 in the
53-comma AEU system, at written pitch with A4 = 440 Hz (dügâh = A). To add a
makam, add an entry to `MAKAMLAR` (and a key signature in
`tools/generate_notation.py`), rerun both generators, and copy an existing
chapter page as a template.
