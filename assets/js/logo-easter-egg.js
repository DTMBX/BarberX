// Copyright © 2024–2026 Faith Frontier Ecclesiastical Trust. All rights reserved.
// PROPRIETARY — See LICENSE.

(function () {
  const logo = document.querySelector(".js-site-logo");
  if (!logo) return;

  logo.addEventListener("click", (e) => {
    const p = window.location.pathname;
    const isHome = p === "/" || p === "/index.html";

    if (isHome) {
      e.preventDefault();
      window.location.assign("/essays/logo/");
    }
  });
})();
