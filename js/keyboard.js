/* Computer-keyboard instrument: play the makam's perdeler live.
   Physical home-row keys (layout-independent event.code) map to scale
   degrees; Web Audio synthesizes the exact AEU comma pitches. Hold a key
   to sustain. Three selectable voices: warm synth, breathy ney, plucked oud. */

(function () {
  "use strict";

  const KEY_CODES = ["KeyA", "KeyS", "KeyD", "KeyF", "KeyG", "KeyH",
                     "KeyJ", "KeyK", "KeyL", "Semicolon", "Quote"];
  const KEY_CAPS = ["A", "S", "D", "F", "G", "H", "J", "K", "L", ";", "'"];

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

  const notes = box.dataset.notes.split(",").map(function (s) {
    const parts = s.split("|");
    return { commas: +parts[0], perde: parts[1], flag: parts[2] || "" };
  });

  let ctx = null, master = null, noiseBuf = null;
  const waves = {};           // voice key -> PeriodicWave
  const active = new Map();   // note index -> handle {off(t)}
  const keyEls = [];

  // Follow the site-wide voice picker (js/voice.js). "oud" maps to pluck.
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
    return 440 * Math.pow(2, (commas - 40) / 53);
  }

  /* Each starter returns a handle with off(t) that releases and cleans up. */

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
    // Delayed vibrato.
    const lfo = ctx.createOscillator();
    lfo.frequency.value = 4.8;
    const depth = ctx.createGain();
    depth.gain.setValueAtTime(0, t);
    depth.gain.linearRampToValueAtTime(f * 0.004, t + 0.6);
    lfo.connect(depth).connect(osc.frequency);
    // Breath: band-passed noise around the second partial.
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
    // Slow, swelling body.
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
    // Darkening filter: bright attack, mellow tail, like a plucked string.
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

  function noteOn(i) {
    if (i < 0 || i >= notes.length || active.has(i)) return;
    ensureAudio();
    active.set(i, STARTERS[voice](freqOf(notes[i].commas), ctx.currentTime));
    keyEls[i].classList.add("active");
  }

  function noteOff(i) {
    const h = active.get(i);
    if (!h) return;
    active.delete(i);
    h.off(ctx.currentTime);
    keyEls[i].classList.remove("active");
  }

  // Build the on-screen keys.
  notes.forEach(function (n, i) {
    const k = document.createElement("div");
    k.className = "kbd-key" +
      (n.flag === "t" ? " tonic" : n.flag === "g" ? " guclu" :
       n.flag === "y" ? " yeden" : "");
    k.innerHTML = '<span class="cap">' + (KEY_CAPS[i] || "·") + "</span>" +
      '<span class="perde">' + n.perde + "</span>";
    k.addEventListener("pointerdown", function (e) {
      e.preventDefault();
      k.setPointerCapture(e.pointerId);
      noteOn(i);
    });
    ["pointerup", "pointercancel"].forEach(function (ev) {
      k.addEventListener(ev, function () { noteOff(i); });
    });
    box.appendChild(k);
    keyEls.push(k);
  });

  document.addEventListener("keydown", function (e) {
    if (e.repeat || e.metaKey || e.ctrlKey || e.altKey) return;
    const i = KEY_CODES.indexOf(e.code);
    if (i >= 0 && i < notes.length) {
      e.preventDefault();
      noteOn(i);
    }
  });
  document.addEventListener("keyup", function (e) {
    const i = KEY_CODES.indexOf(e.code);
    if (i >= 0) noteOff(i);
  });
  window.addEventListener("blur", function () {
    Array.from(active.keys()).forEach(noteOff);
  });
})();
