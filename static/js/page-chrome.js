(function () {
  var ticking = false;

  function updateNavbarState() {
    document.documentElement.classList.toggle("noflower-scrolled", window.scrollY > 12);
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
    initToc();
  });
})();
