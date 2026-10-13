const data = JSON.parse(document.querySelector('#episode-data').textContent);
const escapeHTML = value => String(value).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const sources = new Map(data.sources.map((source, i) => [source.id, i + 1]));
const imageInfo = new Map(data.images.map(item => [item.file, item]));
const ref = id => `<a class="ref" href="#source-${escapeHTML(id)}">[${sources.get(id)}]</a>`;
document.querySelectorAll('[data-order]').forEach(button => button.addEventListener('click', () => {
  document.querySelectorAll('[data-order]').forEach(item => { const selected = item === button; item.classList.toggle('active', selected); item.setAttribute('aria-pressed', String(selected)); });
  const cards = [...document.querySelectorAll('.scene-card')];
  cards.sort((a, b) => Number(a.dataset[button.dataset.order === 'time' ? 'time' : 'screen']) - Number(b.dataset[button.dataset.order === 'time' ? 'time' : 'screen']));
  cards.forEach((card, index) => { card.querySelector('.scene-num').textContent = String(index + 1).padStart(2, '0'); document.querySelector('#timeline').append(card); });
  document.querySelector('#order-note').textContent = button.dataset.order === 'time' ? '按本集事件的大致先后排列；回忆场景归入其发生的时间。' : '按剧中叙事顺序排列。展开批注，阅读场景的意义。';
}));

const points = new Map(data.characters.map((character, i) => {
  const angle = -Math.PI / 2 + i * Math.PI * 2 / data.characters.length;
  return [character.id, {x: 350 + 232 * Math.cos(angle), y: 252 + 166 * Math.sin(angle)}];
}));
const people = new Map(data.characters.map(character => [character.id, character]));
let phase = 0;
let selectedPerson = data.characters[0].id;
let selectedRelation = null;
const panel = document.querySelector('#person-detail');
document.querySelectorAll('[data-person]').forEach(button => {
  const point = points.get(button.dataset.person);
  button.style.left = `${point.x / 7}%`;
  button.style.top = `${point.y / 5.1}%`;
  button.addEventListener('click', () => { selectedPerson = button.dataset.person; selectedRelation = null; renderGraph(); });
});
function renderGraph() {
  const active = data.relationships.map((relation, index) => ({relation, index})).filter(item => item.relation.phases.includes(phase));
  document.querySelector('.graph-lines').innerHTML = active.map(({relation, index}) => {
    const a = points.get(relation.from), b = points.get(relation.to);
    const highlight = selectedRelation === index || (selectedRelation === null && [relation.from, relation.to].includes(selectedPerson));
    const kind = ['care','trust','peer'].includes(relation.type) ? 'trust' : ['conflict','tension','loss'].includes(relation.type) ? 'conflict' : 'command';
    return `<path d="M${a.x} ${a.y} L${b.x} ${b.y}" class="${kind} ${highlight ? 'highlighted' : 'subdued'}"/>`;
  }).join('');
  document.querySelectorAll('[data-person]').forEach(button => { const selected = selectedRelation === null && button.dataset.person === selectedPerson; button.classList.toggle('selected', selected); button.setAttribute('aria-pressed', String(selected)); });
  document.querySelector('#graph-note').textContent = data.phases[phase].note;
  const options = document.querySelector('#relation-options');
  options.innerHTML = active.map(({relation, index}) => `<button data-relation="${index}" class="${selectedRelation === index ? 'active' : ''}" aria-pressed="${selectedRelation === index}">${escapeHTML(people.get(relation.from).name)} ↔ ${escapeHTML(people.get(relation.to).name)}<small>${escapeHTML(relation.label)}</small></button>`).join('');
  options.querySelectorAll('button').forEach(button => button.addEventListener('click', () => { selectedRelation = Number(button.dataset.relation); renderGraph(); }));
  if (selectedRelation !== null) {
    const relation = data.relationships[selectedRelation];
    panel.innerHTML = `<div class="detail-kicker">RELATIONSHIP / 关系档案</div><h3>${escapeHTML(relation.label)}</h3><p class="detail-role">${escapeHTML(people.get(relation.from).name)} ↔ ${escapeHTML(people.get(relation.to).name)}</p><h4>具体证据 · 剧情事实</h4><p>${escapeHTML(relation.fact)}${ref(relation.source)}</p><div class="detail-reading"><span>怎样理解 · 个人解读</span><p>${escapeHTML(relation.analysis)}</p></div>`;
  } else {
    const person = people.get(selectedPerson);
    const connected = active.filter(({relation}) => [relation.from,relation.to].includes(selectedPerson));
    panel.innerHTML = `<div class="detail-kicker">PERSONNEL FILE / 人物档案</div><h3>${escapeHTML(person.name)}</h3><div class="person-en">${escapeHTML(person.en)}</div><p class="detail-role">${escapeHTML(person.role)}</p><h4>截至本集 · 剧情事实</h4><p>${escapeHTML(person.fact)}${ref(person.source)}</p><div class="detail-reading"><span>人物阅读 · 个人解读</span><p>${escapeHTML(person.analysis)}</p></div><div class="connected-note">这一阶段关联：${connected.map(({relation})=>escapeHTML(relation.label)).join(' / ') || '尚无本页记录的直接关系'}</div>`;
  }
}
document.querySelectorAll('[data-phase]').forEach(button => button.addEventListener('click', () => {
  phase = Number(button.dataset.phase); selectedRelation = null;
  document.querySelectorAll('[data-phase]').forEach(item => { const selected = item === button; item.classList.toggle('active', selected); item.setAttribute('aria-pressed', String(selected)); });
  renderGraph();
}));
renderGraph();

let quoteIndex = 0;
function renderQuote() {
  const quote = data.quotes[quoteIndex], image = imageInfo.get(quote.image);
  const picture = document.querySelector('#quote-image');
  picture.src = quote.image; picture.alt = image.alt;
  document.querySelector('#quote-count').textContent = `${String(quoteIndex + 1).padStart(2,'0')} / ${String(data.quotes.length).padStart(2,'0')}`;
  document.querySelector('#quote-scene').textContent = `台词场景 / ${quote.scene} · 配图：${image.caption}`;
  document.querySelector('#quote-note').innerHTML = `<div class="quote-speaker">${escapeHTML(quote.speaker)} · 第 ${data.episode} 集</div><blockquote lang="en">“${escapeHTML(quote.en)}”</blockquote><p class="translation">${escapeHTML(quote.zh)}</p><h4>发生在什么情境</h4><p>${escapeHTML(quote.context)}${ref(quote.source)}</p><div class="quote-reading"><h4>放回上下文 · 个人解读</h4><p>${escapeHTML(quote.analysis)}</p></div>`;
}
document.querySelector('#quote-prev').addEventListener('click', () => { quoteIndex = (quoteIndex + data.quotes.length - 1) % data.quotes.length; renderQuote(); });
document.querySelector('#quote-next').addEventListener('click', () => { quoteIndex = (quoteIndex + 1) % data.quotes.length; renderQuote(); });
renderQuote();
let scheduled = false;
function updateProgress(){const distance = document.documentElement.scrollHeight - innerHeight; document.querySelector('#progress').style.width = `${distance > 0 ? Math.min(100, scrollY/distance*100) : 0}%`;}
addEventListener('scroll', () => {if(!scheduled){scheduled=true;requestAnimationFrame(()=>{updateProgress();scheduled=false;});}},{passive:true});
addEventListener('resize', updateProgress); updateProgress();
