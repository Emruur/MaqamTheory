/* Audio playback for play buttons and clickable note chips.
   Works from file:// — uses <audio> elements, no fetch. */

(function () {
  "use strict";

  let current = null; // { audio, el, cls }

  function stopCurrent() {
    if (!current) return;
    current.audio.pause();
    current.audio.currentTime = 0;
    current.el.classList.remove(current.cls);
    current = null;
  }

  function play(el, src, cls) {
    if (current && current.el === el) { stopCurrent(); return; }
    stopCurrent();
    if (window.MaqamVoice) src = window.MaqamVoice.path(src);
    const audio = new Audio(src);
    el.classList.add(cls);
    current = { audio, el, cls };
    audio.addEventListener("ended", function () {
      if (current && current.audio === audio) stopCurrent();
    });
    audio.play().catch(function () { stopCurrent(); });
  }

  document.addEventListener("click", function (e) {
    const btn = e.target.closest("button.play");
    if (btn && btn.dataset.audio) {
      play(btn, btn.dataset.audio, "playing");
      return;
    }
    const chip = e.target.closest(".note-chip");
    if (chip && chip.dataset.c) {
      const prefix = document.body.dataset.audioPath || "../audio/";
      play(chip, prefix + "note_" + chip.dataset.c + ".wav", "sounding");
    }
  });
})();
