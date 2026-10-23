/* Single person's settings grouped by actual public-facing page. */
(function () {
  "use strict";
  document.addEventListener('DOMContentLoaded', function () {
    const form = document.querySelector('form#siteconfig_form');
    if (!form) return;

    const names = ['Overview', 'About', 'Tech Stack', 'Contact & Links', 'Identity'];
    const sections = new Map();
    const fieldsets = Array.from(form.querySelectorAll('fieldset.module'));
    for (const fieldset of fieldsets) {
      const heading = fieldset.querySelector('h2');
      if (!heading) continue;
      const name = heading.textContent.trim();
      if (!names.includes(name)) continue;
      fieldset.id = 'settings-' + name.toLowerCase().replace(/[^a-z0-9]+/g, '-');
      sections.set(name, fieldset);
    }

    // Django renders all inlines after all fieldsets. Put them under the
    // right page instead of leaving an unrelated group at the bottom.
    const inlineGroups = [
      ['focus_items-group', 'Overview'],
      ['updates-group', 'Overview'],
      ['kpis-group', 'Overview'],
      ['social_links-group', 'Contact & Links'],
    ];
    const lastInGroup = new Map();
    for (const [id, name] of inlineGroups) {
      const item = document.getElementById(id);
      const parent = lastInGroup.get(name) || sections.get(name);
      if (!item || !parent) continue;
      parent.after(item);
      lastInGroup.set(name, item);
    }

    const targets = names.filter(name => sections.has(name));
    if (!targets.length) return;
    const nav = document.createElement('nav');
    nav.setAttribute('aria-label', 'Website page settings');
    nav.className = 'siteconfig-page-nav';
    Object.assign(nav.style, {
      display: 'flex', flexWrap: 'wrap', gap: '12px',
      margin: '16px 0 20px', padding: '12px',
      border: '1px solid var(--hairline-color, #8884)',
      borderRadius: '6px'
    });
    for (const name of targets) {
      const link = document.createElement('a');
      link.href = '#' + sections.get(name).id;
      link.textContent = name;
      nav.appendChild(link);
    }
    sections.get(targets[0]).before(nav);
  });
})();
