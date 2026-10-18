export function setupActiveNav(): void {
  const path = window.location.pathname;
  document.querySelectorAll<HTMLAnchorElement>(".side-link[data-nav],.side-group-heading-link[data-nav]").forEach((link) => {
    const active = link.dataset.nav === "home" ? path === "/" : (path === "/projects/" || path.startsWith("/projects/"));
    link.classList.toggle("is-active", active);
    if (active) link.setAttribute("aria-current", "page");
    else link.removeAttribute("aria-current");
  });
  document.querySelectorAll<HTMLAnchorElement>(".side-link[data-project-slug]").forEach((link) => {
    const active = new URL(link.href, location.origin).pathname === path;
    link.classList.toggle("is-active", active);
    if (active) link.setAttribute("aria-current", "page");
    else link.removeAttribute("aria-current");
  });
}
