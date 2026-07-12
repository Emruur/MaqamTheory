/* Computer-keyboard instrument: play the makam's perdeler live.
   Physical home-row keys (layout-independent event.code) map to scale
   degrees; Web Audio synthesizes the exact AEU comma pitches with the
   same warm harmonic recipe as the WAV files. Hold a key to sustain. */

(function () {
  "use strict";

  const KEY_CODES = ["KeyA", "KeyS", "KeyD", "KeyF", "KeyG", "KeyH",
                     "KeyJ", "KeyK", "KeyL", "Semicolon", "Quote"];
  const KEY_CAPS = ["A", "S", "D", "F", "G", "H", "J", "K", "L", ";", "'"];
  const HARMONICS = [0, 1, 0.42, 0.28, 0.12, 0.08, 0.045];

  const box = document.querySelector(".kbd-instrument");
  if (!box) return;

  const notes = box.dataset.notes.split(",").map(function (s) {
    const parts = s.split("|");
    return { commas: +parts[0], perde: parts[1], flag: parts[2] || "" };
  });

  let ctx = null, wave = null, master = null;
  const active = new Map();   // index -> {osc, gain}
  const keyEls = [];

  function ensureAudio() {
    if (!ctx) {
      ctx = new (window.AudioContext || window.webkitAudioContext)();
      wave = ctx.createPeriodicWave(
        new Float32Array(HARMONICS.length),
        Float32Array.from(HARMONICS));
      master = ctx.createGain();
      master.gain.value = 0.9;
      const lp = ctx.createBiquadFilter();
      lp.type = "lowpass";
      lp.frequency.value = 5200;
      master.connect(lp).connect(ctx.destination);
    }
    if (ctx.state === "suspended") ctx.resume();
  }

  function freqOf(commas) {
    return 440 * Math.pow(2, (commas - 40) / 53);
  }

  function noteOn(i) {
    if (i < 0 || i >= notes.length || active.has(i)) return;
    ensureAudio();
    const t = ctx.currentTime;
    const osc = ctx.createOscillator();
    osc.setPeriodicWave(wave);
    osc.frequency.value = freqOf(notes[i].commas);
    const gain = ctx.createGain();
    gain.gain.setValueAtTime(0.0001, t);
    gain.gain.exponentialRampToValueAtTime(0.30, t + 0.025);
    gain.gain.exponentialRampToValueAtTime(0.16, t + 0.7);
    osc.connect(gain).connect(master);
    osc.start(t);
    active.set(i, { osc: osc, gain: gain });
    keyEls[i].classList.add("active");
  }

  function noteOff(i) {
    const v = active.get(i);
    if (!v) return;
    active.delete(i);
    const t = ctx.currentTime;
    v.gain.gain.cancelScheduledValues(t);
    v.gain.gain.setValueAtTime(Math.max(v.gain.gain.value, 0.0001), t);
    v.gain.gain.exponentialRampToValueAtTime(0.0001, t + 0.35);
    v.osc.stop(t + 0.4);
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
