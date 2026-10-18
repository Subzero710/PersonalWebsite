
export function setupProjectFilters(): void {
  const grid = document.querySelector<HTMLElement>("#projectsGrid");
  const search = document.querySelector<HTMLInputElement>("#projectSearch");
  if (!grid || !search) return;
  const tagBar = document.querySelector<HTMLElement>("#tagBar");
  const count = document.querySelector<HTMLElement>("#projectCount");
  const noMatches = document.querySelector<HTMLElement>("#noProjectMatches");
  const reset = document.querySelector<HTMLButtonElement>("#resetProjectFilters");
  const cards = Array.from(grid.querySelectorAll<HTMLElement>(".project-card"));
  let activeTag = "all";
  const initialQuery = new URLSearchParams(window.location.search).get("q");
  if (initialQuery !== null) search.value = initialQuery;

  const apply = (): void => {
    const query = search.value.trim().toLocaleLowerCase();
    let visible = 0;
    cards.forEach((card) => {
      const tags = (card.dataset.tags || "").split(",").filter(Boolean);
      const searchable = [card.dataset.title || "", card.dataset.summary || "", ...Array.from(card.querySelectorAll<HTMLElement>(".chip"), (chip) => chip.textContent || "")].join(" ").toLocaleLowerCase();
      const match = (!query || searchable.includes(query)) && (activeTag === "all" || tags.includes(activeTag));
      card.hidden = !match;
      if (match) visible += 1;
    });
    if (count) count.textContent = `${visible} ${visible === 1 ? "project" : "projects"}`;
    if (noMatches) noMatches.hidden = visible > 0 || cards.length === 0;
  };

  search.addEventListener("input", apply);
  tagBar?.addEventListener("click", (event: MouseEvent) => {
    if (!(event.target instanceof Element)) return;
    const button = event.target.closest<HTMLButtonElement>("button[data-tag]");
    if (!button) return;
    activeTag = button.dataset.tag || "all";
    tagBar.querySelectorAll<HTMLButtonElement>("button[data-tag]").forEach((item) => {
      const selected = item === button;
      item.classList.toggle("is-active", selected);
      item.setAttribute("aria-pressed", String(selected));
    });
    apply();
  });
  reset?.addEventListener("click", () => {
    search.value = "";
    activeTag = "all";
    tagBar?.querySelectorAll<HTMLButtonElement>("button[data-tag]").forEach((button) => {
      const selected = button.dataset.tag === "all";
      button.classList.toggle("is-active", selected);
      button.setAttribute("aria-pressed", String(selected));
    });
    const url = new URL(window.location.href);
    url.searchParams.delete("q");
    window.history.replaceState(null, "", `${url.pathname}${url.search}${url.hash}`);
    apply();
    search.focus();
  });
  apply();
}
