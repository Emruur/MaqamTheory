# Makam Theory — A Listener's Course

A self-contained static website for learning Turkish makam theory (Rast,
Nihavend, Uşşak, Hüseyni, Hicaz) with synthesized microtonal audio and staff
notation using authentic Arel–Ezgi–Uzdilek (AEU) accidentals.

## Using the site

Open `index.html` directly in a browser, or serve it:

```sh
python3 -m http.server   # then http://localhost:8000
```

## Regenerating the assets

All audio (`audio/*.wav`) and notation (`img/*.svg`) are generated:

```sh
python3 tools/generate_audio.py --check   # verify theory data + synth pitch
python3 tools/generate_audio.py           # write ~60 WAV files
python3 tools/generate_notation.py        # write ~40 SVG files
```

Requires Python 3 and numpy (audio only). All pitch math lives in
`tools/makam_data.py`: pitches are Holdrian commas above written C4 in the
53-comma AEU system, at written pitch with A4 = 440 Hz (dügâh = A). To add a
makam, add an entry to `MAKAMLAR` (and a key signature in
`tools/generate_notation.py`), rerun both generators, and copy an existing
chapter page as a template.
