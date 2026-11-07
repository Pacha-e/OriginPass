// The holder's handover screen: count the code's two minutes down and fetch
// the next code when they run out. The ring empties as the seconds pass.
(function () {
  "use strict";
  var box = document.querySelector("[data-handover]");
  if (!box) return;
  var WINDOW = 120;
  var url = box.getAttribute("data-handover-url");
  var left = parseInt(box.getAttribute("data-handover-seconds"), 10) || WINDOW;
  var codeEl = box.querySelector("[data-handover-code]");
  var ring = box.querySelector("[data-handover-ring]");
  var secondsEl = box.querySelector("[data-handover-seconds-text]");

  function draw() {
    secondsEl.textContent = left;
    ring.style.strokeDashoffset = String(WINDOW - left);
  }

  function refresh() {
    fetch(url, { credentials: "same-origin", cache: "no-store" })
      .then(function (response) {
        if (!response.ok) throw new Error(response.status);
        return response.json();
      })
      .then(function (data) {
        codeEl.textContent = data.code.slice(0, 3) + " " + data.code.slice(3);
        left = data.seconds_left;
        draw();
      })
      .catch(function () {
        // Handed over or revoked: this screen has nothing left to show.
        window.location.reload();
      });
  }

  draw();
  window.setInterval(function () {
    left -= 1;
    if (left <= 0) {
      left = WINDOW;
      refresh();
    }
    draw();
  }, 1000);
})();
