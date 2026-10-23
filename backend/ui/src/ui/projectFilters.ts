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
  const count = document.querySelector<HTMLElement>("#projectCount");
  const noMatches = document.querySelector<HTMLElement>("#noProjectMatches");
  const reset = document.querySelector<HTMLButtonElement>("#resetProjectFilters");
  const allButton = tagBar?.querySelector<HTMLButtonElement>('button[data-tag="all"]');
  const tagButtons = Array.from(tagBar?.querySelectorAll<HTMLButtonElement>('button[data-tag]:not([data-tag="all"])') || []);

  const cards: ProjectItem[] = Array.from(grid.querySelectorAll<HTMLElement>(".project-card"), (element) => ({
    element,
    searchText: [element.dataset.title || "", element.dataset.summary || "", element.dataset.tagNames || ""].join(" ").toLocaleLowerCase(),
    tags: (element.dataset.tags || "").split(",").filter(Boolean),
  }));

  let activeTag = "all";
  const initialQuery = new URLSearchParams(window.location.search).get("q");
  if (initialQuery !== null) search.value = initialQuery;

  const apply = (): void => {
    const query = search.value.trim().toLocaleLowerCase();
    const searching = query.length > 0;

    for (const button of tagButtons) {
      const selected = button.dataset.tag === activeTag;
      button.classList.toggle("is-active", selected);
      button.setAttribute("aria-pressed", String(selected));
    }
    allButton?.classList.toggle("is-active", activeTag === "all");
    allButton?.setAttribute("aria-pressed", String(activeTag === "all"));

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

  search.addEventListener("input", apply);
  tagBar?.addEventListener("click", (event: MouseEvent) => {
    if (!(event.target instanceof Element)) return;
    const button = event.target.closest<HTMLButtonElement>("button[data-tag]");
    if (!button) return;
    activeTag = button.dataset.tag || "all";
    apply();
  });
  reset?.addEventListener("click", () => {
    search.value = "";
    activeTag = "all";
    const url = new URL(window.location.href);
    url.searchParams.delete("q");
    window.history.replaceState(null, "", `${url.pathname}${url.search}${url.hash}`);
    apply();
    search.focus();
  });

  apply();
}
