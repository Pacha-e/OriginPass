document.querySelectorAll("[data-stepper]").forEach(function (stepper) {
  var input = stepper.querySelector("input");
  var min = Number(input.min);
  var max = Number(input.max);
  stepper.querySelectorAll("[data-step]").forEach(function (button) {
    button.addEventListener("click", function () {
      var next = (parseInt(input.value, 10) || min) + Number(button.dataset.step);
      input.value = Math.min(Math.max(next, min), max);
    });
  });
});
