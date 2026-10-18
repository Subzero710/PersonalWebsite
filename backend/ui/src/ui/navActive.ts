const normalizePath = (path: string): string => path.replace(/\/+$/, "") || "/";

export function setupActiveNav(): void {
  const links = Array.from(document.querySelectorAll<HTMLAnchorElement>(
    ".side-link[data-nav], .side-group-heading-link[data-nav], .side-link[data-project-slug], .side-link[href*='#']"
  ));
  const update = (): void => {
    const pathname = normalizePath(window.location.pathname);
    const currentHash = decodeURIComponent(window.location.hash);
    const hasMatchingAnchor = !!currentHash && links.some((link) => {
      const target = new URL(link.href, window.location.href);
      return normalizePath(target.pathname) === pathname &&
        !!target.hash && decodeURIComponent(target.hash) === currentHash;
    });
    for (const link of links) {
      const target = new URL(link.href, window.location.href);
      const targetPath = normalizePath(target.pathname);
      const samePath = targetPath === pathname;
      const isAnchor = Boolean(target.hash);
      const matchesAnchor = isAnchor && decodeURIComponent(target.hash) === currentHash;
      const active = isAnchor
        ? samePath && matchesAnchor
        : link.dataset.projectSlug
          ? samePath
          : link.dataset.nav === "projects"
            ? pathname === "/projects" || pathname.startsWith("/projects/")
            : samePath && !hasMatchingAnchor;
      link.classList.toggle("is-active", active);
      if (active) link.setAttribute("aria-current", isAnchor ? "location" : "page");
      else link.removeAttribute("aria-current");
    }
  };
  document.addEventListener("click", (event: MouseEvent) => {
    if (!(event.target instanceof Element)) return;
    if (event.target.closest("a[href*='#']")) requestAnimationFrame(update);
  });
  window.addEventListener("hashchange", update);
  window.addEventListener("popstate", update);
  update();
}
