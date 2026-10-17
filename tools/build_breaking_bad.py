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
    cards = ''
    for item in entries:
        number, hero = item['number'], item['hero']
        href = f's01e{number:02}/'
        cards += f'<article class="season-card"><a class="season-photo" href="{href}" target="_blank" rel="noopener"><img src="{href}{e(hero["file"])}" alt="{e(hero["alt"])}" width="{hero["width"]}" height="{hero["height"]}" loading="lazy"><span>FILE {number:02}</span></a><div class="season-copy"><div class="eyebrow">S01 / E{number:02}</div><h2>{e(item["title"])}</h2><h3>{e(item["question"])}</h3><p>{e(item["deck"])}</p><div class="season-stats">12 个剧情节点 · {item["characterCount"]} 位人物 · 4 组冲突</div><a class="season-read" href="{href}" target="_blank" rel="noopener">打开本集档案 <span>↗</span></a><small>剧透截至 S01E{number:02} · 含本集结尾</small></div></article>'
    html = f'''<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="theme-color" content="#102a22"><meta name="description" content="绝命毒师第一季七集图文解读：84 个剧情节点、逐集人物关系、冲突深读和真实剧照。"><title>绝命毒师 · 第一季七集阅读档案 — 剧中人</title><link rel="icon" href="shared/mark.svg" type="image/svg+xml"><link rel="stylesheet" href="shared/episode.css"></head><body><header class="masthead"><a class="brand" href="../../"><b>✦</b>剧中人<small>STORY FIELDNOTES</small></a><a class="episode-id" href="../../">全部作品 ↗</a></header><main><section class="season-hero"><div class="wrap"><div class="eyebrow">BREAKING BAD / THE COMPLETE FIRST SEASON</div><h1>绝命毒师<span>第一季 · 变化的代价</span></h1><p>从一张诊断书，到一笔无法轻松退出的生意。<br>七集、七道问题，跟着人物的每一次选择往前走。</p><div class="season-totals"><span><b>07</b>集完整图解</span><span><b>84</b>个剧情节点</span><span><b>28</b>组人物冲突</span></div></div></section><section class="season-body wrap"><div class="section-heading"><div><div class="eyebrow">SEASON 01 / EPISODE ARCHIVE</div><h2>每一步，都改变了下一步。</h2><p>目录直接展示全部七集的配图与导读；标题和导读会提示本集议题。单集在新标签页打开，各篇只使用截至当集已揭示的信息。</p></div><span class="margin-note">2008.01.20<br>— 2008.03.09</span></div><div class="season-grid">{cards}</div><p class="catalogue-credit">图像均来自剧集截图或明确标注的本集宣传剧照。逐图来源、角色照登记与文字依据见各篇篇末。各集均包含默认展开的剧情解读、三阶段关系图、四组冲突、三段短对白与六处镜头细节。</p><div class="footer-bottom"><a href="../../">← 全部作品</a><span>BREAKING BAD / SEASON ONE COMPLETE</span><a href="https://github.com/yokel062/shows/tree/main/series/breaking-bad">源码与内容 / GitHub ↗</a></div></section></main></body></html>'''
    (SHOW / 'index.html').write_text(html+'\n')
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
