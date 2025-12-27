export function setupActiveNav() {
  const path = location.pathname;
  document.querySelectorAll<HTMLAnchorElement>(".navlinks a").forEach((a) => {
    if (a.getAttribute("href") === path) a.classList.add("is-active");
  });
}