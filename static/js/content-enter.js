(function () {
  var mathJaxWaitStartedAt = Date.now();

  function markReady() {
    document.querySelectorAll("#content > .content").forEach(function (content) {
      content.classList.add("noflower-content-ready");
    });
  }

  function waitForMathJax() {
    return new Promise(function (resolve) {
      var content = document.querySelector("#content > .content");
      if (!content || !/(\\\(|\\\[|\$\$)/.test(content.textContent || "")) {
        resolve();
        return;
      }

      function waitForStartup() {
        if (window.MathJax && window.MathJax.startup && window.MathJax.startup.promise) {
          window.MathJax.startup.promise
            .then(function () {
              if (content && window.MathJax.typesetPromise) {
                return window.MathJax.typesetPromise([content]);
              }
            })
            .then(resolve)
            .catch(resolve);
          return;
        }

        if (Date.now() - mathJaxWaitStartedAt > 8000) {
          resolve();
          return;
        }

        window.setTimeout(waitForStartup, 50);
      }

      waitForStartup();
    });
  }

  document.addEventListener("DOMContentLoaded", function () {
    waitForMathJax().then(function () {
      window.requestAnimationFrame(markReady);
    });
  });
})();
