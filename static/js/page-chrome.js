(function () {
  var ticking = false;

  function updateNavbarState() {
    document.documentElement.classList.toggle("noflower-scrolled", window.scrollY > 12);
  }

  function parseColor(value) {
    if (!value) return null;
    var color = String(value).trim();
    var hex = color.match(/^#?([0-9a-f]{3}|[0-9a-f]{6})$/i);
    if (hex) {
      var raw = hex[1];
      if (raw.length === 3) {
        raw = raw.replace(/(.)/g, "$1$1");
      }
      return [
        parseInt(raw.slice(0, 2), 16),
        parseInt(raw.slice(2, 4), 16),
        parseInt(raw.slice(4, 6), 16),
      ];
    }

    var rgb = color.match(/rgba?\(\s*([\d.]+)[,\s]+([\d.]+)[,\s]+([\d.]+)/i);
    if (rgb) {
      return [Number(rgb[1]), Number(rgb[2]), Number(rgb[3])].map(function (part) {
        return Math.max(0, Math.min(255, Math.round(part)));
      });
    }

    var spaced = color.match(/^(\d{1,3})\s+(\d{1,3})\s+(\d{1,3})$/);
    if (spaced) {
      return [Number(spaced[1]), Number(spaced[2]), Number(spaced[3])].map(function (part) {
        return Math.max(0, Math.min(255, Math.round(part)));
      });
    }

    return null;
  }

  function setAccentColor(rgb) {
    if (!rgb) return;
    document.documentElement.style.setProperty("--noflower-accent-rgb", rgb.join(" "));
    document.documentElement.dataset.noflowerAccentSource = "cover";
  }

  function extractImageAccent(img) {
    var canvas = document.createElement("canvas");
    var size = 48;
    canvas.width = size;
    canvas.height = size;
    var ctx = canvas.getContext("2d", { willReadFrequently: true });
    if (!ctx) return null;

    ctx.drawImage(img, 0, 0, size, size);
    var data = ctx.getImageData(0, 0, size, size).data;
    var r = 0;
    var g = 0;
    var b = 0;
    var total = 0;

    for (var i = 0; i < data.length; i += 16) {
      var alpha = data[i + 3];
      if (alpha < 160) continue;

      var red = data[i];
      var green = data[i + 1];
      var blue = data[i + 2];
      var max = Math.max(red, green, blue);
      var min = Math.min(red, green, blue);
      var lightness = (max + min) / 2;
      var saturation = max === min ? 0 : (max - min) / (255 - Math.abs(2 * lightness - 255));

      if (lightness < 28 || lightness > 235 || saturation < 0.12) continue;

      var weight = 1 + saturation * 3 + Math.abs(lightness - 128) / 255;
      r += red * weight;
      g += green * weight;
      b += blue * weight;
      total += weight;
    }

    if (!total) return null;

    return [
      Math.round(r / total),
      Math.round(g / total),
      Math.round(b / total),
    ];
  }

  function initCoverAccent() {
    var cover = document.querySelector(".noflower-page-cover");
    if (!cover) return;

    var manual = parseColor(cover.getAttribute("data-cover-accent"));
    if (manual) {
      setAccentColor(manual);
      return;
    }

    var img = cover.querySelector("img");
    if (!img) return;

    function applyExtractedAccent() {
      try {
        setAccentColor(extractImageAccent(img));
      } catch (error) {
        // Cross-origin images can taint canvas; in that case keep the section color.
      }
    }

    if (img.complete && img.naturalWidth > 0) {
      applyExtractedAccent();
    } else {
      img.addEventListener("load", applyExtractedAccent, { once: true });
    }
  }

  function initCoverBackdropScroll() {
    var backdrop = document.querySelector(".noflower-page-cover-backdrop");
    var tickingCover = false;

    function updateCoverBackdrop() {
      tickingCover = false;
      var y = Math.min(window.scrollY * 0.28, 220);
      document.documentElement.style.setProperty("--noflower-page-bg-y", y.toFixed(1) + "px");
      if (backdrop) {
        backdrop.style.setProperty("--noflower-cover-backdrop-y", y.toFixed(1) + "px");
      }
    }

    function requestCoverUpdate() {
      if (!tickingCover) {
        tickingCover = true;
        window.requestAnimationFrame(updateCoverBackdrop);
      }
    }

    window.addEventListener("scroll", requestCoverUpdate, { passive: true });
    window.addEventListener("resize", requestCoverUpdate);
    updateCoverBackdrop();
  }

  function initToc() {
    var toc = document.querySelector(".hextra-toc");
    if (!toc) return;

    var links = Array.prototype.slice.call(toc.querySelectorAll(".noflower-toc-link"));
    if (!links.length) return;

    var headingWrap = toc.querySelector(".noflower-toc-heading-wrap");
    var entries = links
      .map(function (link, index) {
        var id = link.getAttribute("data-heading-id") || (link.hash || "").slice(1);
        return {
          index: index,
          link: link,
          heading: id ? document.getElementById(id) : null,
          level: Number(link.getAttribute("data-toc-level") || 0),
        };
      })
      .filter(function (entry) {
        return entry.heading;
      });

    entries.forEach(function (entry, index) {
      entry.index = index;
    });

    if (!entries.length) return;

    function scrollToHeading(target) {
      var offset = 104;
      var top = target.getBoundingClientRect().top + window.scrollY - offset;
      window.scrollTo({
        top: Math.max(0, top),
        behavior: "smooth",
      });
    }

    links.forEach(function (link) {
      link.addEventListener("click", function (event) {
        var id = link.getAttribute("data-heading-id") || (link.hash || "").slice(1);
        var target = id ? document.getElementById(id) : null;
        if (!target) return;

        event.preventDefault();
        window.history.pushState(null, "", "#" + id);
        scrollToHeading(target);
      });
    });

    function getVisibleRange(active) {
      var viewportTop = 88;
      var viewportBottom = window.innerHeight - 72;
      var visible = entries.filter(function (entry) {
        var rect = entry.heading.getBoundingClientRect();
        return rect.top <= viewportBottom && rect.bottom >= viewportTop;
      });

      if (!visible.length && active) {
        visible = [active];
      }

      if (!visible.length) return null;

      return {
        start: visible[0],
        end: visible[visible.length - 1],
      };
    }

    function setActive(active) {
      var visibleRange = getVisibleRange(active);

      entries.forEach(function (entry) {
        entry.link.classList.toggle("is-active", entry === active);
        entry.link.classList.toggle(
          "is-in-active-branch",
          Boolean(visibleRange && entry.index >= visibleRange.start.index && entry.index <= visibleRange.end.index)
        );
      });

      if (!visibleRange || !headingWrap) return;

      var wrapRect = headingWrap.getBoundingClientRect();
      var startBox = visibleRange.start.link.closest("li") || visibleRange.start.link;
      var endBox = visibleRange.end.link.closest("li") || visibleRange.end.link;
      var startRect = startBox.getBoundingClientRect();
      var endRect = endBox.getBoundingClientRect();
      var top = Math.max(0, startRect.top - wrapRect.top);
      var height = Math.max(24, endRect.bottom - startRect.top);
      headingWrap.style.setProperty("--noflower-toc-active-top", top.toFixed(1) + "px");
      headingWrap.style.setProperty("--noflower-toc-active-height", height.toFixed(1) + "px");
      headingWrap.style.setProperty("--noflower-toc-progress-height", (top + height).toFixed(1) + "px");
    }

    function updateTocState() {
      ticking = false;
      updateNavbarState();

      var marker = 120;
      var active = entries[0];
      for (var i = 0; i < entries.length; i += 1) {
        if (entries[i].heading.getBoundingClientRect().top <= marker) {
          active = entries[i];
        } else {
          break;
        }
      }
      setActive(active);

    }

    function requestUpdate() {
      if (!ticking) {
        ticking = true;
        window.requestAnimationFrame(updateTocState);
      }
    }

    window.addEventListener("scroll", requestUpdate, { passive: true });
    window.addEventListener("resize", requestUpdate);
    updateTocState();
  }

  document.addEventListener("DOMContentLoaded", function () {
    updateNavbarState();
    initCoverAccent();
    initCoverBackdropScroll();
    initToc();
  });
})();
