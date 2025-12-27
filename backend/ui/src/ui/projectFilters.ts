export function setupProjectFilters() {
  const grid = document.getElementById("projectsGrid");
  if (!grid) return;

  const search = document.getElementById("projectSearch") as HTMLInputElement | null;
  const tagBar = document.getElementById("tagBar");
  let activeTag = "all";

  const apply = () => {
    const q = (search?.value ?? "").trim().toLowerCase();
    grid.querySelectorAll<HTMLElement>(".card").forEach((card) => {
      const title = card.dataset.title ?? "";
      const tags = (card.dataset.tags ?? "").split(",").filter(Boolean);

      const okQ = !q || title.includes(q);
      const okT = activeTag === "all" || tags.includes(activeTag);

      card.style.display = (okQ && okT) ? "" : "none";
    });
  };

  search?.addEventListener("input", apply);

  tagBar?.addEventListener("click", (e) => {
    const b = (e.target as HTMLElement).closest<HTMLButtonElement>(".tagpill");
    if (!b) return;

    activeTag = b.dataset.tag ?? "all";
    tagBar.querySelectorAll(".tagpill").forEach(x => x.classList.remove("is-active"));
    b.classList.add("is-active");
    apply();
  });

  apply();
}