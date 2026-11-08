document.querySelectorAll("[data-photo-pick]").forEach(function (pick) {
  var input = pick.querySelector("input[type=file]");
  var name = pick.querySelector("[data-photo-name]");
  input.addEventListener("change", function () {
    name.textContent = input.files.length ? input.files[0].name : name.dataset.empty;
  });
});
