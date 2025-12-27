import { setupReveal } from "./ui/reveal";
import { setupActiveNav } from "./ui/navActive";
import { setupProjectFilters } from "./ui/projectFilters";
import { setupCopyButtons } from "./ui/copy";
document.documentElement.classList.add("js");
setupReveal();
setupActiveNav();
setupProjectFilters();
setupCopyButtons();