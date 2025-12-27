export function setupReveal() {
  const els = document.querySelectorAll<HTMLElement>(".reveal");
  const io = new IntersectionObserver((entries) => {
    for (const e of entries) {
      if (e.isIntersecting) {
        (e.target as HTMLElement).classList.add("in");
        io.unobserve(e.target);
      }
    }
  }, { threshold: 0.12 });

  els.forEach((el) => io.observe(el));
}