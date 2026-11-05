// Reads the QR of a passport with the camera and fills the passport code field.
// The QR encodes the public address .../v/<code>/; the field takes only <code>.
// Needs a secure page (HTTPS): without navigator.mediaDevices it does nothing and
// the typed field stays the way to claim.
(function () {
  "use strict";

  var panel = document.querySelector("[data-scanner]");
  var startButton = document.querySelector("[data-scanner-start]");
  if (!panel || !startButton) {
    return;
  }
  if (
    !navigator.mediaDevices ||
    !navigator.mediaDevices.getUserMedia ||
    typeof jsQR !== "function"
  ) {
    return;
  }

  var field = document.getElementById(panel.getAttribute("data-scanner-field"));
  var video = panel.querySelector("video");
  var canvas = panel.querySelector("canvas");
  var message = panel.querySelector("[data-scanner-status]");
  var stopButton = panel.querySelector("[data-scanner-stop]");
  var context = canvas.getContext("2d", { willReadFrequently: true });
  var stream = null;
  var frame = null;

  function say(key) {
    message.textContent = panel.getAttribute("data-msg-" + key) || "";
  }

  function codeFrom(text) {
    var match = /\/v\/([A-Za-z0-9_-]+)\/?(?:[?#].*)?$/.exec(text);
    return match ? match[1] : null;
  }

  function stop() {
    if (frame) {
      cancelAnimationFrame(frame);
      frame = null;
    }
    if (stream) {
      stream.getTracks().forEach(function (track) {
        track.stop();
      });
      stream = null;
    }
    panel.hidden = true;
    startButton.hidden = false;
  }

  function scan() {
    if (video.readyState < video.HAVE_ENOUGH_DATA) {
      frame = requestAnimationFrame(scan);
      return;
    }
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    context.drawImage(video, 0, 0, canvas.width, canvas.height);
    var pixels = context.getImageData(0, 0, canvas.width, canvas.height);
    var result = jsQR(pixels.data, pixels.width, pixels.height);
    var code = result ? codeFrom(result.data) : null;
    if (code) {
      field.value = code;
      say("found");
      stop();
      field.focus();
      return;
    }
    frame = requestAnimationFrame(scan);
  }

  function start() {
    navigator.mediaDevices
      .getUserMedia({ video: { facingMode: "environment" }, audio: false })
      .then(function (camera) {
        stream = camera;
        video.srcObject = camera;
        panel.hidden = false;
        startButton.hidden = true;
        say("aim");
        return video.play();
      })
      .then(function () {
        scan();
      })
      .catch(function () {
        stop();
        say("denied");
      });
  }

  startButton.hidden = false;
  startButton.addEventListener("click", start);
  stopButton.addEventListener("click", stop);
})();
