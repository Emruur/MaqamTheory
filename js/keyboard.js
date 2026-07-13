/* Computer-keyboard instrument: play the makam's perdeler live.
   Home-row keys (layout-independent event.code) map to scale degrees;
   Web Audio synthesizes the exact AEU comma pitches. Hold to sustain.
   The row above (Q W E R T ...) carries 12-TET "piano twin" keys for the
   microtonal perdeler only, aligned above their makam counterparts, so the
   comma differences can be compared directly. Voices follow the site-wide
   picker; the root selector transposes the whole grid (ahenk-style). */

(function () {
  "use strict";

  const KEY_CODES = ["KeyA", "KeyS", "KeyD", "KeyF", "KeyG", "KeyH",
                     "KeyJ", "KeyK", "KeyL", "Semicolon", "Quote"];
  const KEY_CAPS = ["A", "S", "D", "F", "G", "H", "J", "K", "L", ";", "'"];
  const TOP_CODES = ["KeyQ", "KeyW", "KeyE", "KeyR", "KeyT", "KeyY",
                     "KeyU", "KeyI", "KeyO", "KeyP", "BracketLeft"];
  const TOP_CAPS = ["Q", "W", "E", "R", "T", "Y", "U", "I", "O", "P", "["];
  const TET_NAMES = ["A", "B♭", "B", "C", "C♯", "D", "E♭", "E",
                     "F", "F♯", "G", "G♯"];

  const VOICES = {
    warm: {
      label: "Warm synth",
      harmonics: [0, 1, 0.42, 0.28, 0.12, 0.08, 0.045],
    },
    ney: {
      label: "Breathy ney",
      harmonics: [0, 1, 0.14, 0.40, 0.09, 0.17, 0.05, 0.07],
    },
    pluck: {
      label: "Plucked oud",
      harmonics: [0, 1, 0.62, 0.45, 0.30, 0.19, 0.12, 0.08, 0.05],
    },
  };

  const box = document.querySelector(".kbd-instrument");
  if (!box) return;

  // Entry format: commas|perde|flag|westernSemitone (western only for
  // microtonal perdeler; semitones from A4 in 12-TET at written pitch).
  const notes = box.dataset.notes.split(",").map(function (s) {
    const parts = s.split("|");
    return {
      commas: +parts[0],
      perde: parts[1],
      flag: parts[2] || "",
      western: parts[3] === undefined || parts[3] === "" ? null : +parts[3],
    };
  });

  /* ---- transposable root (ahenk) ---- */
  const NATURALS = { C: 0, D: 9, E: 18, F: 22, G: 31, A: 40, B: 49 };
  const ROOT_ORDER = ["A", "B", "C", "D", "E", "F", "G"];
  const tonicCommas = (notes.find(function (n) { return n.flag === "t"; })
                       || notes[0]).commas;
  const writtenRoot = Object.keys(NATURALS).find(function (L) {
    return NATURALS[L] === tonicCommas % 53;
  }) || "G";
  // G-tonic makams transpose only downward from written pitch; A-tonic
  // makams only upward. Together the five makams span about two octaves.
  const goesDown = writtenRoot === "G";
  const makamKey = (document.body.className.match(/makam-(\w+)/) || [])[1] || "x";
  let root = writtenRoot;
  try {
    const saved = localStorage.getItem("maqam-root-" + makamKey);
    if (saved in NATURALS) root = saved;
  } catch (e) {}

  function offsetCommas() {
    let d = NATURALS[root] - (tonicCommas % 53);
    if (goesDown && d > 0) d -= 53;
    if (!goesDown && d < 0) d += 53;
    return d;
  }

  function soundingTonicName() {
    const c = tonicCommas + offsetCommas();
    return root + (4 + Math.floor(c / 53));
  }

  let ctx = null, master = null, noiseBuf = null;
  const waves = {};
  const active = new Map();   // id (number | "w"+number) -> handle
  const keyEls = [];          // makam keys
  const westEls = {};         // index -> western key element

  // Follow the site-wide voice picker (js/voice.js).
  let voice = "warm";
  if (window.MaqamVoice) {
    voice = window.MaqamVoice.get();
    window.MaqamVoice.onChange(function (v) {
      voice = v in VOICES ? v : "warm";
    });
    if (!(voice in VOICES)) voice = "warm";
  }

  function ensureAudio() {
    if (!ctx) {
      ctx = new (window.AudioContext || window.webkitAudioContext)();
      master = ctx.createGain();
      master.gain.value = 0.9;
      const lp = ctx.createBiquadFilter();
      lp.type = "lowpass";
      lp.frequency.value = 6200;
      master.connect(lp).connect(ctx.destination);
      Object.keys(VOICES).forEach(function (k) {
        const h = VOICES[k].harmonics;
        waves[k] = ctx.createPeriodicWave(
          new Float32Array(h.length), Float32Array.from(h));
      });
      noiseBuf = ctx.createBuffer(1, ctx.sampleRate * 1.5, ctx.sampleRate);
      const d = noiseBuf.getChannelData(0);
      for (let i = 0; i < d.length; i++) d[i] = Math.random() * 2 - 1;
    }
    if (ctx.state === "suspended") ctx.resume();
  }

  function freqOf(commas) {
    return 440 * Math.pow(2, (commas + offsetCommas() - 40) / 53);
  }

  function westernFreqOf(semitones) {
    // The piano twin, moved by the same ratio as the root transposition,
    // so the comma-sized gap to its makam neighbour is preserved.
    return 440 * Math.pow(2, semitones / 12) *
           Math.pow(2, offsetCommas() / 53);
  }

  function startWarm(f, t) {
    const osc = ctx.createOscillator();
    osc.setPeriodicWave(waves.warm);
    osc.frequency.value = f;
    const g = ctx.createGain();
    g.gain.setValueAtTime(0.0001, t);
    g.gain.exponentialRampToValueAtTime(0.30, t + 0.025);
    g.gain.exponentialRampToValueAtTime(0.16, t + 0.7);
    osc.connect(g).connect(master);
    osc.start(t);
    return { off: function (te) { release(g, [osc], te, 0.35); } };
  }

  function startNey(f, t) {
    const osc = ctx.createOscillator();
    osc.setPeriodicWave(waves.ney);
    osc.frequency.value = f;
    const lfo = ctx.createOscillator();
    lfo.frequency.value = 4.8;
    const depth = ctx.createGain();
    depth.gain.setValueAtTime(0, t);
    depth.gain.linearRampToValueAtTime(f * 0.004, t + 0.6);
    lfo.connect(depth).connect(osc.frequency);
    const noise = ctx.createBufferSource();
    noise.buffer = noiseBuf;
    noise.loop = true;
    const bp = ctx.createBiquadFilter();
    bp.type = "bandpass";
    bp.frequency.value = f * 2;
    bp.Q.value = 9;
    const ng = ctx.createGain();
    ng.gain.setValueAtTime(0.0001, t);
    ng.gain.exponentialRampToValueAtTime(0.035, t + 0.12);
    noise.connect(bp).connect(ng).connect(master);
    const g = ctx.createGain();
    g.gain.setValueAtTime(0.0001, t);
    g.gain.exponentialRampToValueAtTime(0.26, t + 0.09);
    g.gain.exponentialRampToValueAtTime(0.20, t + 0.9);
    osc.connect(g).connect(master);
    osc.start(t); lfo.start(t); noise.start(t);
    return { off: function (te) {
      release(ng, [noise], te, 0.18);
      release(g, [osc, lfo], te, 0.28);
    } };
  }

  function startPluck(f, t) {
    const osc = ctx.createOscillator();
    osc.setPeriodicWave(waves.pluck);
    osc.frequency.value = f;
    const lp = ctx.createBiquadFilter();
    lp.type = "lowpass";
    lp.frequency.setValueAtTime(Math.min(f * 9, 7500), t);
    lp.frequency.exponentialRampToValueAtTime(Math.max(f * 2, 700), t + 0.9);
    const g = ctx.createGain();
    g.gain.setValueAtTime(0.0001, t);
    g.gain.exponentialRampToValueAtTime(0.34, t + 0.006);
    g.gain.exponentialRampToValueAtTime(0.002, t + 1.6);
    osc.connect(lp).connect(g).connect(master);
    osc.start(t);
    return { off: function (te) { release(g, [osc], te, 0.12); } };
  }

  function release(gainNode, sources, t, secs) {
    gainNode.gain.cancelScheduledValues(t);
    gainNode.gain.setValueAtTime(Math.max(gainNode.gain.value, 0.0001), t);
    gainNode.gain.exponentialRampToValueAtTime(0.0001, t + secs);
    sources.forEach(function (s) { s.stop(t + secs + 0.05); });
  }

  const STARTERS = { warm: startWarm, ney: startNey, pluck: startPluck };

  function soundOn(id, freq, el) {
    if (active.has(id)) return;
    ensureAudio();
    active.set(id, STARTERS[voice](freq, ctx.currentTime));
    el.classList.add("active");
  }

  function soundOff(id, el) {
    const h = active.get(id);
    if (!h) return;
    active.delete(id);
    h.off(ctx.currentTime);
    el.classList.remove("active");
  }

  function noteOn(i) {
    if (i >= 0 && i < notes.length) {
      soundOn(i, freqOf(notes[i].commas), keyEls[i]);
    }
  }
  function noteOff(i) {
    if (keyEls[i]) soundOff(i, keyEls[i]);
  }
  function westOn(i) {
    if (notes[i] && notes[i].western !== null) {
      soundOn("w" + i, westernFreqOf(notes[i].western), westEls[i]);
    }
  }
  function westOff(i) {
    if (westEls[i]) soundOff("w" + i, westEls[i]);
  }

  /* ---- root selector UI ---- */
  const rootRow = document.createElement("div");
  rootRow.className = "kbd-root";
  const rootLabel = document.createElement("span");
  rootLabel.className = "kr-label";
  rootLabel.textContent = "Root:";
  rootRow.appendChild(rootLabel);
  const rootBtns = {};
  const rootStatus = document.createElement("span");
  rootStatus.className = "kr-status";
  function updateRootUI() {
    ROOT_ORDER.forEach(function (L) {
      rootBtns[L].classList.toggle("selected", L === root);
    });
    rootStatus.textContent = root === writtenRoot
      ? "tonic sounds at " + soundingTonicName() + " (written pitch)"
      : "tonic sounds at " + soundingTonicName() + " — transposed " +
        (offsetCommas() > 0 ? "up " : "down ") +
        Math.abs(offsetCommas()) + " commas";
  }
  ROOT_ORDER.forEach(function (L) {
    const b = document.createElement("button");
    b.type = "button";
    b.textContent = L === writtenRoot ? L + "·" : L;
    b.title = L === writtenRoot ? "Written pitch"
      : "Transpose tonic " + (goesDown ? "down" : "up") + " to " + L;
    b.addEventListener("click", function () {
      root = L;
      try { localStorage.setItem("maqam-root-" + makamKey, L); } catch (e) {}
      updateRootUI();
    });
    rootBtns[L] = b;
    rootRow.appendChild(b);
  });
  rootRow.appendChild(rootStatus);
  box.parentNode.insertBefore(rootRow, box);
  updateRootUI();

  /* ---- on-screen keys: columns with optional piano twin on top ---- */
  function bindPress(el, on, off) {
    el.addEventListener("pointerdown", function (e) {
      e.preventDefault();
      el.setPointerCapture(e.pointerId);
      on();
    });
    ["pointerup", "pointercancel"].forEach(function (ev) {
      el.addEventListener(ev, off);
    });
  }

  const hasWestern = notes.some(function (n) { return n.western !== null; });
  notes.forEach(function (n, i) {
    const col = document.createElement("div");
    col.className = "kbd-col";
    if (n.western !== null) {
      const w = document.createElement("div");
      w.className = "kbd-key western";
      const name = TET_NAMES[((n.western % 12) + 12) % 12] +
                   (n.western >= 12 ? "′" : "");
      w.innerHTML = '<span class="cap">' + (TOP_CAPS[i] || "·") + "</span>" +
        '<span class="perde">piano ' + name + "</span>";
      bindPress(w, function () { westOn(i); }, function () { westOff(i); });
      westEls[i] = w;
      col.appendChild(w);
    }
    const k = document.createElement("div");
    k.className = "kbd-key" +
      (n.flag === "t" ? " tonic" : n.flag === "g" ? " guclu" :
       n.flag === "y" ? " yeden" : "");
    k.innerHTML = '<span class="cap">' + (KEY_CAPS[i] || "·") + "</span>" +
      '<span class="perde">' + n.perde + "</span>";
    bindPress(k, function () { noteOn(i); }, function () { noteOff(i); });
    col.appendChild(k);
    box.appendChild(col);
    keyEls.push(k);
  });
  if (hasWestern) box.classList.add("has-western");

  document.addEventListener("keydown", function (e) {
    if (e.repeat || e.metaKey || e.ctrlKey || e.altKey) return;
    let i = KEY_CODES.indexOf(e.code);
    if (i >= 0 && i < notes.length) {
      e.preventDefault();
      noteOn(i);
      return;
    }
    i = TOP_CODES.indexOf(e.code);
    if (i >= 0 && i < notes.length && notes[i].western !== null) {
      e.preventDefault();
      westOn(i);
    }
  });
  document.addEventListener("keyup", function (e) {
    let i = KEY_CODES.indexOf(e.code);
    if (i >= 0) { noteOff(i); return; }
    i = TOP_CODES.indexOf(e.code);
    if (i >= 0) westOff(i);
  });
  window.addEventListener("blur", function () {
    Array.from(active.keys()).forEach(function (id) {
      if (typeof id === "number") noteOff(id);
      else westOff(+id.slice(1));
    });
  });
})();
