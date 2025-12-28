import { setupReveal } from "./ui/reveal";
import { setupActiveNav } from "./ui/navActive";
import { setupProjectFilters } from "./ui/projectFilters";
import { setupCopyButtons } from "./ui/copy";

document.documentElement.classList.add("js");

for (const el of document.querySelectorAll<HTMLElement>(".card")) {
  el.addEventListener("pointermove", (e) => {
    const r = el.getBoundingClientRect();
    el.style.setProperty("--mx", `${e.clientX - r.left}px`);
    el.style.setProperty("--my", `${e.clientY - r.top}px`);
  });
}

setupReveal();
setupActiveNav();
setupProjectFilters();
setupCopyButtons();