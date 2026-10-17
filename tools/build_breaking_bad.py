#!/usr/bin/env python3
"""Render all seven Breaking Bad season-one episode guides and their catalogue."""
import argparse
import hashlib
import json
from html import escape
from pathlib import Path
from string import Template

ROOT = Path(__file__).resolve().parents[1]
SHOW = ROOT / 'series/breaking-bad'
TITLES = ['Pilot', "Cat's in the Bag...", "...and the Bag's in the River", 'Cancer Man', 'Gray Matter', "Crazy Handful of Nothin'", 'A No-Rough-Stuff-Type Deal']


def build_episode(number):
    from PIL import Image
    EPISODE = SHOW / f's01e{number:02}'
    source = EPISODE / 'content.json'
    data = json.loads(source.read_text())
    registry = json.loads((SHOW / 'shared/portraits.json').read_text())['characters']
    portraits = {key: registry[key] for key in data['characters']}
    images = {p['id']: p for p in data['images']}
    sources = {s['id']: s for s in data['sources']}
    e = lambda value: escape(str(value), quote=True)
    assert data['version'] == 1 and data['episode'] == f'S01E{number:02}' and data['title'] == TITLES[number - 1]
    assert len(data['scenes']) == len({s['id'] for s in data['scenes']}) == 12
    assert len(images) == len(data['images']) and len(sources) == len(data['sources'])
    assert set(portraits) == set(data['characters']) and 5 <= len(portraits) <= 9
    assert len(data['phases']) == len(data['quotes']) == 3
    assert len(data['conflicts']) == 4 and len(data['motifs']) == 6
    words = sum(len(q['en'].split()) for q in data['quotes'])
    assert words <= 25
    for act in data['acts']:
        assert sum(s['act'] == act['id'] for s in data['scenes']) == 4
    for s in data['scenes']:
        assert all(s[k] for k in ['fact', 'analysis', 'turn', 'sources'])
        assert s['image'] in images and all(k in sources for k in s['sources'])
    for phase in data['phases']:
        assert set(phase['details']) == set(portraits) and len(phase['edges']) == 6
    for item in data['images']:
        path = (EPISODE / item['file']).resolve()
        assert path.is_relative_to(EPISODE / 'assets') and path.is_file()
        assert item['episode'] == data['episode'] and item['kind'] in ['episode-still', 'episode-production-still']
        assert item['caption'] and item['alt']
        assert all(item[k].startswith('https://') for k in ['sourceUrl', 'originalUrl'])
        with Image.open(path) as picture:
            assert picture.size == (item['width'], item['height'])
    for person in portraits.values():
        path = (SHOW / 'shared' / person['file']).resolve()
        assert path.is_relative_to(SHOW / 'shared/portraits') and path.is_file()
        assert person['actor'] and int(person['episode'][-2:]) <= number
        assert person['kind'] == 'character-still'
        assert all(person[k].startswith('https://') for k in ['sourceUrl', 'originalUrl'])
        with Image.open(path) as picture:
            picture.verify()
    assert all(x['image'] in images for x in data['conflicts'] + data['quotes'])

    def image_tag(key, lazy=True, attrs=''):
        p = images[key]
        loading = ' loading="lazy"' if lazy else ' fetchpriority="high"'
        return f'<img src="{e(p["file"])}" alt="{e(p["alt"])}" width="{p["width"]}" height="{p["height"]}"{loading}{attrs}>'

    def photo(key):
        return image_tag(key) + f'<figcaption>{e(images[key]["caption"])}</figcaption>'

    def avatar(key):
        p = portraits[key]
        return f'<span class="portrait"><img src="../shared/{e(p["file"])}" alt="{e(p["name"])}的剧中角色照" width="128" height="128" loading="lazy"></span>'

    def person_detail(key):
        p, c = portraits[key], data['characters'][key]
        return f'<div class="detail-heading">{avatar(key)}<div><h3>{e(p["name"])}</h3><small>{e(p["en"])}</small></div></div><p class="detail-role">{e(c["role"])}</p><h4>想要什么 · 人物阅读</h4><p>{e(c["want"])}</p><h4>手中有什么</h4><p>{e(c["leverage"])}</p><h4>本集行动 · 剧情事实</h4><p>{e(c["fact"])}</p><h4>冲突位置 · 个人解读</h4><p>{e(c["analysis"])}</p><div class="phase-detail"><strong>{e(data["phases"][0]["name"])}</strong><p>{e(data["phases"][0]["details"][key])}</p></div><div class="portrait-credit">{e(p["actor"])} 饰 · {e(p["credit"])}</div>'

    def conflict_html(c):
        return f'<figure class="conflict-photo">{photo(c["image"])}</figure><article class="conflict-copy"><div class="conflict-axis"><span>{e(c["left"])}</span><b>×</b><span>{e(c["right"])}</span></div><h3>{e(c["title"])}</h3><p>{e(c["text"])}</p><p>{e(c["second"])}</p><p class="fact-boundary">{e(c["limit"])}</p></article>'

    def quote_html(q):
        return f'<div class="speaker">{e(q["speaker"])}</div><blockquote lang="en">{e(q["en"])}</blockquote><p class="translation">{e(q["zh"])}<small>中文自译</small></p><h4>这句话发生在哪里</h4><p>{e(q["context"])}</p><h4>没有说透的部分 · 个人解读</h4><p>{e(q["analysis"])}</p>'

    acts = ''
    for act in data['acts']:
        scenes = ''
        for index, s in enumerate(data['scenes'], 1):
            if s['act'] != act['id']:
                continue
            refs = ''.join(f'<a class="ref" href="#source-{e(key)}" aria-label="查看第{list(sources).index(key)+1}项依据">[{list(sources).index(key)+1}]</a>' for key in s['sources'])
            scenes += f'<article class="scene" id="scene-{e(s["id"])}"><div class="scene-top"><span class="scene-number">{index:02}</span><div><small>{e(s["where"])}</small><h4>{e(s["title"])}</h4></div></div><figure class="scene-photo">{photo(s["image"])}<button class="zoom-photo" data-image="{e(s["image"])}" aria-label="查看第{index}个节点的完整剧照">↗</button></figure><p class="scene-fact"><span>剧情事实</span>{e(s["fact"])} {refs}</p><details class="scene-analysis" open><summary>这一场为什么重要 · 个人解读</summary><p>{e(s["analysis"])}</p></details><p class="scene-turn"><span>因此 →</span>{e(s["turn"])}</p></article>'
        acts += f'<section class="act" id="act-{e(act["id"])}"><div class="act-heading"><span class="act-roman">{e(act["number"])}</span><div><h3>{e(act["title"])}</h3><p>{e(act["deck"])}</p></div><small>{e(act["range"])}</small></div><div class="scene-grid">{scenes}</div><div class="act-summary"><strong>这一幕推进了什么</strong><p>{e(act["summary"])}</p></div></section>'
    default_positions = {'walt': (45, 50), 'skyler': (15, 23), 'junior': (15, 76), 'hank': (45, 14), 'marie': (78, 14), 'jesse': (78, 50), 'krazy8': (63, 85), 'emilio': (88, 85)}
    default_labels = {'walt': '责任 / 自尊', 'skyler': '家庭 / 知情', 'junior': '少年 / 尊严', 'hank': '执法 / 力量', 'marie': '关心 / 评议', 'jesse': '经验 / 搭档', 'krazy8': '渠道 / 风险', 'emilio': '怀疑 / 目击'}
    positions = data.get('graph', {}).get('positions', default_positions)
    labels = data.get('graph', {}).get('labels', default_labels)
    assert set(positions) == set(portraits) == set(labels)
    people = ''.join(f'<button class="node {key}" data-person="{key}" style="left:{x}%;top:{y}%" aria-pressed="{str(key == "walt").lower()}" aria-label="查看{e(portraits[key]["name"])}的本集档案">{avatar(key)}<strong>{e(portraits[key]["name"])}</strong><small>{labels[key]}</small></button>' for key, (x, y) in positions.items())
    default_pairs = ['沃尔特 — 斯凯勒', '沃尔特 — 小沃尔特', '沃尔特 — 汉克', '沃尔特 — 杰西', '搭档 — 经销者', '斯凯勒 — 玛丽']
    pairs = data.get('edgePairs', default_pairs)
    assert len(pairs) == 6
    edge_readout = ''.join(f'<div><strong>{pair}</strong><span id="edge-{i}">{e(data["phases"][0]["edges"][i])}</span></div>' for i, pair in enumerate(pairs))
    values = dict(intro=e(data['intro']), spoiler=e(data['spoiler']), acts=acts, people=people, edge_readout=edge_readout, initial_person=person_detail('walt'), initial_conflict=conflict_html(data['conflicts'][0]), initial_quote=quote_html(data['quotes'][0]), quote_words=words, graph_note=e(data['phases'][0]['note']))
    values['phase_tabs'] = ''.join(f'<button data-phase="{p["id"]}" aria-pressed="{str(i == 0).lower()}">{e(p["name"])}</button>' for i, p in enumerate(data['phases']))
    values['conflict_tabs'] = ''.join(f'<button data-conflict="{c["id"]}" aria-pressed="{str(i == 0).lower()}">{e(c["label"])}</button>' for i, c in enumerate(data['conflicts']))
    for field in ['title', 'fact', 'analysis']:
        values['prologue_' + field] = e(data['prologue'][field])
    for key in (['prologue', 'classroom', 'cook'] if number == 1 else ['prologue']):
        values[key + '_photo'] = photo(key)
    values['hero_image'] = image_tag('hero', lazy=False, attrs=' class="hero-image"')
    q = images[data['quotes'][0]['image']]
    values['quote_photo'] = image_tag(q['id'], attrs=' id="quote-image"') + f'<figcaption id="quote-caption">{e(q["caption"])}</figcaption>'
    values['lightbox_src'], values['lightbox_alt'] = e(images['prologue']['file']), e(images['prologue']['alt'])
    values['motifs'] = ''.join(f'<article class="motif"><span class="motif-number">{e(m["number"])}</span><h3>{e(m["title"])}</h3><p>{e(m["text"])}</p><a href="#scene-{e(m["link"])}">回到相关场景 ↗</a></article>' for m in data['motifs'])
    values['source_list'] = ''.join(f'<li id="source-{e(s["id"])}"><a href="{e(s["url"])}" target="_blank" rel="noopener">{e(s["title"])} ↗</a><span>{e(s["note"])}</span></li>' for s in data['sources'])
    values['image_list'] = ''.join(f'<li>{e(p["caption"])} · <a href="{e(p["originalUrl"])}" target="_blank" rel="noopener">原图</a> / <a href="{e(p["sourceUrl"])}" target="_blank" rel="noopener">源页</a></li>' for p in {item['file']: item for item in data['images']}.values())
    values['portrait_list'] = ''.join(f'<li>{e(p["name"])} · {e(p["actor"])} 饰 · {e(p["credit"])} · <a href="{e(p["originalUrl"])}" target="_blank" rel="noopener">原图</a> / <a href="{e(p["sourceUrl"])}" target="_blank" rel="noopener">源页</a></li>' for p in portraits.values())
    payload = dict(data, portraits=portraits, sourceHash=hashlib.sha256(source.read_bytes()).hexdigest())
    values['payload'] = json.dumps(payload, ensure_ascii=False).replace('<', '\\u003c')
    values['no_script_reading'] = '<noscript><section class="no-script wrap"><div class="eyebrow">READING CONTINUES / 未启用脚本时的完整阅读</div><h3>人物档案、其余冲突与台词</h3><div class="no-script-cast">' + ''.join(f'<article class="person-detail">{person_detail(key)}</article>' for key in portraits) + '</div>' + ''.join(f'<div class="conflict-layout">{conflict_html(c)}</div>' for c in data['conflicts'][1:]) + ''.join(f'<div class="quote-layout"><figure class="quote-photo">{photo(q["image"])}</figure><div class="quote-copy">{quote_html(q)}</div></div>' for q in data['quotes'][1:]) + '<h3>三阶段关系记录</h3>' + ''.join(f'<h4>{e(p["name"])}</h4><p>{e(p["note"])}</p><ul>' + ''.join(f'<li>{e(portraits[key]["name"])}：{e(text)}</li>' for key, text in p['details'].items()) + '</ul>' for p in data['phases']) + '</section></noscript>'
    navigation = episode_navigation(number)
    values['episode_navigation'] = navigation
    if number > 1:
        page = data['page']
        for key, text in page.items():
            if isinstance(text, str):
                values['page_' + key] = e(text).replace('|', '<br>')
        values.update(episode=e(data['episode']), episode_number=f'{number:02}', episode_title=e(data['title']), airdate=e(data['airdate']), character_count=len(portraits), hero_caption=e(images['hero']['caption']), initial_phase=e(data['phases'][0]['id']))
        values['chapter_nav'] = ''.join(f'<a href="#act-{e(act["id"])}"><b>{e(act["number"])}</b><span><strong>{e(act["title"])}</strong><small>{e(act["deck"])}</small></span><em>{e(act["range"])} ↘</em></a>' for act in data['acts'])
        pair = page['framePair']
        values['pair_left'], values['pair_right'] = photo(pair['left']), photo(pair['right'])
        values['pair_title'], values['pair_text'] = e(pair['title']), e(pair['text'])
        values['ending_paragraphs'] = ''.join(f'<p>{e(text)}</p>' for text in page['endingParagraphs'])
        values['graph_svg'] = ''.join(f'<line class="{e(edge[2])}-line" x1="{positions[edge[0]][0] * 10}" y1="{positions[edge[0]][1] * 7}" x2="{positions[edge[1]][0] * 10}" y2="{positions[edge[1]][1] * 7}"/>' for edge in data['graph']['edges'])
    template = 'episode.html' if number == 1 else 'season-episode.html'
    rendered = Template((SHOW / 'shared' / template).read_text()).substitute(values)
    assert rendered.count('<details class="scene-analysis" open>') == 12
    (EPISODE / 'index.html').write_text(rendered)
    print(f'Rendered {data["episode"]}: 12 scenes, {len(images)} images, {len(portraits)} characters, {words} quoted words')


def episode_navigation(number):
    items = []
    if number > 1:
        items.append(f'<a href="../s01e{number - 1:02}/">← 上一集 <span>{escape(TITLES[number - 2])}</span></a>')
    else:
        items.append('<span>第一季的开始</span>')
    items.append('<a href="../">第一季 · 七集目录 ↗</a>')
    if number < 7:
        items.append(f'<a href="../s01e{number + 1:02}/">下一集 → <span>{escape(TITLES[number])}</span></a>')
    else:
        items.append('<span>第一季完 · 本页止于 S01E07</span>')
    return '<nav class="episode-navigation wrap" aria-label="逐集阅读">' + ''.join(items) + '</nav>'


def build_catalogue():
    entries = []
    for number, title in enumerate(TITLES, 1):
        folder = SHOW / f's01e{number:02}'
        data = json.loads((folder / 'content.json').read_text())
        hero = next(item for item in data['images'] if item['id'] == 'hero')
        entries.append(dict(number=number,episode=data['episode'],title=title,question=data['question'],deck=data.get('page',{}).get('catalogueDeck',data['intro']),hero=hero,sceneCount=len(data['scenes']),characterCount=len(data['characters']),conflictCount=len(data['conflicts'])))
    metadata = dict(season=1,complete=True,episodeCount=7,episodes=entries)
    (SHOW / 'season.json').write_text(json.dumps(metadata,ensure_ascii=False,indent=2)+'\n')
    e = lambda value: escape(str(value), quote=True)
    topics = ['病与尊严 / 知识与金钱', '分工 / 秘密', '求生 / 道德', '家庭 / 信任', '援助 / 自主', '威慑 / 野心', '承诺 / 暴力']
    labels = ['起点', '分工', '抉择', '家人', '援助', '威慑', '规则']
    cards = {}
    for item in entries:
        number, hero = item['number'], item['hero']
        href = f's01e{number:02}/'
        featured = ' is-featured' if number == 1 else ''
        question = e(item['question']).replace('，', '，<br>', 1)
        photo_label = '<span class="frame-kind">本集宣传剧照</span>' if hero['kind'] == 'episode-production-still' else ''
        cards[number] = f'''<article class="season-card{featured}" id="episode-{number:02}">
  <a class="season-photo" href="{href}" target="_blank" rel="noopener" aria-label="打开第 {number} 集图文解读">
    <img src="{href}{e(hero['file'])}" alt="{e(hero['alt'])}" width="{hero['width']}" height="{hero['height']}" loading="lazy">
    <span class="frame-number" aria-hidden="true">{number:02}</span>{photo_label}<span class="frame-arrow" aria-hidden="true">↗</span>
  </a>
  <div class="season-copy">
    <div class="episode-original"><span>S01 / E{number:02}</span><span lang="en">{e(item['title'])}</span></div>
    <h3>{question}</h3>
    <p class="episode-deck">{e(item['deck'])}</p>
    <div class="episode-topics">{topics[number - 1]}</div>
    <div class="episode-bottom"><a class="season-read" href="{href}" target="_blank" rel="noopener">打开本集图解 <span>↗</span></a><small>剧透截至 S01E{number:02}</small></div>
  </div>
</article>'''
    sections = [
        ('I', '01—03 / THE FIRST STEP', '越界，从来不是一个瞬间。', '诊断之后，是搭档、秘密，和必须面对的人。<br>第一次冒险结束了，后果才刚刚开始。', [1, 2, 3]),
        ('II', '04—05 / INSIDE THE FAMILY', '家人越靠近，秘密越沉重。', '关心能否抵达一个拒绝被帮助的人？<br>选择权、旧日信任与自尊，在家中发生碰撞。', [4, 5]),
        ('III', '06—07 / A DIFFERENT KIND OF POWER', '当恐惧，成了一种力量。', '他开始发现自己能让人害怕。<br>可威慑奏效之后，危险真的减少了吗？', [6, 7]),
    ]
    groups = ''.join(f'''<section class="archive-group" aria-labelledby="group-{roman}"><div class="group-heading"><span class="group-number" aria-hidden="true">{roman}</span><div><div class="eyebrow">{e(kicker)}</div><h2 id="group-{roman}">{e(title)}</h2></div><p>{deck}</p></div><div class="season-grid">{''.join(cards[number] for number in numbers)}</div></section>''' for roman, kicker, title, deck, numbers in sections)
    jump_links = ''.join(f'<a href="#episode-{number:02}"><b>{number:02}</b><span>{label}</span></a>' for number, label in enumerate(labels, 1))
    pilot = json.loads((SHOW / 's01e01/content.json').read_text())
    cover = next(item for item in pilot['images'] if item['id'] == 'home')
    hero_image = f'<img class="cover-image" src="s01e01/{e(cover["file"])}" alt="{e(cover["alt"])}" width="{cover["width"]}" height="{cover["height"]}" fetchpriority="high">'
    registry = json.loads((SHOW / 'shared/portraits.json').read_text())['characters']
    relationships = [
        ('jesse', '搭档 / 不对等的需要', '沃尔特 × 杰西', '化学知识与街头经验相互需要，风险与代价却并不对等。一起越界，能不能让他们真正站到同一边？', 2),
        ('skyler', '家庭 / 被留在秘密之外', '沃尔特 × 斯凯勒', '他把秘密叫作保护，她只能在缺失的信息里追问。对家人的责任，是否也包括让对方知道真相？', 5),
        ('hank', '亲缘 / 调查的另一面', '沃尔特 × 汉克', '饭桌上的亲人，工作中的调查者。同一件事，在两个男人那里有两套叙述，距离也悄悄发生变化。', 6),
    ]
    def portrait(key):
        person = registry[key]
        return f'<img src="shared/{e(person["file"])}" alt="{e(person["name"])}的剧中角色照" width="128" height="128" loading="lazy">'
    relationship_cards = ''.join(f'<article class="relationship-card"><div class="portrait-pair">{portrait("walt")}<span aria-hidden="true"></span>{portrait(key)}</div><p class="relation-label">{e(label)}</p><h3>{e(title)}</h3><p>{e(copy)}</p><a href="s01e{number:02}/#relations" target="_blank" rel="noopener">从第 {number} 集关系图读起 <span>↗</span></a></article>' for key, label, title, copy, number in relationships)
    image_sources = f'<li>封面 · 第 1 集公路持枪镜头：<a href="{e(cover["sourceUrl"])}" target="_blank" rel="noopener">图像出处 ↗</a></li>'
    for item in entries:
        image = item['hero']
        kind = '本集宣传剧照' if image['kind'] == 'episode-production-still' else '本集截图'
        image_sources += f'<li>第 {item["number"]} 集 · {kind}：<a href="{e(image["sourceUrl"])}" target="_blank" rel="noopener">图像出处 ↗</a></li>'
    for key in ['walt', 'jesse', 'skyler', 'hank']:
        person = registry[key]
        image_sources += f'<li>{e(person["name"])} · {e(person["actor"])} 饰：<a href="{e(person["sourceUrl"])}" target="_blank" rel="noopener">角色照出处 ↗</a></li>'
    template = Template((SHOW / 'shared/season-catalogue.html').read_text())
    html = template.substitute(hero_image=hero_image, hero_source=e(cover['sourceUrl']), groups=groups, jump_links=jump_links, relationship_cards=relationship_cards, image_sources=image_sources)
    (SHOW / 'index.html').write_text(html.rstrip()+'\n')
    print('Rendered season catalogue: all seven episodes visible')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--episode',type=int,choices=range(1,8))
    parser.add_argument('--complete',action='store_true',help='Require all seven editorial sources (default).')
    args = parser.parse_args()
    for number in ([args.episode] if args.episode else range(1,8)):
        build_episode(number)
    build_catalogue()


if __name__ == '__main__':
    main()
