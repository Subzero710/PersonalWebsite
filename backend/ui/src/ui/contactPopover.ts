export function setupContactPopover(): void {
  const wrap = document.querySelector<HTMLElement>("#connectMenu");
  const trigger = document.querySelector<HTMLButtonElement>("#connectTrigger");
  const panel = document.querySelector<HTMLElement>("#connectPanel");
  if (!wrap || !trigger || !panel) return;

  const close = (restoreFocus = false): void => {
    panel.hidden = true;
    trigger.setAttribute("aria-expanded", "false");
    if (restoreFocus) trigger.focus();
  };
  const open = (keyboard: boolean): void => {
    panel.hidden = false;
    trigger.setAttribute("aria-expanded", "true");
    if (keyboard) panel.querySelector<HTMLAnchorElement>("a[href]")?.focus();
  };

  trigger.addEventListener("click", (event) => {
    if (panel.hidden) open(event.detail === 0);
    else close();
  });
  document.addEventListener("pointerdown", (event) => {
    if (event.target instanceof Node && !wrap.contains(event.target)) close();
  });
  document.addEventListener("keydown", (event) => {
    if (event.key === "Escape" && !panel.hidden) {
      event.preventDefault();
      close(true);
    }
  });
  wrap.addEventListener("focusout", (event) => {
    const next = event.relatedTarget;
    if (next instanceof Node && !wrap.contains(next)) close();
  });
}
