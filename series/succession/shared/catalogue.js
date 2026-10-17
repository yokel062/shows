(() => {
  'use strict';

  const links = [...document.querySelectorAll('.episode-jump a')];
  const cards = [...document.querySelectorAll('.season-card')];
  if (!links.length || !cards.length || !('IntersectionObserver' in window)) return;

  const visible = new Set();
  let selected = null;
  let pending = cards.some(card => `#${card.id}` === location.hash) ? location.hash.slice(1) : null;
  const activate = id => {
    selected = id;
    for (const link of links) {
      if (link.hash === `#${id}`) link.setAttribute('aria-current', 'location');
      else link.removeAttribute('aria-current');
    }
  };

  const observer = new IntersectionObserver(entries => {
    for (const entry of entries) {
      if (entry.isIntersecting) visible.add(entry.target);
      else visible.delete(entry.target);
    }
    if (pending) {
      const target = cards.find(card => card.id === pending);
      if (!visible.has(target)) return;
      activate(pending);
      pending = null;
      return;
    }
    const first = cards.find(card => card.id === selected && visible.has(card)) || cards.find(card => visible.has(card));
    if (first) activate(first.id);
    else for (const link of links) link.removeAttribute('aria-current');
  }, { rootMargin: '-100px 0px -35% 0px', threshold: 0 });

  for (const card of cards) observer.observe(card);
  for (const link of links) link.addEventListener('click', () => {
    pending = link.hash.slice(1);
    activate(pending);
  });
})();
