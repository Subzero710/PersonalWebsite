
export function setupActiveNav(): void {
  const path = window.location.pathname;
  const active = path === "/" ? "home" : path.startsWith("/projects/") ? "projects" : "";
  if (!active) return;
  document.querySelectorAll<HTMLAnchorElement>(".side-link[data-nav]").forEach((link) => {
    if (link.dataset.nav === active) {
      link.classList.add("is-active");
      link.setAttribute("aria-current", "page");
    } else {
      link.removeAttribute("aria-current");
    }
  });
}
