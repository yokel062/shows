(() => {
  'use strict';
  const data = JSON.parse(document.getElementById('episode-data').textContent);
  const images = Object.fromEntries(data.images.map(item => [item.id, item]));
  const escapeHTML = value => String(value).replace(/[&<>"']/g, char => ({'&':'&amp;', '<':'&lt;', '>':'&gt;', '"':'&quot;', "'":'&#39;'}[char]));
  const avatar = key => {
    const person = data.portraits[key];
    return `<span class="portrait"><img src="../shared/${escapeHTML(person.file)}" alt="${escapeHTML(person.name)}的剧中角色照" width="128" height="128"></span>`;
  };
  let selectedPerson = 'walt';
  let selectedPhase = data.phases[0];
  const renderPerson = () => {
    const portrait = data.portraits[selectedPerson];
    const character = data.characters[selectedPerson];
    document.getElementById('person-detail').innerHTML = `<div class="detail-heading">${avatar(selectedPerson)}<div><h3>${escapeHTML(portrait.name)}</h3><small>${escapeHTML(portrait.en)}</small></div></div><p class="detail-role">${escapeHTML(character.role)}</p><h4>想要什么 · 人物阅读</h4><p class="want">${escapeHTML(character.want)}</p><h4>手中有什么</h4><p>${escapeHTML(character.leverage)}</p><h4>本集行动 · 剧情事实</h4><p>${escapeHTML(character.fact)}</p><h4>冲突位置 · 个人解读</h4><p>${escapeHTML(character.analysis)}</p><div class="phase-detail"><strong>${escapeHTML(selectedPhase.name)}</strong><p>${escapeHTML(selectedPhase.details[selectedPerson])}</p></div><div class="portrait-credit">${escapeHTML(portrait.actor)} 饰 · ${escapeHTML(portrait.credit)}</div>`;
    document.querySelectorAll('[data-person]').forEach(button => button.setAttribute('aria-pressed', String(button.dataset.person === selectedPerson)));
  };
  document.querySelectorAll('[data-person]').forEach(button => button.addEventListener('click', () => {
    selectedPerson = button.dataset.person;
    renderPerson();
  }));
  document.querySelectorAll('button[data-phase]').forEach(button => button.addEventListener('click', () => {
    selectedPhase = data.phases.find(phase => phase.id === button.dataset.phase);
    document.querySelectorAll('button[data-phase]').forEach(tab => tab.setAttribute('aria-pressed', String(tab === button)));
    selectedPhase.edges.forEach((label, index) => { document.getElementById(`edge-${index}`).textContent = label; });
    document.querySelector('.graph').dataset.phase = selectedPhase.id;
    document.getElementById('graph-note').textContent = selectedPhase.note;
    renderPerson();
  }));
  document.querySelectorAll('[data-conflict]').forEach(button => button.addEventListener('click', () => {
    const conflict = data.conflicts.find(item => item.id === button.dataset.conflict);
    const picture = images[conflict.image];
    document.querySelectorAll('[data-conflict]').forEach(tab => tab.setAttribute('aria-pressed', String(tab === button)));
    document.getElementById('conflict-content').innerHTML = `<figure class="conflict-photo"><img src="${escapeHTML(picture.file)}" alt="${escapeHTML(picture.alt)}" width="${picture.width}" height="${picture.height}"><figcaption>${escapeHTML(picture.caption)}</figcaption></figure><article class="conflict-copy"><div class="conflict-axis"><span>${escapeHTML(conflict.left)}</span><b>×</b><span>${escapeHTML(conflict.right)}</span></div><h3>${escapeHTML(conflict.title)}</h3><p>${escapeHTML(conflict.text)}</p><p>${escapeHTML(conflict.second)}</p><p class="fact-boundary">${escapeHTML(conflict.limit)}</p></article>`;
  }));
  let quoteIndex = 0;
  const renderQuote = () => {
    const quote = data.quotes[quoteIndex];
    const picture = images[quote.image];
    const image = document.getElementById('quote-image');
    Object.assign(image, {src:picture.file, alt:picture.alt, width:picture.width, height:picture.height});
    document.getElementById('quote-caption').textContent = picture.caption;
    document.getElementById('quote-content').innerHTML = `<div class="speaker">${escapeHTML(quote.speaker)}</div><blockquote lang="en">${escapeHTML(quote.en)}</blockquote><p class="translation">${escapeHTML(quote.zh)}<small>中文自译</small></p><h4>这句话发生在哪里</h4><p class="quote-context">${escapeHTML(quote.context)}</p><h4>没有说透的部分 · 个人解读</h4><p class="quote-analysis">${escapeHTML(quote.analysis)}</p>`;
    document.getElementById('quote-count').textContent = `${String(quoteIndex + 1).padStart(2, '0')} / ${String(data.quotes.length).padStart(2, '0')}`;
  };
  document.getElementById('quote-prev').addEventListener('click', () => { quoteIndex = (quoteIndex + data.quotes.length - 1) % data.quotes.length; renderQuote(); });
  document.getElementById('quote-next').addEventListener('click', () => { quoteIndex = (quoteIndex + 1) % data.quotes.length; renderQuote(); });
  const lightbox = document.getElementById('image-lightbox');
  document.querySelectorAll('[data-image]').forEach(button => button.addEventListener('click', () => {
    const picture = images[button.dataset.image];
    Object.assign(document.getElementById('lightbox-image'), {src:picture.file, alt:picture.alt});
    document.getElementById('lightbox-caption').textContent = picture.caption;
    lightbox.showModal();
  }));
  lightbox.querySelector('button').addEventListener('click', () => lightbox.close());
  lightbox.addEventListener('click', event => { if (event.target === lightbox) lightbox.close(); });
  const revealSource = hash => {
    if (hash.startsWith('#source-')) document.getElementById('source-details').open = true;
  };
  document.addEventListener('click', event => {
    const link = event.target.closest('a[href^="#source-"]');
    if (link) revealSource(link.hash);
  });
  window.addEventListener('hashchange', () => revealSource(window.location.hash));
  revealSource(window.location.hash);
  if (window.location.hash.startsWith('#source-')) requestAnimationFrame(() => document.getElementById(window.location.hash.slice(1))?.scrollIntoView());
  const navLinks = [...document.querySelectorAll('.masthead nav a')];
  const navSections = navLinks.map(link => ({link, section: document.querySelector(link.hash)}));
  const updateNavigation = atBottom => {
    let current = null;
    navSections.forEach(({link, section}) => {
      if (section && section.getBoundingClientRect().top <= 130) current = link;
    });
    if (atBottom) current = navLinks[navLinks.length - 1];
    navLinks.forEach(link => {
      const active = link === current;
      link.classList.toggle('active', active);
      if (active) link.setAttribute('aria-current', 'location');
      else link.removeAttribute('aria-current');
    });
  };
  const progress = document.getElementById('reading-progress');
  let progressPending = false;
  const updateProgress = () => {
    const total = document.documentElement.scrollHeight - window.innerHeight;
    progress.style.width = `${total > 0 ? Math.min(100, Math.max(0, window.scrollY / total * 100)) : 0}%`;
    updateNavigation(total - window.scrollY < 4);
    progressPending = false;
  };
  window.addEventListener('scroll', () => {
    if (!progressPending) { progressPending = true; requestAnimationFrame(updateProgress); }
  }, {passive:true});
  window.addEventListener('resize', updateProgress);
  updateProgress();
})();
