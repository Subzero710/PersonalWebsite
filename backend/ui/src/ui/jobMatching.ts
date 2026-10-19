export function setupJobMatching(): void {
  const panel = document.querySelector<HTMLElement>('#jobMatchPanel');
  const trigger = document.querySelector<HTMLButtonElement>('#jobMatchTrigger');
  const form = document.querySelector<HTMLFormElement>('#jobMatchForm');
  const dialog = panel?.querySelector<HTMLElement>('.jobmatch-dialog');
  const close = panel?.querySelector<HTMLButtonElement>('#jobMatchClose');
  const submit = panel?.querySelector<HTMLButtonElement>('#jobMatchSubmit');
  const description = panel?.querySelector<HTMLTextAreaElement>('#jobMatchDescription');
  const counter = panel?.querySelector<HTMLElement>('#jobMatchCount');
  const status = panel?.querySelector<HTMLElement>('#jobMatchStatus');
  if (!panel || !trigger || !form || !dialog || !close || !submit || !description || !counter || !status) return;

  let pending = false;
  let lastFocus: HTMLElement | null = null;
  const setStatus = (text: string, isError = false) => {
    status.textContent = text;
    status.classList.toggle('is-error', isError);
  };
  const show = () => {
    lastFocus = document.activeElement instanceof HTMLElement ? document.activeElement : null;
    panel.hidden = false;
    document.body.classList.add('jobmatch-open');
    trigger.setAttribute('aria-expanded', 'true');
    setStatus('');
    close.focus();
  };
  const hide = () => {
    if (pending) return;
    panel.hidden = true;
    document.body.classList.remove('jobmatch-open');
    trigger.setAttribute('aria-expanded', 'false');
    lastFocus?.focus();
  };
  trigger.addEventListener('click', show);
  close.addEventListener('click', hide);
  panel.addEventListener('click', (event) => { if (event.target === panel) hide(); });
  description.addEventListener('input', () => { counter.textContent = String(description.value.length); });
  document.addEventListener('keydown', (event) => {
    if (panel.hidden) return;
    if (event.key === 'Escape') { event.preventDefault(); hide(); }
    if (event.key !== 'Tab') return;
    const focusable = Array.from(panel.querySelectorAll<HTMLElement>('button:not([disabled]), input:not([disabled]), textarea:not([disabled])'));
    if (!focusable.length) return;
    const first = focusable[0], last = focusable[focusable.length - 1];
    if (event.shiftKey && document.activeElement === first) { event.preventDefault(); last.focus(); }
    else if (!event.shiftKey && document.activeElement === last) { event.preventDefault(); first.focus(); }
  });

  form.addEventListener('submit', async (event) => {
    event.preventDefault();
    if (pending || !form.reportValidity()) return;
    pending = true;
    submit.disabled = true;
    close.disabled = true;
    setStatus('Analyzing the requirements and preparing your PDF…');
    try {
      const response = await fetch(form.action, {
        method: 'POST', body: new FormData(form), credentials: 'same-origin',
        cache: 'no-store', headers: { 'Accept': 'application/pdf, application/json' },
      });
      if (!response.ok) {
        const payload = await response.json().catch(() => ({}));
        throw new Error(typeof payload.error === 'string' ? payload.error : 'Could not generate the report. Please try again.');
      }
      const blob = await response.blob();
      if (!response.headers.get('content-type')?.includes('application/pdf') || blob.size === 0) {
        throw new Error('The server did not return a valid PDF.');
      }
      const disposition = response.headers.get('content-disposition') || '';
      const filename = disposition.match(/filename="([a-z0-9_.-]+\.pdf)"/i)?.[1] || 'job_matching_report.pdf';
      const objectUrl = URL.createObjectURL(blob);
      const anchor = document.createElement('a');
      anchor.href = objectUrl;
      anchor.download = filename;
      document.body.appendChild(anchor);
      anchor.click();
      anchor.remove();
      setTimeout(() => URL.revokeObjectURL(objectUrl), 1000);
      setStatus('PDF ready. Your download should start automatically.');
    } catch (error) {
      setStatus(error instanceof Error ? error.message : 'Could not generate the PDF.', true);
    } finally {
      pending = false;
      submit.disabled = false;
      close.disabled = false;
    }
  });
}
