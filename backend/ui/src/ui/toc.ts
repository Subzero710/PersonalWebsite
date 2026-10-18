
export function setupTableOfContents(): void {
  const nav = document.querySelector<HTMLElement>("#pageToc");
  const container = document.querySelector<HTMLElement>("#tocLinks");
  const content = document.querySelector<HTMLElement>("#main-content");
  if (!nav || !container || !content) return;
  const sections: HTMLElement[] = Array.from(content.querySelectorAll<HTMLElement>("[data-toc-section]"));
  const headings = Array.from(content.querySelectorAll<HTMLElement>("[data-toc-content] h1, [data-toc-content] h2, [data-toc-content] h3"));
  const usedIds = new Set(Array.from(document.querySelectorAll<HTMLElement>("[id]"), el => el.id));

  headings.forEach((heading, index) => {
    if (heading.tagName === "H1") {
      const replacement = document.createElement("h2");
      while (heading.firstChild) replacement.appendChild(heading.firstChild);
      for (const attr of Array.from(heading.attributes)) replacement.setAttribute(attr.name, attr.value);
      heading.replaceWith(replacement);
      headings[index] = replacement;
    }
  });
  const entries = [...sections, ...headings].sort((a, b) => {
    if (a === b) return 0;
    return a.compareDocumentPosition(b) & Node.DOCUMENT_POSITION_FOLLOWING ? -1 : 1;
  });
  const targets: Array<{ target: HTMLElement; link: HTMLAnchorElement }> = [];
  entries.forEach((target, index) => {
    if (!target.id) {
      const base = (target.textContent || "section").toLocaleLowerCase().normalize("NFKD").replace(/[\u0300-\u036f]/g, "").replace(/[^a-z0-9]+/g, "-").replace(/^-|-$/g, "").slice(0, 55) || `section-${index + 1}`;
      let slug = base, next = 2;
      while (usedIds.has(slug)) slug = `${base}-${next++}`;
      target.id = slug;
      usedIds.add(slug);
    }
    const label = target.dataset.tocTitle || target.textContent?.trim() || "Section";
    const link = document.createElement("a");
    link.href = `#${encodeURIComponent(target.id)}`;
    link.className = "toc-link";
    link.textContent = label.length > 66 ? `${label.slice(0, 63)}…` : label;
    link.dataset.depth = target.tagName === "H3" ? "3" : "2";
    container.appendChild(link);
    targets.push({ target, link });
  });
  if (!targets.length) return;
  nav.hidden = false;

  let activeId = "";
  const activate = (id: string): void => {
    if (activeId === id) return;
    activeId = id;
    targets.forEach((item) => {
      const active = item.target.id === id;
      item.link.classList.toggle("is-current", active);
      item.link.classList.toggle("is-active", active);
      if (active) item.link.setAttribute("aria-current", "location");
      else item.link.removeAttribute("aria-current");
    });
  };
  const hashTarget = (): string | null => {
    let id = "";
    try { id = decodeURIComponent(window.location.hash.slice(1)); }
    catch { id = window.location.hash.slice(1); }
    return targets.find((item) => item.target.id === id)?.target.id || null;
  };
  const updateOnScroll = (): void => {
    const threshold = 150;
    let current = targets[0];
    for (const item of targets) {
      if (item.target.getBoundingClientRect().top <= threshold) current = item;
      else break;
    }
    activate(current.target.id);
  };
  container.addEventListener("click", (event: MouseEvent) => {
    if (!(event.target instanceof Element)) return;
    const link = event.target.closest<HTMLAnchorElement>("a[href^='#']");
    if (link) {
      const id = decodeURIComponent(link.hash.slice(1));
      if (targets.some((item) => item.target.id === id)) activate(id);
    }
  });
  window.addEventListener("hashchange", () => {
    const id = hashTarget();
    if (id) activate(id);
    else updateOnScroll();
  });
  const observer = new IntersectionObserver(updateOnScroll, { rootMargin: "-100px 0px -65% 0px" });
  targets.forEach((item) => observer.observe(item.target));
  window.addEventListener("scroll", updateOnScroll, { passive: true });
  activate(hashTarget() || targets[0].target.id);
}
