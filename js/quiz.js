/* "Guess the makam" ear-training quiz (chapter 10). */

(function () {
  "use strict";

  const MAKAMS = [
    { key: "rast", label: "Rast" },
    { key: "nihavend", label: "Nihavend" },
    { key: "ussak", label: "Uşşak" },
    { key: "huseyni", label: "Hüseyni" },
    { key: "hicaz", label: "Hicaz" },
  ];

  const box = document.getElementById("quiz");
  if (!box) return;

  const playBtn = box.querySelector(".quiz-play");
  const choicesEl = box.querySelector(".quiz-choices");
  const statusEl = box.querySelector(".quiz-status");
  const scoreEl = box.querySelector(".quiz-score");

  let answer = null;
  let audio = null;
  let score = 0, asked = 0, answered = true;

  MAKAMS.forEach(function (m) {
    const b = document.createElement("button");
    b.textContent = m.label;
    b.dataset.key = m.key;
    b.disabled = true;
    b.addEventListener("click", function () { guess(b, m.key); });
    choicesEl.appendChild(b);
  });
  const buttons = Array.prototype.slice.call(choicesEl.children);

  function newRound() {
    answer = MAKAMS[Math.floor(Math.random() * MAKAMS.length)];
    answered = false;
    buttons.forEach(function (b) {
      b.disabled = false;
      b.classList.remove("correct", "wrong");
    });
    statusEl.textContent = "Listen, then pick the makam.";
    playScale();
  }

  function playScale() {
    if (!answer) return;
    if (audio) { audio.pause(); audio.currentTime = 0; }
    audio = new Audio("../audio/" + answer.key + "_quiz.wav");
    audio.play();
  }

  function guess(btn, key) {
    if (answered) return;
    answered = true;
    asked += 1;
    buttons.forEach(function (b) { b.disabled = true; });
    if (key === answer.key) {
      score += 1;
      btn.classList.add("correct");
      statusEl.textContent = "Correct — that was " + answer.label + ".";
    } else {
      btn.classList.add("wrong");
      buttons.forEach(function (b) {
        if (b.dataset.key === answer.key) b.classList.add("correct");
      });
      statusEl.textContent = "That was " + answer.label + ". Listen again and compare.";
    }
    scoreEl.textContent = score + " / " + asked;
    playBtn.textContent = "Next scale";
  }

  playBtn.addEventListener("click", function () {
    if (answered) {
      playBtn.textContent = "Replay scale";
      newRound();
    } else {
      playScale();
    }
  });
})();
