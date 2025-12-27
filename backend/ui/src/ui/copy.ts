export function setupCopyButtons() {
  document.addEventListener("click", async (e) => {
    const btn = (e.target as HTMLElement).closest<HTMLElement>("[data-copy]");
    if (!btn) return;

    const text = btn.getAttribute("data-copy") ?? "";
    if (!text) return;

    try {
      await navigator.clipboard.writeText(text);
      btn.textContent = "Copied ✓";
      setTimeout(() => (btn.textContent = "Copy email"), 1200);
    } catch {
      // fallback
      window.prompt("Copy:", text);
    }
  });
}