const scenes = [
  {id:'wait',time:7,where:'1944 · 英国 / 出发前',title:'先到战争的门口',image:'briefing.jpg',caption:'本集配图：出征前的任务说明',fact:'天气让行动推迟。Winters 与 Nixon 的交谈把我们带回此前的训练经历。',source:'guide',reading:'开头先让观众感到等待的压力，再回到训练场。于是，接下来每一场看似琐碎的争执，都和即将到来的任务发生了联系。'},
  {id:'inspect',time:1,where:'1942 · 托科阿营',title:'从检查与跑山开始',image:'inspection.jpg',caption:'Perconte 接受检查 · 本集画面',fact:'Sobel 从着装和装备细节挑出问题，取消休假，并安排跑山训练。',source:'leadership',reading:'共同承受压力，使原本陌生的人开始拥有共同经历。但凝聚力的形成，并不能单独证明每一次惩罚都合理。'},
  {id:'spaghetti',time:2,where:'托科阿 · 训练期间',title:'一顿饭，变成一次考验',image:'run.jpg',caption:'跑山画面 · 此处配图展示训练，不是用餐场景',fact:'吃过意大利面后，原定的课堂安排变成跑山。随后，训练继续推进，士兵完成跳伞并获得资格。',source:'script',reading:'用餐时的松弛与紧接着的痛苦构成强烈反差。反复出现的山路，也把训练中的身体记忆变成了连队的共同语言。'},
  {id:'exercise',time:3,where:'美国到英国 · 战术演习',title:'会训练，是否就会指挥？',image:'winters.jpg',caption:'Winters 参加演习 · 本集画面',fact:'Sobel 的现场判断与辨图能力暴露问题。在英国，Luz 模仿 Horton 的声音，诱使他下令剪断围栏；另一边 Winters 调整部署。',source:'script',reading:'训练的标准比较明确，现场情势却不断变化。这一组场景让士兵的抱怨逐渐转变为对作战安全的担忧。'},
  {id:'court',time:4,where:'英国 · 军官冲突',title:'Winters 选择正式审理',image:'dispute.jpg',caption:'Winters 与 Sobel · 本集人物配图，非申请审理场景',fact:'面对关于执行命令时间的指控，Winters 不接受处罚，申请由军事法庭审理。',source:'script',reading:'这可以读作一次克制的抵抗：他没有用私下辱骂回击，而是把争议带进正式程序。这里的重点是他的选择，不能把申请写成已经完成审判。'},
  {id:'nco',time:5,where:'英国 · 士官抗议',title:'不信任，终于成为行动',graphic:'NCO → SINK',graphicSub:'士官联名提出辞去职务 · 风险由他们承担',fact:'士官联名提出辞去职务，拒绝由 Sobel 带领进入实战。Sink 严厉训斥，并对带头者作出处置。',source:'summary',reading:'此前的抱怨还可以藏在玩笑里，这次却必须付出代价。抗议让“对上级的服从”和“对战友安全的责任”正面相撞。'},
  {id:'change',time:6,where:'英国 · 指挥调整',title:'连队得到新的指挥安排',graphic:'SOBEL → MEEHAN',graphicSub:'Sobel 调任跳伞学校 · Meehan 接任连长',fact:'Sink 将 Sobel 调往跳伞训练学校，Meehan 接任 E 连连长。训练继续，连队准备出发。',source:'leadership',reading:'这个安排同时处理了两件事：承认 Sobel 的训练能力，回应连队对实战指挥的担忧。职位变化和士兵的信任变化，在本集并不是完全相同的一条线。'},
  {id:'depart',time:8,where:'1944 · 出征',title:'把训练带上飞机',image:'company.jpg',caption:'本集配图：营房前的 E 连士兵',fact:'Guarnere 从家书得知兄长阵亡。最终，士兵携带装备登机，向诺曼底出发；本集在这里结束。',source:'summary',reading:'私人悲伤和集体任务在出发前相遇。结尾把所有训练场上的问题带进机舱，但没有提前给出实战的答案。'}
];
const sourceIds={guide:'source-guide',script:'source-script',leadership:'source-leadership',summary:'source-summary'};
const sourceNums={guide:1,script:2,leadership:3,summary:4};
const timeline=document.querySelector('#timeline');
function renderTimeline(order){
  const list=order==='time'?[...scenes].sort((a,b)=>a.time-b.time):scenes;
  timeline.innerHTML=list.map((s,i)=>`<article class="scene-card" id="scene-${s.id}"><div class="scene-top"><span class="scene-num">${String(i+1).padStart(2,'0')}</span><div class="scene-location">${s.where}<strong>${s.title}</strong></div></div><div class="scene-picture">${s.image?`<img src="assets/${s.image}" alt="${s.caption}" loading="lazy" width="1200" height="675"><span class="scene-caption">${s.caption}</span>`:`<div class="scene-graphic" role="img" aria-label="${s.graphicSub}"><span class="graphic-icon">${s.graphic}</span><p>${s.graphicSub}</p><small>剧情示意图</small></div>`}</div><p class="scene-fact"><span class="fact-tag">剧情事实</span>${s.fact}<a class="ref" href="#${sourceIds[s.source]}">[${sourceNums[s.source]}]</a></p><details class="scene-analysis" open><summary>这一场为什么重要 · 个人解读</summary><p>${s.reading}</p></details></article>`).join('');
  document.querySelector('#order-note').textContent=order==='time'?'按本集事件的大致先后重排：1942 年开始训练 → 英国演习与指挥调整 → 1944 年出征。':'本集先来到 1944 年的英国，再回望 1942 年开始的训练。';
}
document.querySelectorAll('[data-order]').forEach(b=>b.addEventListener('click',()=>{document.querySelectorAll('[data-order]').forEach(x=>{const on=x===b;x.classList.toggle('active',on);x.setAttribute('aria-pressed',String(on));});renderTimeline(b.dataset.order);}));
renderTimeline('screen');

const people={
  sobel:{name:'索贝尔',en:'HERBERT SOBEL',role:'E 连训练期间的连长',training:['不断提高训练要求，并通过检查和惩罚要求士兵服从。Sink 肯定训练成绩；他对 Winters 的要求，则带有上级对下属的压力。','士兵可以同时承认训练有用，又对他的做法感到不满。'],exercise:['演习失误让士兵怀疑他的现场指挥。他与 Winters 的关系升级为处罚争议，士官也采取集体抗议。','当指挥即将关联生死，单靠职位维持的权威受到更严厉的检验。'],departure:['被 Sink 调往 Chilton Foliat 的跳伞训练学校；Meehan 接任 E 连连长。','调任承认了一种能力，也划出了另一种能力的边界。'],source:'leadership'},
  winters:{name:'温特斯',en:'RICHARD WINTERS',role:'E 连军官 · 本集尚未接任连长',training:['与士兵共同训练；在 Sobel 要求寻找违纪者时，将具体处罚安排给轮到值勤的人。Nixon 是他可以坦率交谈的战友。','他给士兵的印象，是在纪律要求之内保留判断与分寸。'],exercise:['当协同受阻时调整部署。面对 Sobel 的处罚，他申请军法审判，暂时离开原有岗位，令士兵担忧。','他获得的信任，不仅来自温和，也来自能够处理事情。'],departure:['恢复到连队的出征准备中，与 Nixon 等人面对行动前的等待。此时连长是 Meehan。','本集留下的核心变化是威望，而不是把所有指挥权都交到他手中。'],source:'script'},
  sink:{name:'辛克',en:'ROBERT SINK',role:'506 团团长 · 上级指挥官',training:['肯定 E 连成绩并晋升 Sobel，也认可 Winters 的表现。','从上级视角看，训练成果是一项明显可见的成绩。'],exercise:['处理士官集体抗议，严厉维护指挥秩序；同时开始面对连队的不信任问题。','他要处理的不仅是个人恩怨，还包括即将出征的组织能否继续运作。'],departure:['安排 Sobel 调往训练学校，并由 Meehan 接任 E 连连长。','最终调整兼顾训练人员的用途与连队的作战准备。'],source:'summary'},
  easy:{name:'E 连士兵',en:'EASY COMPANY',role:'不同背景的士兵 · 士官是其中的骨干',training:['在跑山、夜间行军和跳伞训练中建立共同经历。共同抱怨之外，也有互相鼓励与日常玩笑。','“我们”开始成为一种身份，但个人差异和内部摩擦仍然存在。'],exercise:['对 Sobel 的指挥信心下降。士官联名提出辞去职务，表达不愿由他率领进入实战。','群像在这里获得主动性：他们开始为谁来指挥自己承担风险。'],departure:['在新的指挥安排下继续准备出征。Guarnere 还带着刚得知的亲人阵亡消息。','同一架飞机上的人，拥有共同任务，也各自携带不同的情绪。'],source:'summary'},
  nixon:{name:'尼克森',en:'LEWIS NIXON',role:'军官 · Winters 的亲近战友',training:['与 Winters 谈论训练、Sobel 和连队生活。两人的相处带有熟悉的玩笑与不同的生活习惯。','他们的对话为紧张的纪律场景留出一个能说真话的空间。'],exercise:['参与军官间对 Sobel 的讨论，也是士兵希望能够帮助 Winters 解决困局的人。','围绕他的期待，反映出 Winters 离开岗位给连队造成的不安。'],departure:['与 Winters 在等待出发时谈起美国城市的日常生活。','轻松的交谈与眼前的军营并置，让观众感到他们也是想念普通生活的人。'],source:'script'}
};
let phase='training',selected='sobel';
const phases={training:{conflict:'上级与下属',easy:'严苛训练',winters:'共同训练',note:'训练阶段 · 上级权威和士兵的信任，正在沿不同路径形成。'},exercise:{conflict:'处罚争议',easy:'拒绝跟随实战',winters:'信任与支持',note:'演习与冲突 · 士官抗议将私下的不满带进正式指挥体系。'},departure:{conflict:'Sobel 调任',easy:'结束直接指挥',winters:'信任继续积累',note:'出征阶段 · Meehan 接任连长；图中虚线表示此前冲突留下的变化。'}};
function renderPerson(){
  const p=people[selected],copy=p[phase];
  const button=document.querySelector(`[data-person="${selected}"]`);
  const avatar=button.querySelector('.character-photo');
  const portrait=avatar?`<div class="portrait-heading"><span class="character-photo detail-portrait" style="${avatar.getAttribute('style')}">${avatar.innerHTML}</span><div><h3>${p.name}</h3><div class="person-en">${p.en}</div><p class="portrait-actor">${button.dataset.actor} 饰</p></div></div>`:`<h3>${p.name}</h3><div class="person-en">${p.en}</div>`;
  document.querySelector('#person-detail').innerHTML=`<div class="detail-kicker">PERSONNEL FILE / 人物档案</div>${portrait}<p class="detail-role">${p.role}</p><h4>这一阶段发生了什么 · 剧情事实</h4><p>${copy[0]}<a class="ref" href="#${sourceIds[p.source]}">[${sourceNums[p.source]}]</a></p><div class="detail-reading"><span>怎样理解这段关系 · 个人解读</span><p>${copy[1]}</p></div>`;
  document.querySelectorAll('[data-person]').forEach(b=>{const active=b.dataset.person===selected;b.classList.toggle('selected',active);b.setAttribute('aria-pressed',String(active));});
}
document.querySelectorAll('[data-phase]').forEach(b=>b.addEventListener('click',()=>{phase=b.dataset.phase;document.querySelectorAll('[data-phase]').forEach(x=>{const active=x===b;x.classList.toggle('active',active);x.setAttribute('aria-pressed',String(active));});const p=phases[phase];document.querySelector('#edge-conflict').textContent=p.conflict;document.querySelector('#edge-easy').textContent=p.easy;document.querySelector('#edge-winters').textContent=p.winters;document.querySelector('#graph-note').textContent=p.note;document.querySelector('#sobel-easy-line').setAttribute('class',phase==='training'?'command':phase==='exercise'?'conflict':'past');renderPerson();}));
document.querySelectorAll('[data-person]').forEach(b=>b.addEventListener('click',()=>{selected=b.dataset.person;renderPerson();}));
renderPerson();

const quotes=[
 {en:'Three miles up, three miles down.',zh:'上山三英里，下山三英里。',speaker:'训练中的反复口号',scene:'跑山口号',image:'run.jpg',context:'跑山贯穿托科阿训练。距离被反复喊出，和连队名称、口号一起成为共同记忆。',reading:'它的力量来自重复。观众听到的既是身体负担，也是一种只要说出口，战友就懂的经历。'},
 {en:'I like spaghetti.',zh:'我喜欢意大利面。',speaker:'Sobel 对 Winters',scene:'安排特殊餐食',image:'sobel.jpg',context:'Sobel 提议安排一顿特殊餐食，随后改变计划，让刚吃完的士兵去跑山。配图为本集检查场景。',reading:'第一次听，像是一点难得的随和；知道随后的安排后，这句话又有了冷峻的反讽。意义来自前后场景的拼接。'},
 {en:'I request trial by court-martial.',zh:'我申请由军事法庭审理。',speaker:'Winters 对 Sobel',scene:'拒绝接受处罚',image:'dispute.jpg',context:'Sobel 给出接受处罚或申请审理的选择，Winters 选择后者。配图为本集人物画面，非这句台词的对应镜头。',reading:'这句话没有激烈的措辞，却改变了权力关系：指控不再只由上级单方面决定，而被要求接受正式检验。'},
 {en:'We stand alone.',zh:'我们独立坚守。',speaker:'训练中的集体口号',scene:'Currahee 的身份含义',image:'company.jpg',context:'剧中用这句话解释 Currahee，并将它变成训练时的集体应答。这里按剧中表达理解，不作语言学考证。',reading:'“独立”可以指任务中的处境；说出“我们”，又让它成为集体的承诺。本集的有趣之处，是独立行动和相互依靠同时存在。'}
];
let quoteIndex=0;
function renderQuote(){const q=quotes[quoteIndex];document.querySelector('#quote-note').innerHTML=`<div class="quote-speaker">${q.speaker} · 第 1 集</div><blockquote lang="en">“${q.en}”</blockquote><p class="translation">${q.zh}</p><h4>发生在什么情境</h4><p>${q.context}</p><div class="quote-reading"><h4>放回上下文 · 个人解读</h4><p>${q.reading}</p></div>`;const img=document.querySelector('#quote-image');img.src=`assets/${q.image}`;img.alt=`台词配图：${q.scene}；具体场景说明见右侧文字`;document.querySelector('#quote-scene').textContent=`台词场景 / ${q.scene}`;document.querySelector('#quote-count').textContent=`${String(quoteIndex+1).padStart(2,'0')} / 04`;}
document.querySelector('#quote-prev').addEventListener('click',()=>{quoteIndex=(quoteIndex+quotes.length-1)%quotes.length;renderQuote();});
document.querySelector('#quote-next').addEventListener('click',()=>{quoteIndex=(quoteIndex+1)%quotes.length;renderQuote();});renderQuote();
function updateProgress(){const length=document.documentElement.scrollHeight-window.innerHeight;document.querySelector('#progress').style.width=`${length>0?Math.min(100,window.scrollY/length*100):0}%`;}
let scrollScheduled=false;window.addEventListener('scroll',()=>{if(!scrollScheduled){scrollScheduled=true;requestAnimationFrame(()=>{updateProgress();scrollScheduled=false;});}},{passive:true});window.addEventListener('resize',updateProgress);updateProgress();
