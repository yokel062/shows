#!/usr/bin/env python3
"""Build the White Lotus pilot and catalogue from reviewed editorial data."""
import json
from html import escape
from pathlib import Path
from string import Template

ROOT = Path(__file__).resolve().parents[1]
SHOW = ROOT / 'series' / 'the-white-lotus'
EPISODE = SHOW / 's01e01'


def build():
    data = json.loads((EPISODE / 'content.json').read_text())
    portraits = json.loads((SHOW / 'shared' / 'portraits.json').read_text())['characters']
    images = {item['id']: item for item in data['images']}
    sources = {item['id']: item for item in data['sources']}
    people = {item['id']: item for item in data['characters']}
    e = lambda value: escape(str(value), quote=True)
    assert len(images) == len(data['images'])
    assert len(people) == len(data['characters']) and set(people) == set(portraits)
    scene_ids = {item['id'] for item in data['scenes']}
    assert len(scene_ids) == len(data['scenes'])
    assert sum(len(item['en'].split()) for item in data['quotes']) <= 25
    for item in data['images']:
        path = (EPISODE / item['file']).resolve()
        assert path.is_relative_to(EPISODE / 'assets') and path.is_file()
        assert item['kind'] == 'episode-still' and item['alt'] and item['caption']
        assert item['originalUrl'].startswith('https://') and item['sourceUrl'].startswith('https://')
    for person in portraits.values():
        path = (SHOW / 'shared' / person['file']).resolve()
        assert path.is_relative_to(SHOW / 'shared' / 'portraits') and path.is_file()
        assert person['actor'] and person['kind'] == 'character-still'
        assert person['originalUrl'].startswith('https://') and person['sourceUrl'].startswith('https://')
    for scene in data['scenes']:
        assert scene['act'] in {a['id'] for a in data['acts']}
        assert scene['image'] in images and set(scene['sources']) <= set(sources)
    for conflict in data['conflicts']:
        assert set(conflict['people']) <= set(people) and conflict['scene'] in scene_ids

    def refs(keys):
        return ''.join(f'<a class="ref" href="#source-{e(key)}" aria-label="依据：{e(sources[key]["title"])}">[{list(sources).index(key)+1}]</a>' for key in keys)

    def img(key, lazy=True, prefix=''):
        item = images[key]
        loading = ' loading="lazy"' if lazy else ' fetchpriority="high"'
        return f'<img src="{prefix}{e(item["file"])}" alt="{e(item["alt"])}" width="{item["width"]}" height="{item["height"]}"{loading}>'

    def photo(key, label=None):
        item = images[key]
        return f'<figure class="photo"><button class="photo-button" data-photo="{key}" aria-label="放大：{e(item["alt"])}">{img(key)}<span aria-hidden="true">↗</span></button><figcaption>{e(label or item["caption"])}</figcaption></figure>'

    def avatar(key):
        p = portraits[key]
        x, y = [float(value.rstrip('%')) / 100 for value in p['position'].split()]
        crop_width = p['width'] / p['height'] * p['zoom'] * 100
        crop_left, crop_top = 50 - x * crop_width, 50 - y * p['zoom'] * 100
        style = f'--crop-width:{crop_width:.2f}%;--crop-left:{crop_left:.2f}%;--crop-top:{crop_top:.2f}%'
        return f'<span class="portrait" style="{style}"><img src="../shared/{e(p["file"])}" alt="{e(p["name"])}的剧中角色照" width="{p["width"]}" height="{p["height"]}" loading="lazy"></span>'

    acts = ''
    for act in data['acts']:
        scenes = [s for s in data['scenes'] if s['act'] == act['id']]
        cards = ''
        for scene in scenes:
            index = data['scenes'].index(scene) + 1
            cards += f'<article class="scene" id="scene-{e(scene["id"])}">{photo(scene["image"])}<div class="scene-copy"><div class="scene-heading"><span class="scene-number">{index:02}</span><div><small>{e(scene["where"])}</small><h4>{e(scene["title"])}</h4></div></div><p class="scene-fact"><span class="fact-tag">剧情事实</span>{e(scene["fact"])} {refs(scene["sources"])}</p><details class="scene-analysis" open><summary>这一场为什么重要 · 个人解读</summary><p>{e(scene["analysis"])}</p></details><p class="scene-turn"><span>→</span>{e(scene["turn"])}</p></div></article>'
        if act['id'] == 'needs':
            cards += f'<aside class="father-note">{photo("father")}<div><small>另一条并行的人物线 · 个人解读</small><h4>父亲说了很多，<br>儿子仍在等待被听见。</h4><p>马克担心身体，也担心自己在家庭里的位置。他把陪伴儿子当成一次重新成为好父亲的机会，可谈话很快回到自己的不安。爱是真的，谈话中的重心也是真的。奎因对母亲收入的直问，让两代人的视角短暂撞在一起。</p><a href="#conflict-parents">查看这组关系 ↗</a></div></aside>'
        odd = ' odd' if len(scenes) % 2 else ''
        acts += f'<section class="act" id="act-{act["id"]}"><div class="act-heading"><span>{e(act["number"])}</span><div><small>DAY ONE / 第一天</small><h3>{e(act["title"])}</h3><p>{e(act["deck"])}</p></div></div><div class="scene-grid{odd}">{cards}</div><div class="act-summary"><strong>这一幕推进了什么</strong><p>{e(act["summary"])}</p></div></section>'

    tabs = ''.join(f'<a class="conflict-tab" href="#conflict-{c["id"]}" data-conflict="{c["id"]}" aria-controls="conflict-{c["id"]}"><small>0{i}</small>{e(c["label"])}</a>' for i, c in enumerate(data['conflicts'], 1))
    conflicts = ''
    for i, conflict in enumerate(data['conflicts'], 1):
        nodes = ''.join(f'<a class="relation-person node-{j}" href="#person-{key}">{avatar(key)}<strong>{e(portraits[key]["name"])}</strong><small>{e(people[key]["role"])}</small></a>' for j, key in enumerate(conflict['people']))
        edges = ''.join(f'<li>{e(edge)}</li>' for edge in conflict['edges'])
        two = ' two' if len(conflict['people']) == 2 else ''
        lines = '<path d="M135 150 L465 150 M135 150 L300 330 M465 150 L300 330"/>' if not two else '<path d="M135 230 L465 230"/>'
        graph = f'<div class="relation-graph{two}"><span class="graph-index">RELATIONSHIP / 0{i}</span><svg viewBox="0 0 600 460" preserveAspectRatio="none" aria-hidden="true">{lines}</svg>{nodes}</div><ul class="relation-edges">{edges}</ul>'
        conflicts += f'<article class="conflict-panel" id="conflict-{conflict["id"]}"><div class="relation-visual">{graph}</div><div class="conflict-copy"><small class="eyebrow">0{i} / {e(conflict["label"])}</small><h3>{e(conflict["title"])}</h3><h4>关系依据 · 剧情事实</h4><p>{e(conflict["fact"])}</p><h4>冲突怎样发生 · 个人解读</h4><p>{e(conflict["analysis"])}</p><p class="conflict-question">{e(conflict["question"])}</p><a class="text-link" href="#scene-{conflict["scene"]}">回到对应场景 ↗</a></div></article>'
    cast = ''
    for key, person in people.items():
        p = portraits[key]
        cast += f'<details class="cast-person" id="person-{key}"><summary>{avatar(key)}<span><strong>{e(p["name"])}</strong><small>{e(p["en"])}</small><em>{e(person["role"])}</em></span><b aria-hidden="true">+</b></summary><div class="cast-detail"><p><span class="fact-tag">本集行动</span>{e(person["fact"])}</p><p><span class="reading-tag">个人解读</span>{e(person["reading"])}</p><small>{e(p["actor"])} 饰 · <a href="#portrait-{key}">角色照出处 ↗</a></small></div></details>'
    readings = ''
    for reading in data['readings']:
        readings += f'<article class="close-reading"><div class="reading-heading"><span>{e(reading["number"])}</span><h3>{e(reading["title"])}</h3></div><div class="image-pair">{photo(reading["left"], reading["leftLabel"])}{photo(reading["right"], reading["rightLabel"])}</div><div class="reading-copy"><span class="reading-tag">画面深读 · 个人解读</span><p>{e(reading["analysis"])}</p><a class="text-link" href="#scene-{reading["scene"]}">带着这个问题，回看场景 ↗</a></div></article>'
    quotes = ''.join(f'<article class="quote-card"><small>{e(q["speaker"])}</small><blockquote lang="en">{e(q["en"])}</blockquote><p class="translation">{e(q["zh"])}<span>中文自译</span></p><h3>发生在哪里</h3><p>{e(q["context"])}</p><h3>潜台词 · 个人解读</h3><p>{e(q["analysis"])}</p>{refs(["transcript"])}</article>' for q in data['quotes'])
    source_list = ''.join(f'<li id="source-{key}"><a href="{e(s["url"])}" target="_blank" rel="noopener noreferrer">{e(s["title"])} ↗</a><p>{e(s["note"])}</p></li>' for key, s in sources.items())
    asset_list = ''.join(f'<li><strong>{e(key)}.jpg</strong> · {e(item["caption"])}<br><a href="{e(item["sourceUrl"])}" target="_blank" rel="noopener noreferrer">图库页面 ↗</a> · <a href="{e(item["originalUrl"])}" target="_blank" rel="noopener noreferrer">原始画面 ↗</a></li>' for key, item in images.items())
    portrait_list = ''.join(f'<li id="portrait-{key}"><strong>{e(p["name"])}</strong> · {e(p["actor"])} 饰 · 本集图库 #{p["frame"]}<br><a href="{e(p["sourceUrl"])}" target="_blank" rel="noopener noreferrer">图库页面 ↗</a> · <a href="{e(p["originalUrl"])}" target="_blank" rel="noopener noreferrer">原始画面 ↗</a></li>' for key, p in portraits.items())
    values = {
        'hero': img('hero', False), 'hero_caption': e(images['hero']['caption']),
        'intro': e(data['intro']), 'spoiler': e(data['spoiler']),
        'opening_fact': e(data['opening']['fact']), 'opening_analysis': e(data['opening']['analysis']),
        'opening_refs': refs(data['opening']['sources']), 'acts': acts,
        'tabs': tabs, 'conflicts': conflicts, 'cast': cast, 'readings': readings,
        'quotes': quotes, 'ending_title': '<br>'.join(e(data['ending']['title']).split('\n')),
        'ending_text': e(data['ending']['text']),
        'known': ''.join(f'<li>{e(t)}</li>' for t in data['ending']['known']),
        'sources': source_list, 'asset_sources': asset_list, 'portrait_sources': portrait_list,
        'payload': json.dumps({'images': images}, ensure_ascii=False).replace('<', '\\u003c')
    }
    template = Template((SHOW / 'shared' / 'episode.html').read_text())
    (EPISODE / 'index.html').write_text(template.substitute(values))
    catalogue = Template((SHOW / 'shared' / 'catalogue.html').read_text())
    (SHOW / 'index.html').write_text(catalogue.substitute(hero=img('boat', False, 's01e01/'), arrival=img('arrival', True, 's01e01/')))
    print(f'Built White Lotus pilot: {len(data["scenes"])} scenes, {len(people)} characters, {len(data["conflicts"])} conflict maps, {len(images)} episode images')


if __name__ == '__main__':
    build()
