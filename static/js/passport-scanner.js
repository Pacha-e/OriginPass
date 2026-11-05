// Reads the QR of a passport and fills the passport code field. Two ways:
//  - a photo the user uploads (works on any page, HTTP included: the phone camera
//    opens from the file input);
//  - the live camera (needs a secure page, HTTPS, because of navigator.mediaDevices).
// The QR encodes the public address .../v/<code>/; the field takes only <code>.
(function () {
  "use strict";

  if (typeof jsQR !== "function") {
    return;
  }

  var canvas = document.createElement("canvas");
  var context = canvas.getContext("2d", { willReadFrequently: true });

  function codeFrom(text) {
    var match = /\/v\/([A-Za-z0-9_-]+)\/?(?:[?#].*)?$/.exec(text);
    return match ? match[1] : null;
  }

  // Draws the source at the given size and returns the passport code in it, or null.
  function decode(source, width, height) {
    canvas.width = width;
    canvas.height = height;
    context.drawImage(source, 0, 0, width, height);
    var pixels = context.getImageData(0, 0, width, height);
    var result = jsQR(pixels.data, pixels.width, pixels.height);
    return result ? codeFrom(result.data) : null;
  }

  function uploadPhotos(block) {
    var field = document.getElementById(
      block.getAttribute("data-scanner-field"),
    );
    var input = block.querySelector("[data-scanner-photo-input]");
    var status = block.querySelector("[data-scanner-photo-status]");
    block.hidden = false;

    input.addEventListener("change", function () {
      var file = input.files && input.files[0];
      if (!file) {
        return;
      }
      var url = URL.createObjectURL(file);
      var image = new Image();

      function failed() {
        status.textContent = block.getAttribute("data-msg-none") || "";
      }

      image.onload = function () {
        URL.revokeObjectURL(url);
        // Phone photos are large; a 1600 px side is plenty to read a label.
        var scale = Math.min(
          1,
          1600 / Math.max(image.naturalWidth, image.naturalHeight),
        );
        var code = decode(
          image,
          Math.round(image.naturalWidth * scale),
          Math.round(image.naturalHeight * scale),
        );
        if (!code) {
          failed();
          return;
        }
        field.value = code;
        status.textContent = block.getAttribute("data-msg-found") || "";
        field.focus();
      };
      image.onerror = function () {
        URL.revokeObjectURL(url);
        failed();
      };
      image.src = url;
    });
  }

  function useCamera(panel, startButton) {
    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
      return;
    }

    var field = document.getElementById(
      panel.getAttribute("data-scanner-field"),
    );
    var video = panel.querySelector("video");
    var message = panel.querySelector("[data-scanner-status]");
    var stopButton = panel.querySelector("[data-scanner-stop]");
    var stream = null;
    var frame = null;

    function say(key) {
      message.textContent = panel.getAttribute("data-msg-" + key) || "";
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
      var code = decode(video, video.videoWidth, video.videoHeight);
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
  }

  var photos = document.querySelector("[data-scanner-photo]");
  if (photos) {
    uploadPhotos(photos);
  }

  var panel = document.querySelector("[data-scanner]");
  var startButton = document.querySelector("[data-scanner-start]");
  if (panel && startButton) {
    useCamera(panel, startButton);
  }
})();
