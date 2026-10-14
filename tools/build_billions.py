#!/usr/bin/env python3
"""Render reviewed Billions episode data and the complete season catalogue."""
import argparse
import json
from collections import Counter
from html import escape
from pathlib import Path
from string import Template

ROOT = Path(__file__).resolve().parents[1]
SHOW = ROOT / 'series' / 'billions'
TITLES = ['Pilot', 'Naming Rights', 'YumTime', 'Short Squeeze', 'The Good Life', 'The Deal', 'The Punch', 'Boasts and Rails', 'Where the F*ck Is Donnie?', 'Quality of Life', 'Magical Thinking', 'The Conversation']
BACKGROUND = [
    dict(id='doj', title='美国司法部 · SDNY 办公室介绍', url='https://www.justice.gov/usao-sdny/about', note='机构背景：联邦检察官办公室的职权。'),
    dict(id='sec', title='SEC · Insider Trading — A U.S. Perspective', url='https://www.sec.gov/newsroom/speeches-statements/spch221-insider-trading-us-perspective', note='制度入门背景：重大非公开信息与相关义务，非对剧中交易的法律判决。'),
    dict(id='short', title='Investor.gov · 做多与做空', url='https://www.investor.gov/introduction-investing/investing-basics/how-stock-markets-work/stock-purchases-and-sales-long-and', note='金融术语：做多与做空的基础含义。'),
]


def esc(value):
    return escape(str(value), quote=True)


def lines(value):
    return '<br>'.join(esc(part) for part in str(value).splitlines())


def load_data(number):
    path = SHOW / f's01e{number:02}' / 'content.json'
    data = json.loads(path.read_text())
    data.setdefault('episode', number)
    data.setdefault('season', 1)
    return data


def validate(data, directory, registry):
    assert data['version'] == 2 and data['season'] == 1
    assert 1 <= data['episode'] <= 12
    expected_title = TITLES[data['episode'] - 1]
    title = data['title'].replace('Fuck', 'F*ck').replace('F**k', 'F*ck').replace('F--k', 'F*ck')
    assert title == expected_title, f'Unexpected episode title: {data["title"]}'
    assert 8 <= len(data['scenes']) <= 12, 'An episode needs 8–12 meaningful scenes'
    assert len(data['acts']) == 3 and 2 <= len(data['flows']) <= 3
    assert 3 <= len(data['quotes']) <= 4
    assert sum(len(quote['en'].split()) for quote in data['quotes']) <= 25
    scene_ids = {scene['id'] for scene in data['scenes']}
    assert len(scene_ids) == len(data['scenes'])
    assert {'chuck', 'axe', 'wendy'} <= data['characters'].keys()
    assert 2 <= len(data['characters']) - 3 <= 4
    for key in data['characters']:
        assert key in registry, f'Missing shared portrait: {key}'
        p = registry[key]
        assert p['actor'] and p['kind'] == 'character-still'
        assert (SHOW / 'shared' / p['file']).is_file()
        assert p['sourceUrl'].startswith('https://') and p['originalUrl'].startswith('https://')
    source_ids = {source['id'] for source in data['sources']}
    assert len(source_ids) == len(data['sources']) and len(source_ids) >= 3
    for source in data['sources']:
        assert source['url'].startswith('https://') and source['note'] and source['title']
    images = {Path(item['file']).stem: item for item in data['images']}
    assert len(images) == len(data['images']) and len(images) >= 6
    for image in data['images']:
        path = (directory / image['file']).resolve()
        assert path.is_relative_to(directory.resolve() / 'assets') and path.is_file(), image['file']
        assert image['kind'] in ['episode-still', 'episode-production-still']
        assert image['sourceUrl'].startswith('https://') and image['originalUrl'].startswith('https://')
        assert image['width'] > 0 and image['height'] > 0 and image['caption'] and image['alt']
    act_ids = {act['id'] for act in data['acts']}
    assert len(act_ids) == 3
    for act in data['acts']:
        assert 2 <= sum(scene['act'] == act['id'] for scene in data['scenes']) <= 4
    for scene in data['scenes']:
        assert scene['act'] in act_ids and scene['image'] in images
        assert set(scene['sources']) <= source_ids and scene['sources']
        assert scene['lane'] in ['law', 'capital', 'wendy', 'cross']
        assert all(scene.get(key) for key in ['where', 'title', 'fact', 'analysis', 'turn'])
    assert max(Counter(scene['image'] for scene in data['scenes']).values()) <= 2, 'Scene images are repeated too often'
    assert len(data['phases']) == 3 and len({p['id'] for p in data['phases']}) == 3
    for phase in data['phases']:
        assert len(phase['edges']) == 3
        assert data['characters'].keys() <= phase['details'].keys()
    assert len({flow['id'] for flow in data['flows']}) == len(data['flows'])
    for flow in data['flows']:
        assert len(flow['nodes']) == 4
        for node in flow['nodes']:
            assert node['scene'] in scene_ids
            assert node['portrait'] is None or node['portrait'] in data['characters']
    for quote in data['quotes']:
        assert quote['image'] in images and all(quote.get(k) for k in ['en', 'zh', 'speaker', 'context', 'analysis'])
    if data['episode'] != 1:
        assert len(data['motifs']) == 3 and data['hero'] in images
        assert data['closing']['image'] in images
        assert all(data.get(k) for k in ['heroTitle', 'heroDeck', 'openingTitle', 'storyTitle', 'storyDeck', 'catalogueIntro', 'stamp'])
        assert len(data['comparison']['rows']) == 3
        for side in ['left', 'right']:
            assert data['comparison'][side]['image'] in images
        evidence = data.get('evidence')
        if evidence:
            assert evidence['afterAct'] in act_ids and evidence['scene'] in scene_ids
            assert evidence['leftImage'] in images and evidence['rightImage'] in images
    return images


def navigation(number):
    left = f'<a href="../s01e{number-1:02}/">← 上一集 · {esc(TITLES[number-2])}</a>' if number > 1 else '<a href="../">← 第一季目录</a>'
    right = f'<a href="../s01e{number+1:02}/">下一集 · {esc(TITLES[number])} →</a>' if number < 12 else '<a href="../">回到第一季目录 →</a>'
    return f'<nav class="season-navigation wrap" aria-label="前后集导航">{left}<a href="../">十二集目录</a>{right}</nav>'


def render_episode(data, directory, registry):
    images = validate(data, directory, registry)
    portraits = {key: registry[key] for key in data['characters']}
    sources = list(data['sources'])
    for source in BACKGROUND:
        if source['id'] not in {s['id'] for s in sources}:
            sources.append(source)
    source_ids = [s['id'] for s in sources]
    used = set()
    def pic(name):
        used.add(name)
        return images[name]
    def image_tag(name):
        item = pic(name)
        return f'<img src="{esc(item["file"])}" alt="{esc(item["alt"])}" width="{item["width"]}" height="{item["height"]}" loading="lazy">'
    def photo(name, caption=None):
        item = pic(name)
        return f'<figure>{image_tag(name)}<figcaption>{esc(caption or item["caption"])}</figcaption></figure>'
    def avatar(key):
        p = portraits[key]
        return f'<span class="portrait" style="--position:{esc(p["position"])};--zoom:{p["zoom"]};--origin:{esc(p.get("origin", "50% 50%"))}"><img src="../shared/{esc(p["file"])}" alt="{esc(p["name"])}的剧中角色照" width="160" height="160" loading="lazy"></span>'
    def person_detail(key):
        p, c, phase = portraits[key], data['characters'][key], data['phases'][0]
        return f'<div class="detail-heading">{avatar(key)}<div><h3>{esc(p["name"])}</h3><small>{esc(p["en"])}</small></div></div><p class="detail-role">{esc(c["role"])}</p><h4>本集行动 · 剧情事实</h4><p>{esc(c["fact"])}</p><h4>人物阅读 · 个人解读</h4><p>{esc(c["analysis"])}</p><div class="phase-detail"><strong>{esc(phase["name"])}</strong><p>{esc(phase["details"][key])}</p></div><div class="portrait-credit">{esc(p["actor"])} 饰 · 统一剧中角色照</div>'
    def flow_html(flow):
        nodes = ''
        for i, node in enumerate(flow['nodes'], 1):
            face = avatar(node['portrait']) if node['portrait'] else f'<span class="flow-number">{i:02}</span>'
            nodes += f'<a class="flow-node" href="#scene-{esc(node["scene"])}">{face}<span><strong>{esc(node["name"])}</strong><small>{esc(node["role"])}</small></span></a>'
        return f'<div class="flow-heading"><h3>{esc(flow["title"])}</h3><p>{esc(flow["intro"])}</p></div><div class="flow-nodes">{nodes}</div><p class="flow-result">{esc(flow["result"])}</p>'
    def quote_html(q):
        return f'<div class="speaker">{esc(q["speaker"])}</div><blockquote lang="en">{esc(q["en"])}</blockquote><p class="translation">{esc(q["zh"])}</p><h4>这句话发生在哪里</h4><p>{esc(q["context"])}</p><div class="quote-reading"><h4>潜台词 · 个人解读</h4><p>{esc(q["analysis"])}</p></div>'
    acts = ''
    chapter_links = ''
    evidence = data.get('evidence')
    for act in data['acts']:
        indices = [i for i, scene in enumerate(data['scenes'], 1) if scene['act'] == act['id']]
        actual_range = f'{min(indices):02}—{max(indices):02}'
        chapter_links += f'<a href="#act-{esc(act["id"])}"><b>{esc(act["number"])}</b>{esc(act["title"].split("：")[0])} · {actual_range}</a>'
        cards = ''
        for index, scene in enumerate(data['scenes'], 1):
            if scene['act'] != act['id']:
                continue
            item = pic(scene['image'])
            refs = ''.join(f'<a class="ref" href="#source-{esc(key)}" aria-label="查看剧情依据">[{source_ids.index(key)+1}]</a>' for key in scene['sources'])
            detail = f'<p class="scene-detail">{esc(scene["detail"])}</p>' if scene.get('detail') else ''
            cards += f'<article class="scene" id="scene-{esc(scene["id"])}" data-index="{index}" data-lane="{esc(scene["lane"])}"><div class="scene-top"><span class="scene-num">{index:02}</span><div class="scene-title"><small>{esc(scene["where"])}</small><h4>{esc(scene["title"])}</h4></div></div><figure class="scene-photo">{image_tag(scene["image"])}<button class="zoom-photo" data-image="{esc(scene["image"])}" aria-label="查看第{index}个场景的完整图片">↗</button><figcaption class="caption">{esc(item["caption"])}</figcaption></figure><p class="scene-fact"><span class="fact-tag">剧情事实</span>{esc(scene["fact"])}{refs}</p><details class="scene-analysis" open><summary>这一场为什么重要 · 个人解读</summary><p>{esc(scene["analysis"])}</p></details><p class="scene-turn">{esc(scene["turn"])}</p>{detail}</article>'
        pair = ''
        if evidence and act['id'] == evidence['afterAct']:
            pair = f'<aside class="evidence"><div class="evidence-images">{photo(evidence["leftImage"],evidence["leftCaption"])}{photo(evidence["rightImage"],evidence["rightCaption"])}</div><div class="evidence-copy"><div class="eyebrow">{esc(evidence["kicker"])}</div><h3>{lines(evidence["title"])}</h3><p>{esc(evidence["text"])} <a href="#scene-{esc(evidence["scene"])}">回看对应场景 ↗</a></p></div></aside>'
        acts += f'<section class="act" id="act-{esc(act["id"])}"><div class="act-heading"><span class="roman">{esc(act["number"])}</span><div><h3>{esc(act["title"])}</h3><p>{esc(act["deck"])}</p></div><span class="range">{actual_range}</span></div><div class="scene-grid">{cards}</div><div class="act-summary"><strong>这一幕推进了什么</strong><p>{esc(act["summary"])}</p></div>{pair}</section>'
    comparison = data['comparison']
    columns = ''
    for side in ['left', 'right']:
        c = comparison[side]
        columns += f'<article class="warning-card">{photo(c["image"],c["caption"])}<div class="speaker">{esc(c["speaker"])}</div><h3>{lines(c["title"])}</h3><p>{esc(c["text"])}</p></article>'
    rows = ''.join(f'<div><dt>{esc(row["label"])}</dt><dd>{esc(row["left"])}</dd><span>↔</span><dd>{esc(row["right"])}</dd></div>' for row in comparison['rows'])
    insight = comparison['insight']
    comparison_section = f'<section class="power-section wrap" id="power"><div class="section-heading"><div><div class="eyebrow">04 / A CLOSER LOOK</div><h2>{lines(comparison["title"])}</h2><p>{esc(comparison["deck"])} · 以下为个人解读。</p></div></div><div class="warning-pair">{columns}</div><dl class="comparison">{rows}</dl><div class="reading-insight"><div class="eyebrow">{esc(insight["kicker"])}</div><h3>{lines(insight["title"])}</h3><p>{esc(insight["text"])}</p></div></section>'
    motifs = ''
    for i, motif in enumerate(data['motifs'], 1):
        steps = '<b>→</b>'.join(f'<span>{esc(step)}</span>' for step in motif['steps'])
        motifs += f'<article class="motif"><span class="motif-number">{i:02}</span><h3>{esc(motif["title"])}</h3><p>{esc(motif["fact"])} {esc(motif["analysis"])}</p><div class="mini-flow">{steps}</div></article>'
    core = ['chuck', 'axe', 'wendy']
    cast_strip = ''.join(f'<a class="cast-item" href="#relations">{avatar(key)}<div><small>{esc(portraits[key]["en"])}</small><p><strong>{esc(portraits[key]["name"])}</strong></p><p>{esc(data["characters"][key]["role"])}</p></div></a>' for key in core)
    main_people = ''.join(f'<button class="person {key}" data-person="{key}" aria-pressed="{str(key == "wendy").lower()}" aria-label="查看{esc(portraits[key]["name"])}的关系">{avatar(key)}<strong>{esc(portraits[key]["name"])}</strong><small>{esc(portraits[key]["en"])}</small></button>' for key in core)
    support = [key for key in portraits if key not in core]
    support_people = ''.join(f'<button class="support-person" data-person="{key}" aria-pressed="false" aria-label="查看{esc(portraits[key]["name"])}的关系">{avatar(key)}<strong>{esc(portraits[key]["name"])}</strong></button>' for key in support)
    phase_tabs = ''.join(f'<button data-phase="{p["id"]}" aria-pressed="{str(i == 0).lower()}">{esc(p["name"])}</button>' for i,p in enumerate(data['phases']))
    flow_tabs = ''.join(f'<button data-flow="{flow["id"]}" aria-pressed="{str(i == 0).lower()}">{esc(flow["title"])}</button>' for i,flow in enumerate(data['flows']))
    glossary = '<article><h3>联邦检察官</h3><p>查克属于联邦体系；纽约南区办公室代表美国处理其职权范围内的诉讼。<a href="#source-doj">[司法部]</a></p></article><article><h3>内幕交易</h3><p>重大非公开信息与相应义务，是理解剧中怀疑的重要背景。人物的指控、观众的判断与案件结论分别阅读。<a href="#source-sec">[SEC]</a></p></article><article><h3>做多 / 做空</h3><p>做多通常期待上涨；做空通常先卖出借来的股票，期待日后以较低价格买回。<a href="#source-short">[Investor.gov]</a></p></article>'
    values = dict(description=f'《亿万》S01E{data["episode"]:02} {data["title"]} 图文梳理：三幕剧情、人物关系、消息与选择路径、场景对照和台词笔记。剧透截至本集。',episode_slug=f'S01E{data["episode"]:02}',episode_number=f'{data["episode"]:02}',episode_code=f'S01 / E{data["episode"]:02}',episode_title=esc(data['title']),hero_title=lines(data['heroTitle']),hero_deck=lines(data['heroDeck']),spoiler=esc(data['spoiler']),spoiler_scope=f'剧透范围：截至 S01E{data["episode"]:02} 结尾',intro=esc(data['intro']),opening_title=lines(data['openingTitle']),opening_fact=esc(data['openingFact']),opening_reading=esc(data['openingReading']),opening_sources=''.join(f'<a class="ref" href="#source-{esc(s["id"])}">[{i+1}]</a>' for i,s in enumerate(sources[:2])),stamp_value=esc(data['stamp']['value']),stamp_label=esc(data['stamp']['label']),stamp_note=lines(data['stamp']['note']),story_title=lines(data['storyTitle']),story_deck=esc(data['storyDeck']),scene_count=len(data['scenes']),acts=acts,chapter_links=chapter_links,cast_strip=cast_strip,main_people=main_people,support_people=support_people,phase_tabs=phase_tabs,graph_note=esc(data['phases'][0]['note']),initial_person=person_detail('wendy'),initial_flow=flow_html(data['flows'][0]),flow_tabs=flow_tabs,comparison_section=comparison_section,motifs=motifs,initial_quote=quote_html(data['quotes'][0]),quote_count=f'{len(data["quotes"]):02}',quote_words=sum(len(q['en'].split()) for q in data['quotes']),season_navigation=navigation(data['episode']),glossary=glossary)
    for i in range(3):
        values[f'edge{i}'] = esc(data['phases'][0]['edges'][i])
    closing = data['closing']
    values.update(closing_kicker=esc(closing['kicker']),closing_value=esc(closing['value']),closing_title=lines(closing['title']),closing_text=lines(closing['text']))
    for prefix,name in [('hero',data['hero']),('quote',data['quotes'][0]['image']),('closing',closing['image'])]:
        item = pic(name)
        for field in ['src','alt','width','height','caption']:
            values[prefix+'_'+field] = esc(item['file'] if field == 'src' else item[field])
    for quote in data['quotes']:
        pic(quote['image'])
    values['source_list'] = ''.join(f'<li id="source-{esc(s["id"])}"><a href="{esc(s["url"])}" target="_blank" rel="noopener">{esc(s["title"])} ↗</a><span>{esc(s["note"])}</span></li>' for s in sources)
    values['image_list'] = ''.join(f'<li>{esc(item["caption"])} · <a href="{esc(item["originalUrl"])}" target="_blank" rel="noopener">原图</a> / <a href="{esc(item["sourceUrl"])}" target="_blank" rel="noopener">源页</a></li>' for name,item in images.items() if name in used)
    values['portrait_list'] = ''.join(f'<li>{esc(p["name"])} · {esc(p["actor"])} 饰 · <a href="{esc(p["originalUrl"])}" target="_blank" rel="noopener">原图</a> / <a href="{esc(p["sourceUrl"])}" target="_blank" rel="noopener">源页</a>{(" · " + esc(p["note"])) if p.get("note") else ""}</li>' for p in portraits.values())
    values['payload'] = json.dumps(dict(data,portraits=portraits,sources=sources),ensure_ascii=False).replace('<','\\u003c')
    page = Template((SHOW / 'shared' / 'season-episode.html').read_text()).substitute(values)
    page = page.replace('<div class="support-people"',f'<div class="support-people" style="--support-count:{len(support)}"')
    (directory / 'index.html').write_text(page)
    print(f'Rendered S01E{data["episode"]:02}: {len(data["scenes"])} scenes / {len(used)} editorial images / {len(portraits)} characters')


def catalogue(entries):
    records = []
    cards = ''
    for data in entries:
        number = data['episode']
        hero = next(item for item in data['images'] if Path(item['file']).stem == data['hero'])
        intro = data.get('catalogueIntro', '一条交易线索与一栋海边豪宅，如何将试探推进成公开对抗。首集建立查克、阿克斯与温迪的权力关系。')
        record = dict(episode=number,title=data['title'],subtitle=data['chineseTitle'],intro=intro,hero=f's01e{number:02}/{hero["file"]}',alt=hero['alt'],imageSource=hero['sourceUrl'],scenes=len(data['scenes']),quotes=len(data['quotes']))
        records.append(record)
        cards += f'<article class="season-card" id="episode-{number:02}"><a class="season-card-image" href="s01e{number:02}/" target="_blank" rel="noopener"><img src="{esc(record["hero"])}" alt="{esc(hero["alt"])}" width="{hero["width"]}" height="{hero["height"]}" loading="lazy"><span>{number:02}</span></a><div class="season-card-copy"><div class="eyebrow">EPISODE {number:02} / {esc(data["title"])}</div><h2>{esc(data["chineseTitle"])}</h2><p>{esc(intro)}</p><div class="season-card-meta"><span>{len(data["scenes"])} 个剧情节点</span><span>{len(data["quotes"])} 张台词卡</span><span>剧透至 E{number:02}</span></div><a class="read-link" href="s01e{number:02}/" target="_blank" rel="noopener">打开本集图解 ↗</a></div></article>'
    complete = len(records) == 12
    status = '完整十二集' if complete else f'已完成 {len(records)} 集'
    pilot = records[0]
    page = f'''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="theme-color" content="#161c20"><meta name="description" content="《亿万》第一季十二集图文阅读档案：剧情推进、真实剧照、人物关系、消息路径与台词深读。"><title>亿万 · 第一季十二集图解 — 剧中人</title><link rel="stylesheet" href="shared/episode.css?v=season1"><link rel="stylesheet" href="shared/season.css?v=season1"></head><body><header class="masthead"><a class="brand" href="../../"><b>✦</b>剧中人 <small>STORY FIELDNOTES</small></a><a class="episode-label" href="../../">全部作品 ↗</a></header><main><section class="season-hero"><img src="{esc(pilot['hero'])}" alt="{esc(pilot['alt'])}" width="640" height="426"><div class="season-hero-scrim"></div><div class="wrap"><div class="eyebrow">SEASON 01 / {status}</div><h1>BILLIONS<span>亿万 · 第一季</span></h1><p>一场调查，逐渐越过职业与婚姻的边界。<br>十二集，追踪选择怎样改写关系，关系又怎样改变证据。</p><div class="season-stat"><span><strong>{len(records):02}</strong>单集档案</span><span><strong>{sum(r['scenes'] for r in records)}</strong>剧情节点</span><span><strong>{sum(r['quotes'] for r in records)}</strong>台词笔记</span></div></div></section><section class="wrap season-opening"><h2>沿着十二集，读懂这场较量。</h2><p>每一篇限定截至该集的剧透范围，包含真实配图、三幕剧情、分阶段人物关系、消息与选择路径、对照深读和台词卡。场景解读默认展开；单集在新标签页打开。</p><p class="season-scope">目录完整展示各集配图与导读，导读本身也涉及对应剧情。请按已观看的集数选择。</p><nav class="season-jump" aria-label="集数导航">{''.join(f'<a href="#episode-{r["episode"]:02}">{r["episode"]:02}</a>' for r in records)}</nav></section><section class="wrap season-grid" aria-label="第一季单集目录">{cards}</section></main><footer class="sources wrap"><p>剧情事实、制度背景与个人解读分别标注。剧集画面归原权利人；图片与文字出处详见各篇末尾。首集保留已完成的重做版本。</p><div class="footer-bottom"><a href="../../">← 全部作品</a><span>BILLIONS / SEASON 01</span><a href="https://github.com/yokel062/shows">源码与内容 / GitHub ↗</a></div></footer></body></html>'''
    (SHOW / 'index.html').write_text(page+'\n')
    (SHOW / 'season.json').write_text(json.dumps(dict(season=1,complete=complete,episodes=records),ensure_ascii=False,indent=2)+'\n')
    print(f'Rendered season catalogue: {len(records)} episodes')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--complete', action='store_true', help='Require all twelve editorial episodes')
    parser.add_argument('--episode', type=int, choices=range(2,13), help='Render one new episode without changing the catalogue')
    parser.add_argument('--pilot', action='store_true', help='Regenerate the edited pilot, then restore the season catalogue')
    args = parser.parse_args()
    if args.pilot:
        from build_billions_pilot import build
        build()
    registry = json.loads((SHOW / 'shared' / 'portraits.json').read_text())['characters']
    if args.episode:
        data = load_data(args.episode)
        render_episode(data, SHOW / f's01e{args.episode:02}', registry)
        return
    numbers = [n for n in range(1,13) if (SHOW / f's01e{n:02}' / 'content.json').is_file()]
    if args.complete:
        assert numbers == list(range(1,13)), f'Missing episode sources: {set(range(1,13)) - set(numbers)}'
    entries = []
    for number in numbers:
        data = load_data(number)
        if number != 1:
            render_episode(data, SHOW / f's01e{number:02}', registry)
        entries.append(data)
    catalogue(entries)


if __name__ == '__main__':
    main()
