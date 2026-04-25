(function () {
  var hideTimer = null;
  var activeCard = null;

  function clamp(value, min, max) {
    return Math.min(Math.max(value, min), max);
  }

  function positionCard(author) {
    var card = author._noflowerHovercard;
    if (!card) return;

    card.classList.remove("noflower-author-card--below");

    var rect = author.getBoundingClientRect();
    var margin = 12;
    var gap = 10;
    var cardWidth = Math.min(360, window.innerWidth - margin * 2);
    var cardHeight = card.offsetHeight || 230;
    var left = clamp(rect.left, margin, window.innerWidth - cardWidth - margin);
    var top = rect.top - cardHeight - gap;
    var below = top < margin;

    if (below) {
      top = rect.bottom + gap;
      card.classList.add("noflower-author-card--below");
    }

    top = clamp(top, margin, window.innerHeight - cardHeight - margin);

    var arrowLeft = clamp(rect.left + rect.width / 2 - left - 6, 14, cardWidth - 26);
    card.style.setProperty("--noflower-card-left", left + "px");
    card.style.setProperty("--noflower-card-top", top + "px");
    card.style.setProperty("--noflower-card-width", cardWidth + "px");
    card.style.setProperty("--noflower-card-arrow-left", arrowLeft + "px");
  }

  function showCard(author) {
    window.clearTimeout(hideTimer);
    var card = author._noflowerHovercard;
    if (!card) return;
    if (activeCard && activeCard !== card) {
      activeCard.classList.remove("noflower-author-card--visible");
    }
    activeCard = card;
    positionCard(author);
    card.classList.add("noflower-author-card--visible");
  }

  function hideCard(author) {
    var card = author._noflowerHovercard;
    hideTimer = window.setTimeout(function () {
      if (card) {
        card.classList.remove("noflower-author-card--visible");
      }
      if (activeCard === card) {
        activeCard = null;
      }
    }, 110);
  }

  document.addEventListener("DOMContentLoaded", function () {
    document.querySelectorAll(".noflower-author").forEach(function (author) {
      var card = author.querySelector(".noflower-author-card");
      if (!card) return;

      author._noflowerHovercard = card;
      document.body.appendChild(card);

      author.addEventListener("mouseenter", function () {
        showCard(author);
      });
      author.addEventListener("focus", function () {
        showCard(author);
      });
      author.addEventListener("mouseleave", function () {
        hideCard(author);
      });
      author.addEventListener("blur", function () {
        hideCard(author);
      });

      card.addEventListener("mouseenter", function () {
        window.clearTimeout(hideTimer);
      });
      card.addEventListener("mouseleave", function () {
        hideCard(author);
      });
    });
  });

  window.addEventListener("resize", function () {
    document.querySelectorAll(".noflower-author:hover, .noflower-author:focus").forEach(positionCard);
  });
})();
