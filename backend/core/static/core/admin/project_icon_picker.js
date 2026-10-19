"use strict";
/* Django Admin visual icon selector. The submitted value is the original select. */
(function () {
  function makeSVG(sprite, key) {
    const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
    svg.setAttribute('viewBox', '0 0 24 24');
    svg.setAttribute('width', '22');
    svg.setAttribute('height', '22');
    svg.setAttribute('aria-hidden', 'true');
    const use = document.createElementNS('http://www.w3.org/2000/svg', 'use');
    use.setAttribute('href', sprite + '#' + (key || 'package'));
    svg.appendChild(use);
    return svg;
  }

  function enhance(select) {
    if (select.dataset.pickerReady === '1') return;
    select.dataset.pickerReady = '1';
    const sprite = select.dataset.iconSprite;
    if (!sprite) return;

    const picker = document.createElement('div');
    picker.className = 'project-icon-picker';
    picker.setAttribute('aria-label', 'Project icon picker');
    const title = document.createElement('p');
    title.className = 'project-icon-picker-caption';
    title.textContent = 'Choose the same icon for the project card and sidebar';
    picker.appendChild(title);

    const search = document.createElement('input');
    search.type = 'search';
    search.className = 'vTextField project-icon-picker-search';
    search.placeholder = 'Search icons (dashboard, security, chat…)';
    search.setAttribute('aria-label', 'Filter icons');
    picker.appendChild(search);

    const groups = [];
    const buttons = [];
    function addGroup(label, options) {
      const section = document.createElement('section');
      section.className = 'project-icon-picker-group';
      const heading = document.createElement('div');
      heading.className = 'project-icon-picker-heading';
      heading.textContent = label;
      section.appendChild(heading);
      const grid = document.createElement('div');
      grid.className = 'project-icon-picker-grid';
      section.appendChild(grid);
      options.forEach(function (option) {
        const btn = document.createElement('button');
        btn.type = 'button';
        btn.className = 'project-icon-picker-choice';
        btn.dataset.iconValue = option.value;
        btn.dataset.search = (option.label + ' ' + option.value + ' ' + label).toLowerCase();
        btn.setAttribute('aria-label', option.label);
        btn.setAttribute('aria-pressed', 'false');
        btn.appendChild(makeSVG(sprite, option.value));
        const span = document.createElement('span');
        span.textContent = option.label;
        btn.appendChild(span);
        btn.addEventListener('click', function () {
          select.value = option.value;
          select.dispatchEvent(new Event('change', { bubbles: true }));
        });
        buttons.push(btn);
        grid.appendChild(btn);
      });
      picker.appendChild(section);
      groups.push({ section: section, buttons: Array.from(grid.children) });
    }

    const ungrouped = Array.from(select.children).filter(function (node) {
      return node.tagName === 'OPTION';
    });
    if (ungrouped.length) addGroup('No custom icon', ungrouped);
    Array.from(select.querySelectorAll('optgroup')).forEach(function (group) {
      addGroup(group.label, Array.from(group.querySelectorAll('option')));
    });

    function updateSelection() {
      buttons.forEach(function (btn) {
        const active = btn.dataset.iconValue === select.value;
        btn.classList.toggle('is-selected', active);
        btn.setAttribute('aria-pressed', active ? 'true' : 'false');
      });
    }
    function filter() {
      const query = search.value.toLowerCase().trim();
      groups.forEach(function (group) {
        let visible = 0;
        group.buttons.forEach(function (btn) {
          const show = !query || btn.dataset.search.includes(query);
          btn.hidden = !show;
          if (show) visible++;
        });
        group.section.hidden = visible === 0;
      });
    }
    select.addEventListener('change', updateSelection);
    search.addEventListener('input', filter);
    select.insertAdjacentElement('afterend', picker);
    /* The native select continues to submit its value; the grid is the UI. */
    select.hidden = true;
    updateSelection();
  }

  function initialize() {
    document.querySelectorAll('select[data-project-icon-picker]').forEach(enhance);
  }
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initialize);
  } else {
    initialize();
  }
})();
