export function setupTheme(): void {
  const button = document.querySelector<HTMLButtonElement>("#themeToggle");
  if (!button) return;
  const root = document.documentElement;
  const apply = (): void => {
    const light = root.dataset.theme === "light";
    button.setAttribute("aria-pressed", String(light));
    button.setAttribute("aria-label", light ? "Switch to dark theme" : "Switch to light theme");
    const color = document.querySelector<HTMLMetaElement>('meta[name="theme-color"]');
    if (color) color.content = light ? "#f9fafc" : "#090d12";
  };
  apply();
  button.addEventListener("click", () => {
    const light = root.dataset.theme !== "light";
    if (light) root.dataset.theme = "light";
    else delete root.dataset.theme;
    try { window.localStorage.setItem("portfolio-theme", light ? "light" : "dark"); } catch {}
    apply();
  });
}
