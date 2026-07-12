"""Shared makam theory data in the Arel-Ezgi-Uzdilek (AEU) 53-comma system.

All pitches are expressed in Holdrian commas above written C4.
Frequency of a pitch: C4_HZ * 2 ** (commas / 53), with A4 (= 40 commas) at 440 Hz.

Diatonic anchors (commas above C4):
  C4=0  D4=9  E4=18  F4=22  G4=31  A4=40  B4=49  C5=53
AEU interval names (in commas):
  B  bakiye            = 4
  S  kucuk mucenneb    = 5
  K  buyuk mucenneb    = 8
  T  tanini            = 9
  A  artik ikili       = 12-13
"""

C4_COMMAS_BELOW_A4 = 40
A4_HZ = 440.0
C4_HZ = A4_HZ * 2 ** (-C4_COMMAS_BELOW_A4 / 53)


def freq(commas: float) -> float:
    return C4_HZ * 2 ** (commas / 53)


# Perde (pitch) names used by the five makams, commas above C4.
PERDE = {
    "yegah": 9,            # D4
    "huseyni asiran": 18,  # E4
    "acem asiran": 22,     # F4
    "irak": 26,            # F#4 (bakiye sharp)
    "rast": 31,            # G4
    "dugah": 40,           # A4
    "kurdi": 44,           # Bb4 (kucuk mucenneb flat)
    "dik kurdi": 45,       # B4 bakiye flat
    "segah": 48,           # B4 koma flat
    "buselik": 49,         # B4
    "cargah": 53,          # C5
    "nim hicaz": 57,       # C#5 (bakiye sharp)
    "neva": 62,            # D5
    "nim hisar": 66,       # Eb5 (kucuk mucenneb flat)
    "hisar": 67,           # Eb5 (bakiye flat)
    "huseyni": 71,         # E5
    "acem": 75,            # F5
    "evic": 79,            # F#5 (bakiye sharp)
    "gerdaniye": 84,       # G5
    "muhayyer": 93,        # A5
    "tiz segah": 101,      # B5 koma flat
    "tiz cargah": 106,     # C6
}

# Genera (cinsler): the tetrachord/pentachord building blocks, as comma steps.
GENUS = {
    "cargah dortlusu": [9, 9, 4],        # T T B
    "buselik dortlusu": [9, 4, 9],       # T B T
    "kurdi dortlusu": [4, 9, 9],         # B T T
    "rast dortlusu": [9, 8, 5],          # T K S
    "ussak dortlusu": [8, 5, 9],         # K S T
    "hicaz dortlusu": [5, 12, 5],        # S A S
    "rast beslisi": [9, 8, 5, 9],        # T K S T
    "buselik beslisi": [9, 4, 9, 9],     # T B T T
    "huseyni beslisi": [8, 5, 9, 9],     # K S T T
    "hicaz beslisi": [5, 12, 5, 9],      # S A S T
}


def steps_to_scale(tonic: int, steps: list[int]) -> list[int]:
    out = [tonic]
    for s in steps:
        out.append(out[-1] + s)
    return out


# Each makam: everything the site needs, in one place.
# "asc"/"desc" are the full scale pitches (tonic -> octave), in commas above C4.
# "seyir" is a short composed demo melody: list of (commas, beats). None = rest.
MAKAMLAR = {
    "rast": {
        "title": "Rast",
        "tonic": PERDE["rast"],
        "guclu": PERDE["neva"],
        "yeden": PERDE["irak"],
        "lower_genus": ("Rast beslisi on rast", "rast beslisi", PERDE["rast"]),
        "upper_genus": ("Rast dortlusu on neva", "rast dortlusu", PERDE["neva"]),
        "asc": steps_to_scale(PERDE["rast"], [9, 8, 5, 9, 9, 8, 5]),
        # Descending form replaces evic (F#, -1 koma) with acem (F natural).
        "desc": steps_to_scale(PERDE["rast"], [9, 8, 5, 9, 9, 4, 9]),
        "seyir_dir": "cikici (ascending)",
        "seyir": [
            (31, 1), (40, 0.5), (48, 0.5), (53, 0.5), (62, 1.5),
            (62, 0.5), (71, 0.5), (79, 0.5), (84, 1.5),
            (84, 0.5), (75, 0.5), (71, 0.5), (62, 1),
            (62, 0.5), (53, 0.5), (48, 0.5), (40, 1),
            (48, 0.5), (40, 0.5), (26, 0.5), (31, 2),
        ],
    },
    "nihavend": {
        "title": "Nihavend",
        "tonic": PERDE["rast"],
        "guclu": PERDE["neva"],
        "yeden": PERDE["irak"],  # written F#4 (bakiye sharp)
        "lower_genus": ("Buselik beslisi on rast", "buselik beslisi", PERDE["rast"]),
        "upper_genus": ("Kurdi dortlusu on neva (desc) / Hicaz flavour (asc)",
                        "kurdi dortlusu", PERDE["neva"]),
        # Ascending: raised leading tone F# (harmonic-minor colour).
        "asc": steps_to_scale(PERDE["rast"], [9, 4, 9, 9, 4, 13, 5]),
        # Descending: natural-minor colour with F natural.
        "desc": steps_to_scale(PERDE["rast"], [9, 4, 9, 9, 4, 9, 9]),
        "seyir_dir": "inici-cikici (descending-ascending)",
        "seyir": [
            (62, 1), (66, 0.5), (62, 0.5), (53, 0.5), (44, 1.5),
            (31, 0.5), (40, 0.5), (44, 0.5), (53, 0.5), (62, 1.5),
            (66, 0.5), (62, 0.5), (53, 0.5), (44, 1),
            (40, 0.5), (44, 0.5), (40, 0.5), (26, 0.5), (31, 2),
        ],
    },
    "ussak": {
        "title": "Ussak",
        "tonic": PERDE["dugah"],
        "guclu": PERDE["neva"],
        "yeden": PERDE["rast"],
        "lower_genus": ("Ussak dortlusu on dugah", "ussak dortlusu", PERDE["dugah"]),
        "upper_genus": ("Buselik beslisi on neva", "buselik beslisi", PERDE["neva"]),
        "asc": steps_to_scale(PERDE["dugah"], [8, 5, 9, 9, 4, 9, 9]),
        "desc": steps_to_scale(PERDE["dugah"], [8, 5, 9, 9, 4, 9, 9]),
        "seyir_dir": "cikici (ascending)",
        "seyir": [
            (40, 1), (48, 0.5), (53, 0.5), (62, 1.5),
            (71, 0.5), (62, 0.5), (53, 0.5), (48, 1),
            (53, 0.5), (48, 0.5), (40, 1.5),
            (31, 0.5), (40, 0.5), (48, 0.5), (40, 2),
        ],
    },
    "huseyni": {
        "title": "Huseyni",
        "tonic": PERDE["dugah"],
        "guclu": PERDE["huseyni"],
        "yeden": PERDE["rast"],
        "lower_genus": ("Huseyni beslisi on dugah", "huseyni beslisi", PERDE["dugah"]),
        "upper_genus": ("Ussak dortlusu on huseyni", "ussak dortlusu", PERDE["huseyni"]),
        "asc": steps_to_scale(PERDE["dugah"], [8, 5, 9, 9, 8, 5, 9]),
        "desc": steps_to_scale(PERDE["dugah"], [8, 5, 9, 9, 8, 5, 9]),
        "seyir_dir": "inici-cikici (descending-ascending)",
        "seyir": [
            (71, 1), (79, 0.5), (84, 0.5), (79, 0.5), (71, 1.5),
            (62, 0.5), (53, 0.5), (48, 0.5), (40, 1.5),
            (40, 0.5), (48, 0.5), (53, 0.5), (62, 0.5), (71, 1.5),
            (62, 0.5), (53, 0.5), (48, 0.5), (40, 2),
        ],
    },
    "hicaz": {
        "title": "Hicaz",
        "tonic": PERDE["dugah"],
        "guclu": PERDE["neva"],
        "yeden": PERDE["rast"],
        "lower_genus": ("Hicaz dortlusu on dugah", "hicaz dortlusu", PERDE["dugah"]),
        "upper_genus": ("Rast beslisi on neva", "rast beslisi", PERDE["neva"]),
        "asc": steps_to_scale(PERDE["dugah"], [5, 12, 5, 9, 8, 5, 9]),
        "desc": steps_to_scale(PERDE["dugah"], [5, 12, 5, 9, 8, 5, 9]),
        "seyir_dir": "cikici (ascending)",
        "seyir": [
            (40, 1), (45, 0.5), (57, 0.5), (62, 1.5),
            (71, 0.5), (79, 0.5), (71, 0.5), (62, 1.5),
            (57, 0.5), (45, 0.5), (40, 1),
            (31, 0.5), (40, 0.5), (45, 0.5), (57, 0.5),
            (62, 0.5), (57, 0.5), (45, 0.5), (40, 2),
        ],
    },
}

MAKAM_ORDER = ["rast", "nihavend", "ussak", "huseyni", "hicaz"]

# Song excerpts, transcribed from the SymbTr-derived ABC corpus
# (Turkish Makam Database, ifdo.ca/~seymour/runabc/makams). Events are
# (commas, beats); None = rest. Ornaments/32nds simplified to 16th resolution.
SONGS = {
    "rast": {
        "title": "Yine Bir Gülnihal",
        "credit": "Hammâmîzâde İsmail Dede Efendi · Rast şarkı, semâî (3/4)",
        "bpm": 138,
        "beats_per_bar": 3,
        "events": [
            # "Yine bir gülnihal aldı bu gönlümü" (with both endings)
            (31, 2), (48, 1), (40, 3), (9, 1), (18, 1), (26, 1),
            (31, 2), (None, 1),
            (31, 2), (48, 1), (40, 3), (40, 1), (48, 1), (53, 1),
            (48, 2), (None, 1),
            # "Simüten gonca fem bî bedel ol güzel"
            (53, 2), (71, 1), (62, 1), (53, 1), (48, 1),
            (40, 1), (48, 1), (53, 1), (48, 2), (None, 1),
            (31, 2), (48, 1), (40, 3), (9, 1), (18, 1), (26, 1),
            (31, 2), (None, 1),
        ],
    },
    "nihavend": {
        "title": "Kâtibim (Üsküdar'a Gider İken)",
        "credit": "Anonymous İstanbul türküsü · nim sofyan (2/4)",
        "bpm": 88,
        "beats_per_bar": 2,
        "events": [
            # "Üsküdar'a gider iken aldı da bir yağmur"
            (31, 0.75), (62, 0.25), (62, 0.5), (62, 0.5),
            (66, 0.25), (62, 0.25), (66, 0.25), (75, 0.25), (62, 0.5), (62, 0.5),
            (53, 0.5), (53, 0.25), (53, 0.25), (44, 0.5), (53, 0.5),
            (62, 0.25), (66, 0.25), (62, 0.25), (53, 0.25),
            (44, 0.25), (40, 0.25), (31, 0.5),
            # "Kâtibimin setresi uzun eteği çamur"
            (31, 0.75), (40, 0.25), (44, 0.5), (53, 0.5),
            (62, 0.25), (66, 0.25), (62, 0.25), (53, 0.25),
            (44, 0.25), (40, 0.25), (31, 0.5),
            (40, 0.25), (53, 0.25), (44, 0.25), (40, 0.25),
            (40, 0.25), (31, 0.25), (31, 0.25), (26, 0.25),
            (31, 2),
        ],
    },
    "ussak": {
        "title": "Uzun İnce Bir Yoldayım",
        "credit": "Âşık Veysel · Uşşak türkü, sofyan (4/4) — simplified skeleton",
        "bpm": 76,
        "beats_per_bar": 4,
        "events": [
            # "Uzun ince bir yoldayım"
            (62, 0.5), (53, 0.25), (62, 0.25), (62, 0.5), (53, 0.25), (40, 0.25),
            (53, 0.25), (48, 0.5), (40, 0.25), (48, 0.25), (31, 0.25), (40, 0.5),
            # "Bilmiyorum ne haldayım" (high phrase)
            (84, 0.5), (79, 0.25), (84, 0.25), (84, 0.75), (84, 0.25),
            (84, 0.25), (75, 0.5), (71, 0.25), (84, 0.25), (75, 0.25), (75, 0.5),
            (79, 0.25), (71, 0.5), (62, 0.25), (75, 0.25), (71, 0.25), (71, 0.5),
            (71, 0.25), (62, 0.25), (62, 0.25), (53, 0.25),
            (71, 0.25), (62, 0.25), (62, 0.5),
            # "Gidiyorum gündüz gece"
            (62, 0.5), (53, 0.25), (48, 0.25), (40, 0.5), (62, 0.25), (48, 0.25),
            (53, 0.5), (53, 0.25), (48, 0.25), (40, 0.5),
            (53, 0.25), (48, 0.25),
            (48, 0.25), (40, 0.25), (40, 0.25), (31, 0.25),
            (48, 0.25), (40, 0.25), (40, 0.5), (40, 2),
        ],
    },
    "huseyni": {
        "title": "Çanakkale İçinde",
        "credit": "İhsan Ozanoğlu / anonymous · catalogued as Nevâ türkü, sofyan (4/4)",
        "bpm": 93,
        "beats_per_bar": 4,
        "events": [
            # "Çanakkale içinde vurdular beni"
            (None, 1), (31, 0.5), (40, 0.5), (40, 0.5), (40, 1.5),
            (84, 0.75), (79, 0.25), (71, 0.75), (62, 0.25), (62, 1.5), (53, 0.5),
            (62, 1), (71, 1), (71, 0.25), (84, 0.25), (79, 0.25), (84, 0.25),
            (71, 0.75), (62, 0.25),
            (62, 2), (62, 1), (None, 1),
            # "Ölmeden mezara koydular beni / Of gençliğim eyvah"
            (62, 1.5), (71, 0.5), (71, 1), (66, 0.75), (62, 0.25),
            (62, 1), (66, 0.5), (62, 0.5), (53, 0.5), (48, 0.5), (53, 1),
            (48, 0.5), (53, 0.5), (62, 1), (62, 0.25), (66, 0.25), (62, 0.25),
            (71, 0.25), (53, 0.5), (48, 0.5),
            (40, 2), (48, 0.5), (53, 0.5), (62, 0.5), (71, 0.5),
            (53, 0.5), (48, 0.75), (31, 0.25), (40, 0.5), (48, 0.5), (40, 1.5),
            (40, 2), (40, 1), (None, 1),
        ],
    },
    "hicaz": {
        "title": "Ada Sahillerinde Bekliyorum",
        "credit": "Anonymous İstanbul kantosu · Hicaz, sofyan (4/4) — simplified",
        "bpm": 80,
        "beats_per_bar": 4,
        "events": [
            # "Ah — Adalar sahilinde bekliyorum"
            (40, 0.5), (93, 3.5),
            (93, 1), (84, 0.5), (93, 0.5), (93, 1), (93, 1),
            (93, 0.25), (84, 0.25), (93, 0.25), (102, 0.25), (93, 0.5), (84, 0.5),
            (79, 0.5), (79, 0.25), (71, 0.25), (84, 0.5), (84, 0.25), (79, 0.25),
            # "Seni yârim serian istiyorum"
            (71, 1), (71, 0.5), (79, 0.5), (84, 0.5), (93, 0.5),
            (84, 0.25), (79, 0.25), (71, 0.5),
            (79, 0.5), (84, 0.25), (93, 0.25), (84, 0.25), (75, 0.25),
            (71, 0.25), (62, 0.25), (71, 0.5), (79, 0.5),
            (93, 0.25), (84, 0.25), (79, 0.25), (71, 0.25),
            # "Her zamanki yerimde bekliyorum"
            (62, 1), (71, 0.5), (75, 0.5), (75, 0.5), (75, 0.25), (71, 0.25), (75, 1),
            (71, 0.5), (75, 0.25), (84, 0.25), (75, 0.25), (71, 0.25),
            (62, 0.5), (57, 0.5), (62, 0.5),
            (71, 0.25), (75, 0.25), (71, 0.25), (62, 0.25),
            # "Beni şâd et Şâdiye başın için"
            (57, 1), (57, 0.5), (62, 0.5), (67, 0.75), (62, 0.25), (62, 0.75), (57, 0.25),
            (57, 0.75), (45, 0.25), (40, 0.5), (45, 0.5), (57, 0.5), (62, 0.5),
            (71, 0.25), (62, 0.25), (57, 0.25), (45, 0.25),
            (40, 3), (None, 1),
        ],
    },
}

# Keyboard-instrument note sets: ~1.5 octaves per makam (yeden below the
# tonic up past the octave), flags: t=tonic/octave, g=guclu, y=yeden.
KEYBOARD = {
    "rast": [(26, "ırak", "y"), (31, "rast", "t"), (40, "dügâh", ""),
             (48, "segâh", ""), (53, "çargâh", ""), (62, "nevâ", "g"),
             (71, "hüseynî", ""), (75, "acem", ""), (79, "eviç", ""),
             (84, "gerdaniye", "t"), (93, "muhayyer", "")],
    "nihavend": [(26, "F♯ yeden", "y"), (31, "rast", "t"), (40, "dügâh", ""),
                 (44, "kürdî", ""), (53, "çargâh", ""), (62, "nevâ", "g"),
                 (66, "nim hisar", ""), (75, "acem", ""), (79, "eviç", ""),
                 (84, "gerdaniye", "t"), (93, "muhayyer", "")],
    "ussak": [(31, "rast", "y"), (40, "dügâh", "t"), (48, "segâh", ""),
              (53, "çargâh", ""), (62, "nevâ", "g"), (71, "hüseynî", ""),
              (75, "acem", ""), (84, "gerdaniye", ""), (93, "muhayyer", "t"),
              (101, "tiz segâh", ""), (106, "tiz çargâh", "")],
    "huseyni": [(31, "rast", "y"), (40, "dügâh", "t"), (48, "segâh", ""),
                (53, "çargâh", ""), (62, "nevâ", ""), (71, "hüseynî", "g"),
                (79, "eviç", ""), (84, "gerdaniye", ""), (93, "muhayyer", "t"),
                (101, "tiz segâh", ""), (106, "tiz çargâh", "")],
    "hicaz": [(31, "rast", "y"), (40, "dügâh", "t"), (45, "dik kürdî", ""),
              (57, "nim hicaz", ""), (62, "nevâ", "g"), (71, "hüseynî", ""),
              (79, "eviç", ""), (84, "gerdaniye", ""), (93, "muhayyer", "t"),
              (98, "tiz dik kürdî", ""), (106, "tiz çargâh", "")],
}

# Comparison genera for chapter 4: every genus type played from dugah (A4).
GENUS_DEMOS = {
    "cargah": ("cargah dortlusu", PERDE["dugah"]),
    "buselik": ("buselik dortlusu", PERDE["dugah"]),
    "kurdi": ("kurdi dortlusu", PERDE["dugah"]),
    "rast": ("rast dortlusu", PERDE["dugah"]),
    "ussak": ("ussak dortlusu", PERDE["dugah"]),
    "hicaz": ("hicaz dortlusu", PERDE["dugah"]),
}


def check() -> None:
    """Assert the theory data is internally consistent."""
    for name, steps in GENUS.items():
        total = sum(steps)
        if "dortlusu" in name:
            assert total == 22, f"{name}: tetrachord must span 22 commas, got {total}"
        else:
            assert total == 31, f"{name}: pentachord must span 31 commas, got {total}"

    for key, m in MAKAMLAR.items():
        for form in ("asc", "desc"):
            scale = m[form]
            assert len(scale) == 8, f"{key} {form}: expected 8 pitches"
            span = scale[-1] - scale[0]
            assert span == 53, f"{key} {form}: octave must be 53 commas, got {span}"
        assert m["asc"][0] == m["tonic"]
        # Lower genus of each makam must start on the tonic.
        _, genus_name, root = m["lower_genus"]
        assert root == m["tonic"], f"{key}: lower genus root != tonic"
        genus_pitches = steps_to_scale(root, GENUS[genus_name])
        assert genus_pitches == m["asc"][: len(genus_pitches)], (
            f"{key}: lower genus {genus_pitches} does not match scale {m['asc']}"
        )

    for key, song in SONGS.items():
        assert key in MAKAMLAR, f"song for unknown makam {key}"
        total = sum(b for _, b in song["events"])
        bpb = song["beats_per_bar"]
        assert abs(total / bpb - round(total / bpb)) < 1e-9, (
            f"{key} song: {total} beats does not fill whole {bpb}-beat bars")
        used = {c for c, _ in song["events"] if c is not None}
        allowed = set(MAKAMLAR[key]["asc"]) | set(MAKAMLAR[key]["desc"])
        allowed |= {MAKAMLAR[key]["yeden"]}
        # Known extras: low-register notes (9,18,26), chromatic passing/color
        # tones (57,67,102), and evic 79 in Ussak folk practice (Huseyni drift).
        # (66 = nim hisar colour in the Canakkale refrain; 75 = descending
        # acem in the Hicaz kanto, mirroring Rast's evic->acem swap.)
        extras = used - allowed - {9, 18, 26, 57, 66, 67, 75, 79, 102}
        assert not extras, f"{key} song: unexpected pitches {sorted(extras)}"

    # A couple of frequency spot checks.
    assert abs(freq(40) - 440.0) < 1e-9, "dugah (A4) must be 440 Hz"
    assert abs(freq(93) - 880.0) < 1e-9, "muhayyer (A5) must be 880 Hz"
    assert abs(freq(31) - 391.1) < 0.5, f"rast (G4) ~391 Hz, got {freq(31):.2f}"
    print("makam_data: all checks passed")


if __name__ == "__main__":
    check()
