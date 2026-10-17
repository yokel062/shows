#!/usr/bin/env python3
"""Render Succession season one and its illustrated catalogue."""
import argparse
import hashlib
import json
import re
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SHOW = ROOT / 'series' / 'succession'
EPISODE = SHOW / 's01e01'


def episode_navigation(number):
    previous = (f'<a href="../s01e{number-1:02}/">← 上一集 / {number-1:02}</a>'
                if number > 1 else '<span>第一季，从这里开始</span>')
    following = (f'<a href="../s01e{number+1:02}/">下一集 / {number+1:02} →</a>'
                 if number < 10 else '<span>第一季完 · 不涉及后季</span>')
    return f'<nav class="episode-navigation wrap" aria-label="相邻集数">{previous}<a href="../">第一季十集目录 ↗</a>{following}</nav>'


def season_values(data, images, img, photo, e):
    def lines(value):
        return e(value).replace('|', '<br>')

    feature = data['feature']
    return {
        'episode_id': f'S01E{data["episode"]:02}', 'number': f'{data["episode"]:02}',
        'title': e(data['title']), 'question_text': e(data['question'].replace('|', '')),
        'question': lines(data['question']), 'deck': lines(data['deck']),
        'description': e(f'《继承之战》S01E{data["episode"]:02} {data["title"]}：三幕剧情、人物关系变化与三组冲突深读。剧透截至本集。'),
        'hero_key': e(data['heroKey']), 'spoiler': e(data['spoiler']),
        'translated_title': e(data['translatedTitle']), 'airdate': e(data['airdate']),
        'writer': e(data['writer']), 'director': e(data['director']),
        'opening_title': lines(data['openingTitle']), 'story_title': lines(data['storyTitle']),
        'couple_label': '夫妻' if data['episode'] == 10 else '未婚夫妻',
        'relation_foot': e(data['relationFoot']),
        'additional_people': ''.join(f'<a href="#person-{e(p["id"])}" data-character="{e(p["id"])}">{e(p["name"])} / {e(p["role"])} ↗</a>' for p in data['characters'] if p['id'] not in {'logan','marcia','kendall','connor','roman','shiv','greg','tom'}),
        'feature_title': lines(feature['title']), 'feature_subtitle': e(feature['subtitle']),
        'feature_steps': ''.join(f'<li><span>0{i}</span><strong>{e(s["title"])}</strong><p>{e(s["text"])}</p></li>' for i, s in enumerate(feature['steps'], 1)),
        'feature_photo': photo(feature['image']), 'feature_question': lines(feature['question']),
        'feature_analysis': ''.join(f'<p>{e(p)}</p>' for p in feature['analysis']),
        'feature_boundary': e(feature['boundary']),
        'ending_title': lines(data['ending']['title']), 'ending_copy': lines(data['ending']['copy']),
        'ending_question': lines(data['ending']['question']),
        'ending_known': e(data['ending']['known']), 'ending_unknown': e(data['ending']['unknown']),
        'ending_boundary': e(data['ending']['boundary']),
        'source_count': len(data['sources']), 'image_count': len(data['images']),
        'person_count': len(data['characters']), 'hero_file': e(images[data['hero']]['file']),
        'glossary': ''.join(f'<article><h3>{e(g["title"])}</h3><p>{e(g["text"])}</p></article>' for g in data['glossary']),
    }


def build_catalogue(require_complete=False):
    config = json.loads((SHOW / 'shared/catalogue.json').read_text())
    cover = config['cover']
    assert cover['kind'] == 'season-promotional' and cover['season'] == 1
    assert (SHOW / cover['file']).is_file()
    entries = []
    for directory in sorted(SHOW.glob('s01e??')):
        data = json.loads((directory / 'content.json').read_text())
        image_id = config['episodeImages'].get(str(data['episode']), data['hero'])
        image = next(x for x in data['images'] if x['id'] == image_id)
        entries.append({'episode': data['episode'], 'title': data['title'],
                        'question': data['question'].replace('|', ''),
                        'summary': data.get('catalogueSummary', data['intro']),
                        'url': directory.name + '/', 'image': directory.name + '/' + image['file'],
                        'alt': image['alt'], 'caption': image['caption'],
                        'sceneCount': len(data['scenes']), 'conflictCount': len(data['conflicts'])})
    if require_complete:
        assert [e['episode'] for e in entries] == list(range(1, 11)), 'All ten episodes are required'
    e = lambda value: escape(str(value), quote=True)
    cards = {}
    for p in entries:
        number = p['episode']
        featured = ' season-card-featured' if number in {1, 8} else ''
        label = '<p class="featured-label">从这里进入罗伊家 / START HERE</p>' if number == 1 else ''
        topics = ' / '.join(e(t) for t in config['topics'][str(number)])
        cards[number] = f'''<article class="season-card{featured}" id="episode-{number:02}"><a class="season-card-image" href="{e(p['url'])}" target="_blank" rel="noopener" aria-label="打开第 {number} 集：{e(p['title'])}"><img src="{e(p['image'])}" alt="{e(p['alt'])}" width="1280" height="720" loading="lazy"><span class="cover-number">{number:02}</span><span class="cover-arrow" aria-hidden="true">↗</span></a><div class="season-card-copy">{label}<p class="card-index">S01E{number:02}<span lang="en">{e(p['title'])}</span></p><h3><a href="{e(p['url'])}" target="_blank" rel="noopener">{e(p['question'])}</a></h3><p class="card-summary">{e(p['summary'])}</p><p class="card-topics">{topics}</p><div class="season-card-meta"><a href="{e(p['url'])}" target="_blank" rel="noopener">阅读本集图解 <span aria-hidden="true">↗</span></a><span>{p['sceneCount']} 个剧情节点 · {p['conflictCount']} 组冲突</span></div><p class="season-card-credit">{e(p['caption'])}</p></div></article>'''
    chapters = []
    assert [n for chapter in config['chapters'] for n in chapter['episodes']] == list(range(1, 11))
    for chapter in config['chapters']:
        chapters.append(f'''<section class="archive-chapter" aria-labelledby="chapter-{e(chapter['number'])}"><header class="chapter-heading"><span class="chapter-number">{e(chapter['number'])}</span><div><p class="eyebrow">{e(chapter['label'])} / EPISODES {e(chapter['range'])}</p><h2 id="chapter-{e(chapter['number'])}">{e(chapter['title'])}</h2></div><p>{e(chapter['summary'])}</p></header><div class="season-grid">{''.join(cards[n] for n in chapter['episodes'])}</div></section>''')
    pilot = json.loads((SHOW / 's01e01/content.json').read_text())
    people = {p['id']: p for p in pilot['characters']}
    portraits = json.loads((SHOW / 'shared/portraits.json').read_text())['characters']
    family = []
    assert {r['conflict'] for r in config['relationships']} <= {c['id'] for c in pilot['conflicts']}
    for relationship in config['relationships']:
        faces = []
        for key in relationship['people']:
            person, portrait = people[key], portraits[key]
            faces.append(f'<img src="shared/{e(portrait["file"])}" alt="{e(person["name"])}（{e(portrait["actor"])}饰）" width="420" height="420" loading="lazy">')
        family.append(f'''<article class="relationship-card"><div class="portrait-pair">{faces[0]}<span aria-hidden="true">×</span>{faces[1]}</div><p class="relation-label">{e(relationship['label'])}</p><h3>{e(relationship['title'])}</h3><p>{e(relationship['copy'])}</p><a href="s01e01/#conflict-{e(relationship['conflict'])}" target="_blank" rel="noopener">读这组人物冲突 <span aria-hidden="true">↗</span></a></article>''')
    raw = (SHOW / 'shared/season-catalogue.html').read_text()
    values = {
        'chapters': ''.join(chapters), 'count': len(entries), 'people': ''.join(family),
        'jumps': ''.join(f'<a href="#episode-{p["episode"]:02}" aria-label="跳到第 {p["episode"]} 集">{p["episode"]:02}</a>' for p in entries),
        'scenes': sum(p['sceneCount'] for p in entries),
        'conflicts': sum(p['conflictCount'] for p in entries),
        'images': sum(len(json.loads((SHOW / p['url'] / 'content.json').read_text())['images']) for p in entries),
        'hero_image': e(cover['file']), 'hero_alt': e(cover['alt']),
        'hero_width': cover['width'], 'hero_height': cover['height'],
        'hero_caption': e(cover['caption']), 'hero_source': e(cover['sourceUrl']),
        'hero_original': e(cover['originalUrl']),
    }
    raw = re.sub(r'\{\{([a-z_]+)\}\}', lambda match: str(values[match[1]]), raw)
    assert not re.search(r'\{\{[a-z_]+\}\}', raw)
    (SHOW / 'index.html').write_text(raw)
    (SHOW / 'season.json').write_text(json.dumps({'season': 1, 'complete': len(entries) == 10, 'episodes': entries}, ensure_ascii=False, indent=2) + '\n')
    print(f'Built Succession catalogue: {len(entries)} episodes')


def build_episode(number=1):
    EPISODE = SHOW / f's01e{number:02}'
    data = json.loads((EPISODE / 'content.json').read_text())
    portraits = json.loads((SHOW / 'shared/portraits.json').read_text())['characters']
    images = {item['id']: item for item in data['images']}
    people = {item['id']: item for item in data['characters']}
    sources = {item['id']: item for item in data['sources']}
    scenes = {item['id']: item for item in data['scenes']}
    acts = {item['id']: item for item in data['acts']}
    e = lambda value: escape(str(value), quote=True)
    assert (data['season'], data['episode']) == (1, number)
    assert len(images) == len(data['images']) and len(scenes) == (12 if number == 1 else 9)
    assert len(people) == len(data['characters']) and set(people) <= set(portraits)
    assert {'logan', 'marcia', 'kendall', 'connor', 'roman', 'shiv', 'greg', 'tom'} <= set(people)
    assert len(sources) == len(data['sources'])
    assert len(acts) == 3 and len(data['phases']) == 3
    assert all(len(phase['edges']) == 5 for phase in data['phases'])
    assert all(re.fullmatch(r'[a-z0-9-]+', key) for key in scenes)
    assert sum(len(item['en'].split()) for item in data['quotes']) <= 25
    for item in data['images']:
        path = (EPISODE / item['file']).resolve()
        assert path.is_relative_to(EPISODE / 'assets') and path.is_file()
        assert item['kind'] == 'episode-still' and item['episode'] == f'S01E{number:02}'
        assert item['alt'] and item['caption'] and item['frame'] > 0
        assert all(item[key].startswith('https://') for key in ['sourceUrl', 'originalUrl'])
    for person in portraits.values():
        path = (SHOW / 'shared' / person['file']).resolve()
        assert path.is_relative_to(SHOW / 'shared/portraits') and path.is_file()
        assert person['actor'] and person['kind'] == 'character-still'
        assert all(person[key].startswith('https://') for key in ['sourceUrl', 'originalUrl'])
    for scene in data['scenes']:
        assert scene['act'] in acts and scene['image'] in images
        assert set(scene['sources']) <= set(sources)
        if 'secondaryImage' in scene:
            assert scene['secondaryImage'] in images
    for conflict in data['conflicts']:
        assert conflict['scene'] in scenes and conflict['image'] in images
        assert set(conflict['people']) <= set(people)
    for person in data['characters']:
        assert len(person['phase']) == len(data['phases'])
    for motif in data['motifs']:
        assert motif['image'] in images and motif['link'] in scenes
    assert data['hero'] in images and data['prologue']['image'] in images
    if number > 1:
        assert data['feature']['image'] in images and len(data['feature']['steps']) == 3
        assert len(data['conflicts']) == 3 and len(data['quotes']) == 3

    def refs(keys):
        return ' '.join(f'<a class="ref" href="#source-{e(key)}" aria-label="依据：{e(sources[key]["title"])}">[{list(sources).index(key) + 1}]</a>' for key in keys)

    def img(key, lazy=True, prefix=''):
        item = images[key]
        loading = ' loading="lazy"' if lazy else ' fetchpriority="high"'
        return f'<img src="{prefix}{e(item["file"])}" alt="{e(item["alt"])}" width="{item["width"]}" height="{item["height"]}"{loading}>'

    def photo(key):
        item = images[key]
        return (f'<figure class="photo"><a class="photo-link" href="{e(item["file"])}" data-photo="{e(key)}" '
                f'aria-label="放大剧照：{e(item["alt"])}">{img(key)}<span aria-hidden="true">↗</span></a>'
                f'<figcaption>{e(item["caption"])}</figcaption></figure>')

    def portrait(key, prefix='../shared/'):
        p = portraits[key]
        return f'<img src="{prefix}{e(p["file"])}" alt="{e(p["name"])}（{e(p["actor"])}饰）" width="420" height="420" loading="lazy">'

    def render(template, values):
        raw = (SHOW / 'shared' / template).read_text()
        output = re.sub(r'\{\{([a-z_]+)\}\}', lambda match: str(values[match[1]]), raw)
        assert not re.search(r'\{\{[a-z_]+\}\}', output)
        return output

    rendered_acts = []
    for act in data['acts']:
        cards = []
        for index, scene in enumerate(data['scenes'], 1):
            if scene['act'] != act['id']:
                continue
            photos = photo(scene['image'])
            if scene.get('secondaryImage'):
                photos = f'<div class="photo-pair">{photos}{photo(scene["secondaryImage"])}</div>'
            cards.append(f'''<article class="scene" id="scene-{e(scene['id'])}">
              <header class="scene-heading"><span class="scene-number">{index:02}</span><div><p class="location">{e(scene['where'])}</p><h4>{e(scene['title'])}</h4></div></header>
              {photos}<div class="scene-copy"><p class="scene-fact"><span class="fact-label">剧情事实</span>{e(scene['fact'])} {refs(scene['sources'])}</p>
              <details class="scene-analysis" open><summary>这一场为什么重要 <span>个人解读</span></summary><p>{e(scene['analysis'])}</p></details>
              <p class="scene-turn"><span>权力的变化</span>{e(scene['turn'])}</p></div></article>''')
        rendered_acts.append(f'''<section class="act" id="act-{e(act['id'])}" aria-labelledby="act-title-{e(act['id'])}">
          <div class="act-heading"><span class="act-number">{e(act['number'])}</span><div><p class="eyebrow">ACT {e(act['number'])} / SCENES {e(act['range'])}</p><h3 id="act-title-{e(act['id'])}">{e(act['title'])}<small>{e(act['subtitle'])}</small></h3></div></div>
          <div class="scene-grid">{''.join(cards)}</div><p class="act-summary"><span>这一幕之后</span>{e(act['summary'])}</p></section>''')

    positions = {'logan': (45, 16.5), 'marcia': (81.25, 16.5), 'kendall': (12.5, 54), 'connor': (37, 54), 'roman': (61.5, 54), 'shiv': (86, 54), 'greg': (12.5, 87), 'tom': (86, 87)}
    nodes = ''.join(f'''<a class="person-node {'patriarch' if key == 'logan' else ''}" href="#person-{key}" data-character="{key}" style="--x:{xy[0]}%;--y:{xy[1]}%"><span class="avatar">{portrait(key)}</span><strong>{e(people[key]['name'])}</strong><small>{e(people[key]['en'])}</small></a>''' for key, xy in positions.items())
    person_cards = []
    for key, p in people.items():
        phases = ''.join(f'<p class="character-phase" data-person-phase="{phase["id"]}"><span>{e(phase["label"])}</span>{e(p["phase"][index])}</p>' for index, phase in enumerate(data['phases']))
        person_cards.append(f'''<article class="person-card" id="person-{key}"><div class="person-heading"><span class="avatar">{portrait(key)}</span><div><p class="eyebrow">CHARACTER FILE</p><h3>{e(p['name'])}</h3><p class="person-english">{e(p['en'])}</p></div></div><p class="person-role">{e(p['role'])}</p>
          <dl><div><dt>想得到</dt><dd>{e(p['want'])}</dd></div><div><dt>手中筹码</dt><dd>{e(p['power'])}</dd></div><div><dt>脆弱之处</dt><dd>{e(p['cost'])}</dd></div></dl>
          <p class="person-reading"><span>人物解读</span>{e(p['reading'])}</p>{phases}</article>''')

    conflict_panels = []
    for c in data['conflicts']:
        faces = ''.join(f'<span class="conflict-person"><span class="avatar">{portrait(key)}</span>{e(people[key]["name"])}</span>' for key in c['people'])
        paragraphs = ''.join(f'<p>{e(text)}</p>' for text in c['analysis'])
        conflict_panels.append(f'''<article class="conflict-panel" id="conflict-{e(c['id'])}"><div class="conflict-visual">{photo(c['image'])}<div class="conflict-people">{faces}</div><p class="surface"><span>表面争执</span>{e(c['surface'])}</p><a class="text-link" href="#scene-{e(c['scene'])}">回到相关场景 ↗</a></div><div class="conflict-copy"><p class="eyebrow">BENEATH THE ARGUMENT / 个人解读</p><h3>{e(c['title'])}</h3><div class="opposed-wants"><p>{e(c['wantA'])}</p><p>{e(c['wantB'])}</p></div>{paragraphs}<p class="boundary"><span>事实边界</span>{e(c['boundary'])}</p></div></article>''')

    quote_cards = ''.join(f'''<article class="quote-card"><span class="quote-mark" aria-hidden="true">“</span><p class="quote-speaker">{e(q['speaker'])}</p><blockquote lang="en">{e(q['en'])}</blockquote><p class="quote-translation">{e(q['zh'])}<small>中文自译</small></p><p class="quote-context"><span>说话时刻</span>{e(q['context'])}</p><p class="quote-analysis"><span>个人解读</span>{e(q['analysis'])}</p></article>''' for q in data['quotes'])
    motif_cards = ''.join(f'''<article class="motif">{photo(m['image'])}<div><p class="eyebrow">{e(m['number'])} / {e(m['label'])}</p><h3>{e(m['title'])}</h3><p>{e(m['text'])}</p><a class="text-link" href="#scene-{e(m['link'])}">回看相关场景 ↗</a></div></article>''' for m in data['motifs'])
    source_list = ''.join(f'<li id="source-{e(s["id"])}"><a href="{e(s["url"])}" target="_blank" rel="noopener noreferrer">{e(s["title"])} ↗</a><p>{e(s["note"])}</p></li>' for s in data['sources'])
    image_list = ''.join(f'<li><strong>{e(item["id"])}</strong> · 本集截图 {item["frame"]:04} · {item["width"]} × {item["height"]}<p>{e(item["caption"])}</p><a href="{e(item["sourceUrl"])}" target="_blank" rel="noopener noreferrer">相册页</a> / <a href="{e(item["originalUrl"])}" target="_blank" rel="noopener noreferrer">对应原图 ↗</a></li>' for item in data['images'])
    portrait_list = ''.join(f'<li><strong>{e(p["name"])} / {e(p["en"])}</strong> · {e(p["actor"])}<p>{e(p["episode"])} 角色照 {p["frame"]:04}，原图裁切后缩放为 420 × 420；同一人物跨集复用。</p><a href="{e(p["sourceUrl"])}" target="_blank" rel="noopener noreferrer">相册页</a> / <a href="{e(p["originalUrl"])}" target="_blank" rel="noopener noreferrer">原始画面 ↗</a></li>' for p in (portraits[key] for key in people))
    chapter_nav = ''.join(f'<a href="#act-{e(a["id"])}"><span>{e(a["number"])}</span><div><strong>{e(a["title"])}</strong><small>{e(a["range"])} / {e(a["subtitle"])}</small></div><b aria-hidden="true">↘</b></a>' for a in data['acts'])
    phase_buttons = ''.join(f'<button type="button" data-phase="{e(p["id"])}" aria-pressed="{str(i == 0).lower()}">{e(p["label"])}</button>' for i, p in enumerate(data['phases']))
    phase_summaries = ''.join(f'<div class="phase-summary" data-phase-summary="{e(p["id"])}"><h3>{e(p["title"])}</h3><p>{e(p["note"])}</p></div>' for p in data['phases'])
    conflict_nav = ''.join(f'<a href="#conflict-{e(c["id"])}" data-conflict="{e(c["id"])}"><span>0{i}</span>{e(c["label"])}<b aria-hidden="true">↗</b></a>' for i, c in enumerate(data['conflicts'], 1))
    source_hash = hashlib.sha256((EPISODE / 'content.json').read_bytes()).hexdigest()
    portrait_hash = hashlib.sha256(json.dumps({key: portraits[key] for key in people}, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
    payload = json.dumps({'images': data['images'], 'phases': data['phases'], 'initialCharacter': data.get('initialCharacter', 'logan'), 'sourceHash': source_hash, 'portraitHash': portrait_hash}, ensure_ascii=False).replace('<', '\\u003c')
    prologue = data['prologue']
    values = {
        'intro': e(data['intro']), 'hero_photo': img(data['hero'], False), 'hero_caption': e(images[data['hero']]['caption']),
        'prologue_photo': photo(prologue['image']), 'prologue_title': e(prologue['title']), 'prologue_fact': e(prologue['fact']),
        'prologue_analysis': e(prologue['analysis']), 'prologue_refs': refs(prologue['sources']),
        'chapter_nav': chapter_nav, 'acts': ''.join(rendered_acts), 'nodes': nodes,
        'phase_buttons': phase_buttons, 'phase_summaries': phase_summaries, 'person_cards': ''.join(person_cards),
        'conflict_nav': conflict_nav, 'conflicts': ''.join(conflict_panels), 'watch_photo': photo('watch') if number == 1 else '',
        'quotes': quote_cards, 'quote_words': sum(len(q['en'].split()) for q in data['quotes']),
        'motifs': motif_cards, 'source_list': source_list, 'image_list': image_list, 'portrait_list': portrait_list,
        'payload': payload, 'episode_nav': episode_navigation(number),
    }
    if number != 1:
        values.update(season_values(data, images, img, photo, e))
    html = render('episode.html' if number == 1 else 'season-episode.html', values)
    (EPISODE / 'index.html').write_text(html)
    print(f'Built Succession S01E{number:02}: {len(scenes)} scenes, {len(people)} characters, {len(data["conflicts"])} conflicts, {len(images)} scene images')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--episode', type=int, choices=range(1, 11))
    parser.add_argument('--complete', action='store_true')
    args = parser.parse_args()
    numbers = [args.episode] if args.episode else range(1, 11)
    for number in numbers:
        build_episode(number)
    build_catalogue(require_complete=args.complete)
