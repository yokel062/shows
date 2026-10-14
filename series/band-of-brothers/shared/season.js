const escapeHTML = value => String(value).replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const records = [
  {episode:1,title:'Currahee',headline:'一群人，怎样成为一支连队。',hero:'s01e01/assets/company.jpg',alt:'第1集E连士兵在营房前列队'},
  /* EPISODE_RECORDS_START */
  {"episode": 2, "title": "Day of Days", "headline": "当队形消失，谁能让一群人重新成为连队？", "hero": "s01e02/assets/battle.jpg", "alt": "温特斯戴着伪装网钢盔伏在沙袋旁，脸上沾满泥土，正朝侧方呼喊"},
  {"episode": 3, "title": "Carentan", "headline": "勇气可以被唤醒，生还却不能被保证", "hero": "s01e03/assets/hero.jpg", "alt": "两名戴网罩头盔的 E 连士兵伏在地面操作巴祖卡火箭筒"},
  {"episode": 4, "title": "Replacements", "headline": "从被照顾的人，到愿意回头寻找战友的人", "hero": "s01e04/assets/hero.jpg", "alt": "戴网罩头盔、咬着雪茄的兰德尔曼近景，肩上可见空降师标识"},
  {"episode": 5, "title": "Crossroads", "headline": "战斗结束了，报告与记忆却没有同时结束", "hero": "s01e05/assets/running.jpg", "alt": "荷兰堤坝旁，数名 E 连士兵持枪从开阔地冲向前方"},
  {"episode": 6, "title": "Bastogne", "headline": "守住阵地，也守住一个人", "hero": "s01e06/assets/hero.jpg", "alt": "雪落在罗的头发和军服上，他坐在林间，左臂戴着红十字袖章。"},
  {"episode": 7, "title": "The Breaking Point", "headline": "谁把一支快要散架的连队，重新带向前方？", "hero": "s01e07/assets/charge.jpg", "alt": "斯皮尔斯持冲锋枪在福伊村建筑之间移动，背景为雪地与木屋"},
  {"episode": 8, "title": "The Last Patrol", "headline": "当活着回家终于成为可能，谁来判断下一次冒险是否值得？", "hero": "s01e08/assets/return.jpg", "alt": "冬季阿格诺镇的房屋、光秃树木与驶入街道的军用车辆"},
  {"episode": 9, "title": "Why We Fight", "headline": "越接近胜利，越需要重新回答为何而战", "hero": "s01e09/assets/town.jpg", "alt": "废墟中的德国小镇、清理瓦砾的居民与街头弦乐演奏者"},
  {"episode": 10, "title": "Points", "headline": "战争结束了，他们怎样回到生活里。", "hero": "s01e10/assets/baseball.jpg", "alt": "第十集画面：阿尔卑斯山脚下，E 连士兵在草地上打棒球，一人在垒边滑垒"},
  /* EPISODE_RECORDS_END */
];
function renderCatalogue(){
  document.querySelector('#season-grid').innerHTML = records.map(record => {
    return `<a class="episode-card" href="s01e${String(record.episode).padStart(2,'0')}/" target="_blank" rel="noopener"><div class="episode-cover"><img src="${escapeHTML(record.hero)}" alt="${escapeHTML(record.alt)}" loading="lazy"><span class="cover-label">S01 · E${String(record.episode).padStart(2,'0')}</span></div><div class="episode-card-info"><div class="eyebrow">包含截至第 ${record.episode} 集的剧情</div><h3>${escapeHTML(record.title)}</h3><p>${escapeHTML(record.headline)}</p><span class="card-open">打开第 ${record.episode} 集图解 ↗</span></div></a>`;
  }).join('');
}
renderCatalogue();
