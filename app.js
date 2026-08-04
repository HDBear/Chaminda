/* Catalogue filter — progressive enhancement; page works without JS too. */
(function () {
  "use strict";
  var q = document.getElementById("q");
  var chips = Array.prototype.slice.call(document.querySelectorAll(".chip"));
  var cards = Array.prototype.slice.call(document.querySelectorAll(".card"));
  var sections = Array.prototype.slice.call(document.querySelectorAll(".group"));
  var noresults = document.getElementById("noresults");
  var activeGroup = "all";

  function apply() {
    var term = q.value.trim().toLowerCase();
    var visible = 0;
    cards.forEach(function (c) {
      var ok = (activeGroup === "all" || c.dataset.group === activeGroup) &&
               (term === "" || c.dataset.search.indexOf(term) !== -1);
      c.hidden = !ok;
      if (ok) visible++;
    });
    sections.forEach(function (s) {
      var any = Array.prototype.some.call(
        s.querySelectorAll(".card"), function (c) { return !c.hidden; });
      s.hidden = (activeGroup !== "all" && s.dataset.group !== activeGroup) || !any;
    });
    noresults.hidden = visible > 0;
  }

  chips.forEach(function (chip) {
    chip.addEventListener("click", function () {
      activeGroup = chip.dataset.group;
      chips.forEach(function (c) {
        c.setAttribute("aria-pressed", c === chip ? "true" : "false");
      });
      apply();
      if (activeGroup !== "all" && q.value.trim() === "") {
        var target = document.getElementById(activeGroup);
        if (target) target.scrollIntoView({ behavior: "smooth", block: "start" });
      }
    });
  });

  q.addEventListener("input", apply);

  document.getElementById("clearq").addEventListener("click", function () {
    q.value = "";
    activeGroup = "all";
    chips.forEach(function (c) {
      c.setAttribute("aria-pressed", c.dataset.group === "all" ? "true" : "false");
    });
    apply();
    q.focus();
  });

  // back-to-top
  var totop = document.getElementById("totop");
  window.addEventListener("scroll", function () {
    totop.hidden = window.scrollY < 600;
  }, { passive: true });
  totop.addEventListener("click", function () {
    window.scrollTo({ top: 0, behavior: "smooth" });
  });
})();
