const MAX_FILTERS = 7;

type ProjectItem = {
  element: HTMLElement;
  searchText: string;
  tags: string[];
};

export function setupProjectFilters(): void {
  const grid = document.querySelector<HTMLElement>("#projectsGrid");
  const search = document.querySelector<HTMLInputElement>("#projectSearch");
  if (!grid || !search) return;

  const tagBar = document.querySelector<HTMLElement>("#tagBar");
  const more = document.querySelector<HTMLButtonElement>("#moreProjectTags");
  const count = document.querySelector<HTMLElement>("#projectCount");
  const noMatches = document.querySelector<HTMLElement>("#noProjectMatches");
  const reset = document.querySelector<HTMLButtonElement>("#resetProjectFilters");
  const allButton = tagBar?.querySelector<HTMLButtonElement>('button[data-tag="all"]');
  const tagButtons = Array.from(tagBar?.querySelectorAll<HTMLButtonElement>('button[data-tag]:not([data-tag="all"])') || []);

  // Names are provided for *all* associated tags, even if the card displays only three.
  const cards: ProjectItem[] = Array.from(grid.querySelectorAll<HTMLElement>(".project-card"), (element) => ({
    element,
    searchText: [element.dataset.title || "", element.dataset.summary || "", element.dataset.tagNames || ""].join(" ").toLocaleLowerCase(),
    tags: (element.dataset.tags || "").split(",").filter(Boolean),
  }));

  let activeTag = "all";
  let showMore = false;
  const initialQuery = new URLSearchParams(window.location.search).get("q");
  if (initialQuery !== null) search.value = initialQuery;

  const apply = (): void => {
    const query = search.value.trim().toLocaleLowerCase();
    const searching = query.length > 0;
    const matchedBySearch = cards.filter((card) => !searching || card.searchText.includes(query));
    const tagCounts = new Map<string, number>();
    for (const card of matchedBySearch) {
      for (const slug of new Set(card.tags)) tagCounts.set(slug, (tagCounts.get(slug) || 0) + 1);
    }

    const relevant = tagButtons.filter((button) => (tagCounts.get(button.dataset.tag || "") || 0) > 0);
    if (searching) {
      relevant.sort((a, b) =>
        (tagCounts.get(b.dataset.tag || "") || 0) - (tagCounts.get(a.dataset.tag || "") || 0) ||
        (a.dataset.tagName || "").localeCompare(b.dataset.tagName || "")
      );
    }
    // On an empty search, buttons retain the backend's popularity order.
    const shown = new Set((showMore ? relevant : relevant.slice(0, MAX_FILTERS)).map((button) => button.dataset.tag));
    // Never hide an active filter, including when it yields zero matching results.
    if (activeTag !== "all") shown.add(activeTag);
    for (const button of tagButtons) {
      button.hidden = !shown.has(button.dataset.tag);
      const selected = button.dataset.tag === activeTag;
      button.classList.toggle("is-active", selected);
      button.setAttribute("aria-pressed", String(selected));
    }
    allButton?.classList.toggle("is-active", activeTag === "all");
    allButton?.setAttribute("aria-pressed", String(activeTag === "all"));

    if (more) {
      const remaining = Math.max(relevant.length - MAX_FILTERS, 0);
      more.hidden = remaining === 0;
      more.textContent = showMore ? "Fewer filters" : `More filters (+${remaining})`;
      more.setAttribute("aria-expanded", String(showMore));
    }

    let visible = 0;
    for (const card of cards) {
      const match = (!searching || card.searchText.includes(query)) &&
        (activeTag === "all" || card.tags.includes(activeTag));
      card.element.hidden = !match;
      if (match) visible++;
    }
    if (count) count.textContent = `${visible} ${visible === 1 ? "project" : "projects"}`;
    if (noMatches) noMatches.hidden = visible > 0 || cards.length === 0;
  };

  search.addEventListener("input", () => {
    showMore = false;
    apply();
  });
  tagBar?.addEventListener("click", (event: MouseEvent) => {
    if (!(event.target instanceof Element)) return;
    const button = event.target.closest<HTMLButtonElement>("button[data-tag]");
    if (!button) return;
    activeTag = button.dataset.tag || "all";
    apply();
  });
  more?.addEventListener("click", () => {
    showMore = !showMore;
    apply();
  });
  reset?.addEventListener("click", () => {
    search.value = "";
    activeTag = "all";
    showMore = false;
    const url = new URL(window.location.href);
    url.searchParams.delete("q");
    window.history.replaceState(null, "", `${url.pathname}${url.search}${url.hash}`);
    apply();
    search.focus();
  });
  apply();
}
