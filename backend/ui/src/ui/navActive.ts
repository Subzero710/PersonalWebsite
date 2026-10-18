const normalizePath = (path: string): string => path.replace(/\/+$/, "") || "/";

export function setupActiveNav(): void {
  const links = Array.from(document.querySelectorAll<HTMLAnchorElement>(
    ".side-link[data-nav], .side-group-heading-link[data-nav], .side-link[data-project-slug], .side-link[href*='#']"
  ));
  const update = (): void => {
    const pathname = normalizePath(window.location.pathname);
    const currentHash = decodeURIComponent(window.location.hash);
    // Prefer an explicit matching anchor when one is present in the sidebar;
    // otherwise keep the current page highlighted while its TOC changes hash.
    const hasMatchingAnchor = !!currentHash && links.some((link) => {
      const target = new URL(link.href, window.location.href);
      return normalizePath(target.pathname) === pathname &&
        !!target.hash && decodeURIComponent(target.hash) === currentHash;
    });
    for (const link of links) {
      const target = new URL(link.href, window.location.href);
      const targetPath = normalizePath(target.pathname);
      const isProject = !!link.dataset.projectSlug;
      const projectIndex = link.dataset.nav === "projects";
      const matchesPath = targetPath === pathname;
      const matchesHash = !!target.hash && decodeURIComponent(target.hash) === currentHash;
      const active = isProject
        ? matchesPath
        : projectIndex
          ? pathname === "/projects" || pathname.startsWith("/projects/")
          : matchesPath && (target.hash ? matchesHash : !hasMatchingAnchor);
      link.classList.toggle("is-active", active);
      if (active) link.setAttribute("aria-current", target.hash ? "location" : "page");
      else link.removeAttribute("aria-current");
    }
  };
  window.addEventListener("hashchange", update);
  window.addEventListener("popstate", update);
  update();
}
