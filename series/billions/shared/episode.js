(() => {
  'use strict';
  const data = JSON.parse(document.getElementById('episode-data').textContent);
  const escapeHTML = value => String(value).replace(/[&<>"']/g, char => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[char]));
  const images = Object.fromEntries(data.images.map(item => [item.file.split('/').pop().replace(/\.[^.]+$/, ''), item]));
  const portrait = key => {
    const p = data.portraits[key];
    return `<span class="portrait" style="--position:${escapeHTML(p.position)};--zoom:${p.zoom};--origin:${escapeHTML(p.origin || "50% 50%")}"><img src="../shared/${escapeHTML(p.file)}" alt="${escapeHTML(p.name)}的剧中角色照"></span>`;
  };
  let selected = 'wendy';
  let phase = data.phases[0];
  const renderPerson = () => {
    const p = data.portraits[selected];
    const c = data.characters[selected];
    document.getElementById('person-detail').innerHTML = `<div class="detail-heading">${portrait(selected)}<div><h3>${escapeHTML(p.name)}</h3><small>${escapeHTML(p.en)}</small></div></div><p class="detail-role">${escapeHTML(c.role)}</p><h4>本集行动 · 剧情事实</h4><p>${escapeHTML(c.fact)}</p><h4>人物阅读 · 个人解读</h4><p>${escapeHTML(c.analysis)}</p><div class="phase-detail"><strong>${escapeHTML(phase.name)}</strong><p>${escapeHTML(phase.details[selected])}</p></div><div class="portrait-credit">${escapeHTML(p.actor)} 饰 · 统一剧中角色照</div>`;
    document.querySelectorAll('[data-person]').forEach(button => button.setAttribute('aria-pressed', String(button.dataset.person === selected)));
  };
  document.querySelectorAll('[data-person]').forEach(button => button.addEventListener('click', () => {
    selected = button.dataset.person;
    renderPerson();
  }));
  document.querySelectorAll('[data-phase]').forEach(button => button.addEventListener('click', () => {
    phase = data.phases.find(item => item.id === button.dataset.phase);
    document.querySelectorAll('[data-phase]').forEach(tab => tab.setAttribute('aria-pressed', String(tab === button)));
    phase.edges.forEach((label, index) => { document.getElementById(`edge-${index}`).textContent = label; });
    document.getElementById('graph-note').textContent = phase.note;
    renderPerson();
  }));
  const renderFlow = flow => {
    const nodes = flow.nodes.map((node, index) => {
      const face = node.portrait ? portrait(node.portrait) : `<span class="flow-number">${String(index + 1).padStart(2, '0')}</span>`;
      return `<a class="flow-node" href="#scene-${escapeHTML(node.scene)}">${face}<span><strong>${escapeHTML(node.name)}</strong><small>${escapeHTML(node.role)}</small></span></a>`;
    }).join('');
    document.getElementById('flow-content').innerHTML = `<div class="flow-heading"><h3>${escapeHTML(flow.title)}</h3><p>${escapeHTML(flow.intro)}</p></div><div class="flow-nodes">${nodes}</div><p class="flow-result">${escapeHTML(flow.result)}</p>`;
  };
  document.querySelectorAll('[data-flow]').forEach(button => button.addEventListener('click', () => {
    document.querySelectorAll('[data-flow]').forEach(tab => tab.setAttribute('aria-pressed', String(tab === button)));
    renderFlow(data.flows.find(flow => flow.id === button.dataset.flow));
  }));
  let quoteIndex = 0;
  const renderQuote = () => {
    const q = data.quotes[quoteIndex];
    const picture = images[q.image];
    const image = document.getElementById('quote-image');
    image.src = picture.file;
    image.alt = picture.alt;
    image.width = picture.width;
    image.height = picture.height;
    document.getElementById('quote-image-caption').textContent = picture.caption;
    document.getElementById('quote-note').innerHTML = `<div class="speaker">${escapeHTML(q.speaker)}</div><blockquote lang="en">${escapeHTML(q.en)}</blockquote><p class="translation">${escapeHTML(q.zh)}</p><h4>这句话发生在哪里</h4><p>${escapeHTML(q.context)}</p><div class="quote-reading"><h4>潜台词 · 个人解读</h4><p>${escapeHTML(q.analysis)}</p></div>`;
    document.getElementById('quote-count').textContent = `${String(quoteIndex + 1).padStart(2, '0')} / ${String(data.quotes.length).padStart(2, '0')}`;
  };
  document.getElementById('quote-prev').addEventListener('click', () => {
    quoteIndex = (quoteIndex - 1 + data.quotes.length) % data.quotes.length;
    renderQuote();
  });
  document.getElementById('quote-next').addEventListener('click', () => {
    quoteIndex = (quoteIndex + 1) % data.quotes.length;
    renderQuote();
  });
  const lightbox = document.getElementById('image-lightbox');
  document.querySelectorAll('[data-image]').forEach(button => button.addEventListener('click', () => {
    const picture = images[button.dataset.image];
    const image = document.getElementById('lightbox-image');
    image.src = picture.file;
    image.alt = picture.alt;
    document.getElementById('lightbox-caption').textContent = picture.caption;
    lightbox.showModal();
  }));
  lightbox.querySelector('button').addEventListener('click', () => lightbox.close());
  lightbox.addEventListener('click', event => { if (event.target === lightbox) lightbox.close(); });
  const revealSource = hash => {
    if (!hash.startsWith('#source-')) return;
    document.getElementById('source-details').open = true;
  };
  document.addEventListener('click', event => {
    const link = event.target.closest('a[href^="#source-"]');
    if (link) revealSource(link.hash);
  });
  window.addEventListener('hashchange', () => revealSource(window.location.hash));
  revealSource(window.location.hash);
  const navLinks = [...document.querySelectorAll('.masthead nav a')];
  const observer = new IntersectionObserver(entries => {
    entries.forEach(entry => {
      if (!entry.isIntersecting) return;
      navLinks.forEach(link => {
        const active = link.hash === `#${entry.target.id}`;
        link.classList.toggle('active', active);
        if (active) link.setAttribute('aria-current', 'location');
        else link.removeAttribute('aria-current');
      });
    });
  }, {rootMargin:'-15% 0px -65% 0px'});
  navLinks.forEach(link => { const section = document.querySelector(link.hash); if (section) observer.observe(section); });
  const progress = document.getElementById('reading-progress');
  const updateProgress = () => {
    const total = document.documentElement.scrollHeight - window.innerHeight;
    progress.style.width = `${total > 0 ? Math.min(100, Math.max(0, window.scrollY / total * 100)) : 0}%`;
  };
  window.addEventListener('scroll', updateProgress, {passive:true});
  window.addEventListener('resize', updateProgress);
  updateProgress();
})();
