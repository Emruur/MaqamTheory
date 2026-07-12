/* Site-wide voice (timbre) selector. Injects a picker into the header and
   maps audio paths: audio/x.wav -> audio/<voice>/x.wav for non-default
   voices. All players (buttons, note chips, quiz, keyboard synth) honor it. */

window.MaqamVoice = (function () {
  "use strict";

  const VOICES = [
    ["warm", "Warm"],
    ["ney", "Ney"],
    ["pluck", "Oud"],
  ];

  let current = "warm";
  try {
    const saved = localStorage.getItem("maqam-voice");
    if (VOICES.some(function (v) { return v[0] === saved; })) current = saved;
  } catch (e) { /* private browsing */ }

  const listeners = [];

  function get() { return current; }

  function set(v) {
    current = v;
    try { localStorage.setItem("maqam-voice", v); } catch (e) {}
    buttons.forEach(function (b) {
      b.classList.toggle("selected", b.dataset.voice === v);
    });
    listeners.forEach(function (fn) { fn(v); });
  }

  function onChange(fn) { listeners.push(fn); }

  /* Map any audio URL to the current voice's copy. */
  function path(src) {
    if (current === "warm") return src;
    return src.replace(/(^|\/)audio\//, "$1audio/" + current + "/");
  }

  // Build the picker in the site header.
  const buttons = [];
  const header = document.querySelector("header.site .crumbs");
  if (header) {
    const wrap = document.createElement("span");
    wrap.className = "voice-picker";
    wrap.setAttribute("role", "group");
    wrap.setAttribute("aria-label", "Sound");
    const label = document.createElement("span");
    label.className = "vp-label";
    label.textContent = "♪";
    wrap.appendChild(label);
    VOICES.forEach(function (v) {
      const b = document.createElement("button");
      b.type = "button";
      b.dataset.voice = v[0];
      b.textContent = v[1];
      if (v[0] === current) b.classList.add("selected");
      b.addEventListener("click", function () { set(v[0]); });
      buttons.push(b);
      wrap.appendChild(b);
    });
    header.appendChild(wrap);
  }

  return { get: get, set: set, path: path, onChange: onChange };
})();
