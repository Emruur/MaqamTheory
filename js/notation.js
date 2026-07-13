/* Live scale notation for the playground. Renders the selected makam's
   scale as inline SVG (same drawing style as tools/generate_notation.py)
   and highlights perdeler as they are played on the keyboard instrument.
   The displayed form follows the player's 7th degree: hearing the
   ascending-only variant (e.g. eviç) shows the çıkıcı staff, the
   descending-only variant (e.g. acem) flips to the inici staff.
   Root transposition never changes the written notation — an ahenk change
   moves sound, not spelling — so highlighting is by written commas. */

window.MaqamSheet = (function () {
  "use strict";

  const LETTERS = "CDEFGAB";

  // commas above written C4 -> [letter, octave, accidental kind]
  const SPELL = {
    31: ["G", 4, null],
    40: ["A", 4, null],
    44: ["B", 4, "flat5"],
    45: ["B", 4, "flat4"],
    48: ["B", 4, "flat1"],
    53: ["C", 5, null],
    57: ["C", 5, "sharp4"],
    62: ["D", 5, null],
    66: ["E", 5, "flat5"],
    71: ["E", 5, null],
    75: ["F", 5, null],
    79: ["F", 5, "sharp4"],
    84: ["G", 5, null],
    93: ["A", 5, null],
  };

  const PERDE = {
    31: "rast", 40: "dügâh", 44: "kürdî", 45: "dik kürdî", 48: "segâh",
    53: "çargâh", 57: "nim hicaz", 62: "nevâ", 66: "nim hisar",
    71: "hüseynî", 75: "acem", 79: "eviç", 84: "gerdaniye", 93: "muhayyer",
  };

  const WEST_SUFFIX = {
    flat1: "↓¹", flat4: "♭⁴", flat5: "♭", sharp4: "♯", sharp5: "♯⁵",
  };

  const KEYSIG = {
    rast: [48, 79], nihavend: [44, 66], ussak: [48],
    huseyni: [48, 79], hicaz: [45, 57],
  };

  // Full scales tonic -> octave, always stored ascending (from makam_data.py).
  const SCALES = {
    rast:     { asc: [31, 40, 48, 53, 62, 71, 79, 84],
                desc: [31, 40, 48, 53, 62, 71, 75, 84] },
    nihavend: { asc: [31, 40, 44, 53, 62, 66, 79, 84],
                desc: [31, 40, 44, 53, 62, 66, 75, 84] },
    ussak:    { asc: [40, 48, 53, 62, 71, 75, 84, 93],
                desc: [40, 48, 53, 62, 71, 75, 84, 93] },
    huseyni:  { asc: [40, 48, 53, 62, 71, 79, 84, 93],
                desc: [40, 48, 53, 62, 71, 79, 84, 93] },
    hicaz:    { asc: [40, 45, 57, 62, 71, 79, 84, 93],
                desc: [40, 45, 57, 62, 71, 79, 84, 93] },
  };

  let box = null, makam = null, label = "", mode = "asc";
  const active = new Set();

  function stepOf(letter, octave) {
    return (octave - 4) * 7 + LETTERS.indexOf(letter);
  }
  function yOf(step) { return 40 - (step - 2) * 5; }

  /* ---- SVG primitives (ported from generate_notation.py) ---- */
  function line(p, x1, y1, x2, y2, w, color) {
    p.push('<line x1="' + x1 + '" y1="' + y1 + '" x2="' + x2 + '" y2="' + y2 +
           '" stroke="' + (color || "#2b2b2b") + '" stroke-width="' + (w || 1.1) + '"/>');
  }

  function path(p, d, w) {
    p.push('<path d="' + d + '" stroke="#2b2b2b" stroke-width="' + (w || 1.6) +
           '" fill="none" stroke-linecap="round" stroke-linejoin="round"/>');
  }

  function drawClef(p, x) {
    path(p,
      "M " + (x - 0.5) + " 45 " +
      "C " + (x + 0.5) + " 34 " + (x + 2.5) + " 14 " + (x + 3) + " -2 " +
      "C " + (x + 3.2) + " -12 " + (x + 1) + " -19 " + (x - 2) + " -15 " +
      "C " + (x - 4.5) + " -11.5 " + (x - 3) + " -4 " + (x + 0.5) + " 2 " +
      "C " + (x + 4) + " 8.5 " + (x + 9.5) + " 14 " + (x + 9.5) + " 24 " +
      "C " + (x + 9.5) + " 33 " + (x + 2.5) + " 37.5 " + (x - 3.5) + " 34.5 " +
      "C " + (x - 9) + " 31.5 " + (x - 8) + " 22.5 " + (x - 1.5) + " 21.5 " +
      "C " + (x + 3) + " 21 " + (x + 5.5) + " 25 " + (x + 4) + " 29 ", 2.5);
    path(p,
      "M " + (x - 0.5) + " 45 C " + (x - 1) + " 50 " + (x - 7.5) + " 51 " +
      (x - 8) + " 46.5 C " + (x - 8.2) + " 43.5 " + (x - 5) + " 42.5 " +
      (x - 3.5) + " 45", 2.2);
  }

  function drawFlat(p, x, y, mirrored, strokes) {
    const sgn = mirrored ? -1 : 1;
    const sx = x - 2.5 * sgn;
    path(p, "M " + sx + " " + (y - 16) + " L " + sx + " " + (y + 7.5), 1.5);
    path(p, "M " + sx + " " + (y + 7.5) +
            " C " + (sx + 8 * sgn) + " " + (y + 1) +
            " " + (sx + 7 * sgn) + " " + (y - 4.5) +
            " " + sx + " " + (y - 1.5), 1.5);
    for (let i = 0; i < (strokes || 0); i++) {
      const yy = y - 9 - i * 4.5;
      path(p, "M " + (x - 4.5) + " " + (yy + 2.5) +
              " L " + (x + 4.5) + " " + (yy - 2.5), 1.3);
    }
  }

  function drawSharp(p, x, y, verticals, slash) {
    if (verticals === 2) {
      line(p, x - 2.1, y - 11, x - 2.1, y + 12, 1.4);
      line(p, x + 2.1, y - 12, x + 2.1, y + 11, 1.4);
    } else {
      line(p, x, y - 11.5, x, y + 11.5, 1.4);
    }
    [y - 3.6, y + 4.4].forEach(function (yy) {
      path(p, "M " + (x - 5) + " " + (yy + 1.6) +
              " L " + (x + 5) + " " + (yy - 1.6), 2.6);
    });
    if (slash) {
      path(p, "M " + (x - 6) + " " + (y + 10) +
              " L " + (x + 6) + " " + (y - 13), 1.3);
    }
  }

  function drawNatural(p, x, y) {
    line(p, x - 2.1, y - 10, x - 2.1, y + 4.5, 1.4);
    line(p, x + 2.1, y - 4.5, x + 2.1, y + 10, 1.4);
    [y - 3.2, y + 3.2].forEach(function (yy) {
      path(p, "M " + (x - 2.1) + " " + (yy + 1.4) +
              " L " + (x + 2.1) + " " + (yy - 1.4), 2.4);
    });
  }

  function drawAccidental(p, kind, x, y) {
    if (kind === "flat1") drawFlat(p, x, y, true, 0);
    else if (kind === "flat4") drawFlat(p, x, y, false, 1);
    else if (kind === "flat5") drawFlat(p, x, y, false, 0);
    else if (kind === "flat8") drawFlat(p, x, y, false, 2);
    else if (kind === "sharp1") drawSharp(p, x, y, 1, false);
    else if (kind === "sharp4") drawSharp(p, x, y, 2, false);
    else if (kind === "sharp5") drawSharp(p, x, y, 1, true);
    else if (kind === "sharp8") drawSharp(p, x, y, 2, true);
    else if (kind === "natural") drawNatural(p, x, y);
  }

  function drawLedger(p, x, step) {
    for (let s = step; s <= 0; s++) {
      if (s % 2 === 0) line(p, x - 10, yOf(s), x + 10, yOf(s), 1.2, "#555");
    }
    for (let s = step; s >= 12; s--) {
      if (s % 2 === 0) line(p, x - 10, yOf(s), x + 10, yOf(s), 1.2, "#555");
    }
  }

  function text(p, x, y, s, size, anchor, color, style, weight) {
    p.push('<text x="' + x + '" y="' + y + '" font-size="' + size +
           '" text-anchor="' + (anchor || "middle") + '" fill="' + color +
           '" font-weight="' + (weight || "normal") + '" style="' +
           (style || "") + '">' + s + "</text>");
  }

  function westernName(letter, acc) {
    return letter + (WEST_SUFFIX[acc] || "");
  }

  /* ---- rendering ---- */
  function variantSets() {
    const sc = SCALES[makam];
    return {
      ascOnly: sc.asc.filter(function (c) { return sc.desc.indexOf(c) < 0; }),
      descOnly: sc.desc.filter(function (c) { return sc.asc.indexOf(c) < 0; }),
    };
  }

  function headHTML(same) {
    const v = variantSets();
    let h = '<div class="ss-head"><span class="ss-title">' + label +
            " scale</span>";
    if (same) {
      h += '<span class="ss-note">çıkıcı = inici — same both ways</span>';
    } else {
      h += '<span class="ss-note">follows your 7th: ' +
           v.ascOnly.map(function (c) { return PERDE[c]; }).join(", ") +
           " ⇒ ↑ · " +
           v.descOnly.map(function (c) { return PERDE[c]; }).join(", ") +
           " ⇒ ↓</span>";
      h += '<span class="ss-mode">' +
           '<button type="button" data-mode="asc"' +
           (mode === "asc" ? ' class="selected"' : "") +
           ">çıkıcı ↑</button>" +
           '<button type="button" data-mode="desc"' +
           (mode === "desc" ? ' class="selected"' : "") +
           ">inici ↓</button></span>";
    }
    return h + "</div>";
  }

  function render() {
    const sc = SCALES[makam];
    const sig = KEYSIG[makam];
    const same = sc.asc.join() === sc.desc.join();
    if (same) mode = "asc";
    const pitches = mode === "desc" ? sc.desc.slice().reverse() : sc.asc.slice();
    const n = pitches.length;
    const noteDx = 58;
    const xNotes = 96 + 18 * sig.length;
    const width = xNotes + n * noteDx + 10;
    const maxStep = Math.max.apply(null, pitches.map(function (c) {
      return stepOf(SPELL[c][0], SPELL[c][1]);
    }));
    const oy = maxStep >= 12 ? 34 : 26;   // headroom for ledger notes
    const height = oy + 102;

    const p = [];
    p.push('<svg xmlns="http://www.w3.org/2000/svg" viewBox="-6 ' + (-oy) +
           " " + width + " " + height + '" width="' + width + '" height="' +
           height + '" font-family="Georgia, serif">');
    for (let i = 0; i < 5; i++) line(p, 0, i * 10, width - 16, i * 10, 1.1, "#555");
    drawClef(p, 14);

    const sigAcc = {};
    let x = 42;
    sig.forEach(function (commas) {
      const s = SPELL[commas];
      sigAcc[s[0]] = s[2];
      drawAccidental(p, s[2], x, yOf(stepOf(s[0], s[1])));
      x += 17;
    });

    pitches.forEach(function (commas, i) {
      const s = SPELL[commas];
      const letter = s[0], acc = s[2];
      const cx = xNotes + i * noteDx;
      const step = stepOf(letter, s[1]);
      const y = yOf(step);
      p.push('<g class="sn" data-commas="' + commas + '">');
      p.push('<circle class="halo" cx="' + cx + '" cy="' + y + '" r="11"/>');
      if (acc !== (sigAcc[letter] || null) && (acc || letter in sigAcc)) {
        drawAccidental(p, acc || "natural", cx - 14, y);
      }
      drawLedger(p, cx, step);
      p.push('<ellipse class="nh" cx="' + cx + '" cy="' + y +
             '" rx="6.2" ry="4.4" transform="rotate(-16 ' + cx + " " + y +
             ')" fill="#fffdf7" stroke="#2b2b2b" stroke-width="2.2"/>');
      text(p, cx, 66, PERDE[commas] || "", 10.5, "middle", "#7a5c2e",
           "font-style:italic");
      text(p, cx, Math.min(-12, y - 12), westernName(letter, acc),
           10.5, "middle", "#555");
      p.push("</g>");
      if (i < n - 1) {
        text(p, cx + noteDx / 2, 84, String(pitches[i + 1] - commas),
             12, "middle", "#a33", "", "bold");
      }
    });
    text(p, xNotes - 30, 84, "commas:", 10, "end", "#a33");
    p.push("</svg>");

    box.innerHTML = headHTML(same) +
      '<div class="ss-staff">' + p.join("\n") + "</div>";
    box.querySelectorAll(".ss-mode button").forEach(function (b) {
      b.addEventListener("click", function () {
        mode = b.dataset.mode;
        render();
      });
    });
    applyHighlights();
  }

  function pc(c) { return ((c % 53) + 53) % 53; }

  function applyHighlights() {
    if (!box) return;
    const groups = Array.prototype.slice.call(box.querySelectorAll(".sn"));
    groups.forEach(function (g) { g.classList.remove("on"); });
    active.forEach(function (c) {
      let hits = groups.filter(function (g) { return +g.dataset.commas === c; });
      if (!hits.length) {
        // Octave twin: e.g. ırak lights eviç, muhayyer lights dügâh.
        hits = groups.filter(function (g) {
          return pc(+g.dataset.commas) === pc(c);
        });
      }
      hits.forEach(function (g) { g.classList.add("on"); });
    });
  }

  function note(commas, on) {
    if (!box || !makam) return;
    if (on) {
      active.add(commas);
      const v = variantSets();
      if (v.descOnly.indexOf(commas) >= 0 && mode !== "desc") {
        mode = "desc";
        render();
        return;
      }
      if (v.ascOnly.indexOf(commas) >= 0 && mode !== "asc") {
        mode = "asc";
        render();
        return;
      }
    } else {
      active.delete(commas);
    }
    applyHighlights();
  }

  function mount(el, key, title) {
    box = el;
    makam = key;
    label = title || key;
    mode = "asc";
    active.clear();
    render();
  }

  return { mount: mount, note: note };
})();
