(() => {
  'use strict';
  const data = JSON.parse(document.getElementById('episode-data').textContent);
  const escapeHTML = value => String(value).replace(/[&<>"']/g, char => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[char]));
  const portrait = key => {
    const person = data.portraits[key];
    return `<span class="portrait" style="--position:${escapeHTML(person.position)};--zoom:${person.zoom}"><img src="../shared/${escapeHTML(person.file)}" alt="${escapeHTML(person.name)}的剧中角色照"></span>`;
  };
  let selected = 'wendy';
  let phase = data.phases[0];
  const renderPerson = () => {
    const p = data.portraits[selected];
    const c = data.characters[selected];
    document.getElementById('person-detail').innerHTML = `<div class="detail-heading">${portrait(selected)}<div><h3>${escapeHTML(p.name)}</h3><small>${escapeHTML(p.en)}</small></div></div><p class="role">${escapeHTML(c.role)}</p><span class="fact-label">本集行动 · 剧情事实</span><p>${escapeHTML(c.fact)}</p><span class="analysis-label">人物阅读 · 个人解读</span><p>${escapeHTML(c.analysis)}</p><p class="phase-detail"><strong>${escapeHTML(phase.name)}</strong><br>${escapeHTML(phase.details[selected])}</p><small class="fact-label">${escapeHTML(p.actor)} 饰</small>`;
    document.querySelectorAll('[data-person]').forEach(button => button.setAttribute('aria-pressed', String(button.dataset.person === selected)));
  };
  document.querySelectorAll('[data-person]').forEach(button => button.addEventListener('click', () => { selected = button.dataset.person; renderPerson(); }));
  document.querySelectorAll('[data-phase]').forEach(button => button.addEventListener('click', () => {
    phase = data.phases.find(item => item.id === button.dataset.phase);
    document.querySelectorAll('[data-phase]').forEach(tab => tab.setAttribute('aria-pressed', String(tab === button)));
    phase.edges.forEach((label, index) => { document.getElementById(`edge-${index}`).textContent = label; });
    document.getElementById('graph-note').textContent = phase.note;
    renderPerson();
  }));
  document.querySelectorAll('[data-order]').forEach(button => button.addEventListener('click', () => {
    const grouped = button.dataset.order === 'threads';
    const laneOrder = ['law', 'capital', 'wendy', 'cross'];
    const cards = [...document.querySelectorAll('.scene')];
    cards.sort((a, b) => grouped ? laneOrder.indexOf(a.dataset.lane) - laneOrder.indexOf(b.dataset.lane) || Number(a.dataset.index) - Number(b.dataset.index) : Number(a.dataset.index) - Number(b.dataset.index));
    const timeline = document.getElementById('timeline');
    const fragment = document.createDocumentFragment();
    cards.forEach(card => fragment.append(card));
    timeline.append(fragment);
    document.querySelectorAll('[data-order]').forEach(tab => tab.setAttribute('aria-pressed', String(tab === button)));
    document.getElementById('order-note').textContent = grouped ? '按查克线、阿克斯线、温迪线、交锋与结尾排列；编号保留原顺序，方便回到对应场景。' : '按本集推进顺序归纳；同一节点可合并相关片段，父子谈话等后续揭示会明确说明。';
  }));
  let quoteIndex = 0;
  const renderQuote = () => {
    const quote = data.quotes[quoteIndex];
    const meta = data.images.find(item => item.file === `assets/${quote.image}.jpg`);
    document.getElementById('quote-image').src = meta.file;
    document.getElementById('quote-image').alt = meta.alt;
    document.getElementById('quote-image-caption').textContent = meta.caption + ' · Showtime / SIMKL';
    document.getElementById('quote-note-body').innerHTML = `<div class="eyebrow">${escapeHTML(quote.speaker)}</div><blockquote lang="en">${escapeHTML(quote.en)}</blockquote><p class="translation">${escapeHTML(quote.zh)}</p><p class="context">场景 / ${escapeHTML(quote.context)}</p><span class="analysis-label">潜台词 · 个人解读</span><p class="quote-analysis">${escapeHTML(quote.analysis)}</p>`;
    document.getElementById('quote-count').textContent = `${String(quoteIndex + 1).padStart(2, '0')} / ${String(data.quotes.length).padStart(2, '0')}`;
  };
  document.getElementById('quote-prev').addEventListener('click', () => { quoteIndex = (quoteIndex - 1 + data.quotes.length) % data.quotes.length; renderQuote(); });
  document.getElementById('quote-next').addEventListener('click', () => { quoteIndex = (quoteIndex + 1) % data.quotes.length; renderQuote(); });
  const navLinks = [...document.querySelectorAll('.nav-items a[href^="#"]')];
  const observer = new IntersectionObserver(entries => {
    entries.forEach(entry => {
      if (entry.isIntersecting) navLinks.forEach(link => {
        const active = link.hash === `#${entry.target.id}`;
        link.classList.toggle('active', active);
        if (active) link.setAttribute('aria-current', 'location');
        else link.removeAttribute('aria-current');
      });
    });
  }, {rootMargin:'-15% 0px -65% 0px'});
  navLinks.forEach(link => { const target = document.querySelector(link.hash); if (target) observer.observe(target); });
  const progress = document.getElementById('reading-progress');
  const updateProgress = () => {
    const total = document.documentElement.scrollHeight - window.innerHeight;
    progress.style.width = `${total > 0 ? Math.min(100, Math.max(0, window.scrollY / total * 100)) : 0}%`;
  };
  window.addEventListener('scroll', updateProgress, {passive:true});
  window.addEventListener('resize', updateProgress);
  renderPerson();
  updateProgress();
})();
