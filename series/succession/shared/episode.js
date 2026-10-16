(() => {
  'use strict';

  const source = document.querySelector('#episode-data');
  if (!source) return;
  const data = JSON.parse(source.textContent);
  const images = new Map(data.images.map(item => [item.id, item]));
  const phases = new Map(data.phases.map(item => [item.id, item]));
  const characterLinks = [...document.querySelectorAll('[data-character]')];
  const personCards = [...document.querySelectorAll('.person-card')];
  const phaseButtons = [...document.querySelectorAll('[data-phase]')];
  const conflictLinks = [...document.querySelectorAll('[data-conflict]')];
  const conflictPanels = [...document.querySelectorAll('.conflict-panel')];

  function selectCharacter(id) {
    if (!personCards.some(card => card.id === `person-${id}`)) return;
    personCards.forEach(card => { card.hidden = card.id !== `person-${id}`; });
    characterLinks.forEach(link => {
      const selected = link.dataset.character === id;
      link.classList.toggle('selected', selected);
      if (selected) link.setAttribute('aria-current', 'true');
      else link.removeAttribute('aria-current');
    });
  }

  function selectPhase(id) {
    const phase = phases.get(id);
    if (!phase) return;
    phaseButtons.forEach(button => button.setAttribute('aria-pressed', String(button.dataset.phase === id)));
    document.querySelectorAll('[data-phase-summary]').forEach(panel => {
      panel.hidden = panel.dataset.phaseSummary !== id;
    });
    document.querySelectorAll('[data-person-phase]').forEach(panel => {
      panel.hidden = panel.dataset.personPhase !== id;
    });
    document.querySelectorAll('[data-edge]').forEach(label => {
      label.textContent = phase.edges[Number(label.dataset.edge)];
    });
  }

  function selectConflict(id) {
    if (!conflictPanels.some(panel => panel.id === `conflict-${id}`)) return;
    conflictPanels.forEach(panel => { panel.hidden = panel.id !== `conflict-${id}`; });
    conflictLinks.forEach(link => {
      if (link.dataset.conflict === id) link.setAttribute('aria-current', 'true');
      else link.removeAttribute('aria-current');
    });
  }

  characterLinks.forEach(link => link.addEventListener('click', event => {
    event.preventDefault();
    selectCharacter(link.dataset.character);
    // Bring the profile into view only when the layout puts it below the graph.
    if (window.matchMedia('(max-width: 1000px)').matches) {
      document.querySelector(`#person-${link.dataset.character}`).scrollIntoView({ block: 'start' });
    }
  }));
  phaseButtons.forEach(button => button.addEventListener('click', () => selectPhase(button.dataset.phase)));
  conflictLinks.forEach(link => link.addEventListener('click', event => {
    event.preventDefault();
    selectConflict(link.dataset.conflict);
  }));

  selectCharacter(data.initialCharacter || 'logan');
  selectPhase(data.phases[0].id);
  selectConflict(conflictPanels[0].id.slice('conflict-'.length));
  document.body.classList.add('js-ready');

  function revealFragment() {
    const id = decodeURIComponent(location.hash.slice(1));
    if (id.startsWith('person-')) selectCharacter(id.slice(7));
    if (id.startsWith('conflict-')) selectConflict(id.slice(9));
    const target = document.getElementById(id);
    if (!target) return;
    for (let ancestor = target.parentElement; ancestor; ancestor = ancestor.parentElement) {
      if (ancestor.tagName === 'DETAILS') ancestor.open = true;
    }
    target.scrollIntoView({ block: 'start' });
  }
  window.addEventListener('hashchange', revealFragment);
  if (location.hash) revealFragment();

  const lightbox = document.querySelector('#image-lightbox');
  const lightboxImage = document.querySelector('#lightbox-image');
  const lightboxCaption = document.querySelector('#lightbox-caption');
  let previousOverflow = '';
  if (lightbox && typeof lightbox.showModal === 'function') {
    document.querySelectorAll('[data-photo]').forEach(link => link.addEventListener('click', event => {
      const item = images.get(link.dataset.photo);
      if (!item || event.ctrlKey || event.metaKey || event.shiftKey || event.altKey) return;
      event.preventDefault();
      lightboxImage.src = item.file;
      lightboxImage.alt = item.alt;
      lightboxImage.width = item.width;
      lightboxImage.height = item.height;
      lightboxCaption.textContent = `${item.caption} · 原始画面 ${item.width} × ${item.height}`;
      previousOverflow = document.body.style.overflow;
      document.body.style.overflow = 'hidden';
      lightbox.showModal();
    }));
    lightbox.querySelector('.lightbox-close').addEventListener('click', () => lightbox.close());
    lightbox.addEventListener('click', event => {
      if (event.target === lightbox) lightbox.close();
    });
    lightbox.addEventListener('close', () => { document.body.style.overflow = previousOverflow; });
  }

  const progress = document.querySelector('.reading-progress span');
  let scheduled = false;
  function updateProgress() {
    const length = document.documentElement.scrollHeight - window.innerHeight;
    progress.style.width = `${length > 0 ? Math.min(100, Math.max(0, window.scrollY / length * 100)) : 0}%`;
    scheduled = false;
  }
  function scheduleProgress() {
    if (!scheduled) {
      scheduled = true;
      requestAnimationFrame(updateProgress);
    }
  }
  window.addEventListener('scroll', scheduleProgress, { passive: true });
  window.addEventListener('resize', scheduleProgress);
  // Expanded source notes and switched panels also change the document length.
  if ('ResizeObserver' in window) new ResizeObserver(scheduleProgress).observe(document.body);
  updateProgress();

  if ('IntersectionObserver' in window) {
    const navigation = [...document.querySelectorAll('.masthead nav a')];
    const observer = new IntersectionObserver(entries => {
      const current = entries.filter(entry => entry.isIntersecting).sort((a, b) => a.boundingClientRect.top - b.boundingClientRect.top)[0];
      if (!current) return;
      navigation.forEach(link => {
        if (link.hash === `#${current.target.id}`) link.setAttribute('aria-current', 'location');
        else link.removeAttribute('aria-current');
      });
    }, { rootMargin: '-100px 0px -55% 0px' });
    navigation.forEach(link => {
      const section = document.getElementById(link.hash.slice(1));
      if (section) observer.observe(section);
    });
  }
})();
