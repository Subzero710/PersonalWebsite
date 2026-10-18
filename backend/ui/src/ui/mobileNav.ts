
export function setupMobileNav(): void {
  const toggle = document.querySelector<HTMLButtonElement>("#menuToggle");
  const sidebar = document.querySelector<HTMLElement>("#siteSidebar");
  const overlay = document.querySelector<HTMLElement>("#sidebarOverlay");
  if (!toggle || !sidebar || !overlay) return;
  const media = window.matchMedia("(max-width: 820px)");
  let lastFocus: HTMLElement | null = null;
  const focusable = (): HTMLElement[] => Array.from(sidebar.querySelectorAll<HTMLElement>('a[href],button:not([disabled]),[tabindex]:not([tabindex="-1"])'));

  const close = (restoreFocus: boolean): void => {
    document.body.classList.remove("sidebar-open");
    toggle.setAttribute("aria-expanded", "false");
    toggle.setAttribute("aria-label", "Open navigation");
    sidebar.removeAttribute("aria-modal");
    sidebar.removeAttribute("role");
    if (restoreFocus) (lastFocus || toggle).focus();
  };
  const open = (): void => {
    if (!media.matches) return;
    lastFocus = document.activeElement instanceof HTMLElement ? document.activeElement : toggle;
    document.body.classList.add("sidebar-open");
    toggle.setAttribute("aria-expanded", "true");
    toggle.setAttribute("aria-label", "Close navigation");
    sidebar.setAttribute("role", "dialog");
    sidebar.setAttribute("aria-modal", "true");
    focusable()[0]?.focus();
  };
  toggle.addEventListener("click", () => document.body.classList.contains("sidebar-open") ? close(true) : open());
  overlay.addEventListener("click", () => close(true));
  sidebar.addEventListener("click", (event) => { if (event.target instanceof Element && event.target.closest("a[href]")) close(false); });
  document.addEventListener("keydown", (event: KeyboardEvent) => {
    if (!document.body.classList.contains("sidebar-open")) return;
    if (event.key === "Escape") { event.preventDefault(); close(true); return; }
    if (event.key !== "Tab") return;
    const elements = focusable();
    if (!elements.length) { event.preventDefault(); return; }
    const first = elements[0], last = elements[elements.length - 1];
    if (event.shiftKey && document.activeElement === first) { event.preventDefault(); last.focus(); }
    else if (!event.shiftKey && document.activeElement === last) { event.preventDefault(); first.focus(); }
    else if (!sidebar.contains(document.activeElement)) { event.preventDefault(); first.focus(); }
  });
  media.addEventListener("change", () => { if (!media.matches) close(false); });
}
