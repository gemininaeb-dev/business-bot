// Плавный «отсчёт» чисел в карточках-виджетах
(function () {
  "use strict";

  const reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  // На повторных переходах (класс no-entrance) не пересчитываем — сразу итог
  const instant = document.documentElement.classList.contains("no-entrance");

  function animateCount(el) {
    const target = parseFloat(el.dataset.count || "0");
    const suffix = el.dataset.suffix || "";
    if (reduce || instant || target === 0) {
      el.textContent = Math.round(target).toLocaleString("ru-RU") + suffix;
      return;
    }
    const duration = 1100;
    const start = performance.now();

    function tick(now) {
      const p = Math.min((now - start) / duration, 1);
      // ease-out cubic
      const eased = 1 - Math.pow(1 - p, 3);
      const value = Math.round(target * eased);
      el.textContent = value.toLocaleString("ru-RU") + suffix;
      if (p < 1) requestAnimationFrame(tick);
    }
    requestAnimationFrame(tick);
  }

  // Запускаем, когда виджет появляется в зоне видимости
  const observer = new IntersectionObserver(
    (entries, obs) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          animateCount(entry.target);
          obs.unobserve(entry.target);
        }
      });
    },
    { threshold: 0.4 }
  );

  document.addEventListener("DOMContentLoaded", () => {
    const items = document.querySelectorAll("[data-count]");
    if (reduce || instant) {
      // мгновенно проставляем итоговые значения
      items.forEach((el) => animateCount(el));
    } else {
      items.forEach((el) => observer.observe(el));
    }
  });
})();
