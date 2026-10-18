
export function setupGlobalSearch(): void {
  const field = document.querySelector<HTMLInputElement>("#globalSearch");
  if (!field) return;
  const shortcut = document.querySelector<HTMLElement>(".search-shortcut");
  if (shortcut) shortcut.textContent = /Mac|iPhone|iPad/.test(navigator.platform) ? "⌘ K" : "Ctrl K";
  document.addEventListener("keydown", (event: KeyboardEvent) => {
    if (event.key.toLowerCase() !== "k" || (!event.ctrlKey && !event.metaKey) || event.altKey || event.shiftKey) return;
    event.preventDefault();
    field.focus();
    field.select();
  });
}
