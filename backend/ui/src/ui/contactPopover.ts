export function setupContactPopover(): void {
  const panel = document.querySelector<HTMLElement>("#connectPanel");
  const dialog = panel?.querySelector<HTMLElement>(".connect-dialog");
  const closeButton = document.querySelector<HTMLButtonElement>("#connectClose");
  const triggers = Array.from(document.querySelectorAll<HTMLButtonElement>("[data-connect-trigger]"));
  if (!panel || !dialog || !closeButton || triggers.length === 0) return;

  let previousFocus: HTMLElement | null = null;
  const isOpen = (): boolean => !panel.hidden;
  const focusable = (): HTMLElement[] => Array.from(dialog.querySelectorAll<HTMLElement>(
    'a[href], button:not([disabled]), [tabindex]:not([tabindex="-1"])'
  ));

  const close = (restoreFocus = true): void => {
    if (!isOpen()) return;
    panel.hidden = true;
    document.body.classList.remove("connect-open");
    triggers.forEach((trigger) => trigger.setAttribute("aria-expanded", "false"));
    if (restoreFocus) {
      const target = previousFocus && previousFocus.getClientRects().length ? previousFocus : triggers[0];
      target?.focus();
    }
  };

  const open = (trigger: HTMLButtonElement): void => {
    if (isOpen()) return;
    previousFocus = trigger;
    panel.hidden = false;
    document.body.classList.add("connect-open");
    triggers.forEach((button) => button.setAttribute("aria-expanded", "true"));
    closeButton.focus();
  };

  triggers.forEach((trigger) => {
    trigger.addEventListener("click", () => isOpen() ? close(false) : open(trigger));
  });
  closeButton.addEventListener("click", () => close());
  panel.addEventListener("pointerdown", (event) => {
    if (event.target === panel) close();
  });
  dialog.addEventListener("click", (event) => {
    if (event.target instanceof Element && event.target.closest("a[href]")) close();
  });
  document.addEventListener("keydown", (event: KeyboardEvent) => {
    if (!isOpen()) return;
    if (event.key === "Escape") {
      event.preventDefault();
      close();
      return;
    }
    if (event.key !== "Tab") return;
    const items = focusable();
    if (!items.length) {
      event.preventDefault();
      dialog.focus();
      return;
    }
    const first = items[0], last = items[items.length - 1];
    if (event.shiftKey && (document.activeElement === first || !dialog.contains(document.activeElement))) {
      event.preventDefault();
      last.focus();
    } else if (!event.shiftKey && (document.activeElement === last || !dialog.contains(document.activeElement))) {
      event.preventDefault();
      first.focus();
    }
  });
  document.addEventListener("focusin", (event) => {
    if (isOpen() && event.target instanceof Node && !dialog.contains(event.target)) closeButton.focus();
  });
}
