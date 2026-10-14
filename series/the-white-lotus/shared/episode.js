(() => {
  'use strict';
  const dataNode = document.getElementById('episode-data');
  if (!dataNode) return;
  const data = JSON.parse(dataNode.textContent);
  const tabs = [...document.querySelectorAll('[data-conflict]')];
  const panels = [...document.querySelectorAll('.conflict-panel')];

  function selectConflict(id) {
    if (!panels.some(panel => panel.id === `conflict-${id}`)) return;
    panels.forEach(panel => { panel.hidden = panel.id !== `conflict-${id}`; });
    tabs.forEach(tab => {
      if (tab.dataset.conflict === id) tab.setAttribute('aria-current', 'true');
      else tab.removeAttribute('aria-current');
    });
  }

  function revealAnchor() {
    const target = document.getElementById(decodeURIComponent(location.hash.slice(1)));
    if (!target) return;
    if (target.classList.contains('conflict-panel')) selectConflict(target.id.replace('conflict-', ''));
    let parent = target;
    while (parent) {
      if (parent.tagName === 'DETAILS') parent.open = true;
      parent = parent.parentElement;
    }
    requestAnimationFrame(() => target.scrollIntoView({ block: 'start' }));
  }

  selectConflict(tabs[0].dataset.conflict);
  tabs.forEach(tab => tab.addEventListener('click', event => {
    event.preventDefault();
    selectConflict(tab.dataset.conflict);
    history.replaceState(null, '', tab.getAttribute('href'));
    requestAnimationFrame(updateProgress);
  }));
  window.addEventListener('hashchange', revealAnchor);
  if (location.hash) revealAnchor();

  const dialog = document.getElementById('photo-viewer');
  const picture = document.getElementById('lightbox-image');
  const caption = document.getElementById('lightbox-caption');
  let opener;
  document.querySelectorAll('[data-photo]').forEach(button => {
    button.addEventListener('click', () => {
      const item = data.images[button.dataset.photo];
      picture.src = item.file;
      picture.alt = item.alt;
      caption.textContent = item.caption;
      opener = button;
      dialog.showModal();
      document.body.classList.add('modal-open');
    });
  });
  dialog.querySelector('.lightbox-close').addEventListener('click', () => dialog.close());
  dialog.addEventListener('click', event => {
    const box = dialog.getBoundingClientRect();
    if (event.target === dialog && (event.clientX < box.left || event.clientX > box.right || event.clientY < box.top || event.clientY > box.bottom)) dialog.close();
  });
  dialog.addEventListener('close', () => {
    document.body.classList.remove('modal-open');
    if (opener) opener.focus({ preventScroll: true });
  });

  const progress = document.getElementById('reading-progress');
  let scheduled = false;
  function updateProgress() {
    const length = document.documentElement.scrollHeight - innerHeight;
    progress.style.width = `${length > 0 ? Math.min(100, scrollY / length * 100) : 0}%`;
    scheduled = false;
  }
  window.addEventListener('scroll', () => {
    if (!scheduled) { scheduled = true; requestAnimationFrame(updateProgress); }
  }, { passive: true });
  window.addEventListener('resize', updateProgress);
  document.querySelectorAll('details').forEach(detail => detail.addEventListener('toggle', updateProgress));
  window.addEventListener('load', updateProgress);
  updateProgress();

  const sections = [...document.querySelectorAll('main > section[id]')];
  if ('IntersectionObserver' in window) {
    const observer = new IntersectionObserver(entries => {
      entries.forEach(entry => {
        if (!entry.isIntersecting) return;
        document.querySelectorAll('.masthead nav a').forEach(link => {
          if (link.hash === `#${entry.target.id}`) link.setAttribute('aria-current', 'location');
          else link.removeAttribute('aria-current');
        });
      });
    }, { rootMargin: '-15% 0px -65% 0px' });
    sections.forEach(section => observer.observe(section));
  }
})();
