#!/usr/bin/env python3
"""Render Better Call Saul season one from episode-specific editorial JSON."""
import argparse
import hashlib
import json
import re
from html import escape
from pathlib import Path
from string import Template

ROOT = Path(__file__).resolve().parents[1]
SHOW = ROOT / 'series' / 'better-call-saul'
TITLES = ['Uno', 'Mijo', 'Nacho', 'Hero', 'Alpine Shepherd Boy', 'Five-O', 'Bingo', 'RICO', 'Pimento', 'Marco']


def validate(data, directory, registry):
    number = int(data['episode'][-2:])
    assert data['version'] == 1 and data['episode'] == f'S01E{number:02}'
    assert data['title'] == TITLES[number - 1]
    assert len(data['scenes']) == len({s['id'] for s in data['scenes']})
    assert 8 <= len(data['scenes']) <= 12
    assert len({item['id'] for item in data['images']}) == len(data['images'])
    assert len({item['id'] for item in data['sources']}) == len(data['sources'])
    assert 4 <= len(data['characters']) <= 9 and set(data['characters']) <= set(registry)
    assert len(data['phases']) == 3 and len(data['conflicts']) == 4
    assert 3 <= len(data['quotes']) <= 4 and sum(len(q['en'].split()) for q in data['quotes']) <= 25
    assert len(data['acts']) == 3 and all(2 <= sum(s['act'] == a['id'] for s in data['scenes']) <= 4 for a in data['acts'])
    sources = {item['id'] for item in data['sources']}
    images = {item['id'] for item in data['images']}
    for scene in data['scenes']:
        assert all(scene[key] for key in ['fact', 'analysis', 'turn', 'sources'])
        assert scene['image'] in images and set(scene['sources']) <= sources
    from PIL import Image
    for item in data['images']:
        path = (directory / item['file']).resolve()
        assert path.is_relative_to(directory / 'assets') and path.is_file()
        assert item['episode'] == data['episode']
        assert item['kind'] in ['episode-still', 'episode-production-still']
        assert item['alt'] and item['caption']
        assert all(item[key].startswith('https://') for key in ['sourceUrl', 'originalUrl'])
        with Image.open(path) as picture:
            assert picture.size == (item['width'], item['height'])
    for key in data['characters']:
        person = registry[key]
        path = (SHOW / 'shared' / person['file']).resolve()
        assert path.is_relative_to(SHOW / 'shared' / 'portraits') and path.is_file()
        assert person['actor'] and person['kind'] == 'character-still'
        assert int(person['episode'][-2:]) <= number, f'Future portrait in {data["episode"]}: {key}'
        assert .8 <= person['zoom'] <= 3 and re.fullmatch(r'\d+% \d+%', person['position'])
        assert 1 <= person['ratio'] <= 2.5
        assert all(person[field].startswith('https://') for field in ['sourceUrl', 'originalUrl'])
    for phase in data['phases']:
        assert set(phase['details']) == set(data['characters'])
        assert len(phase['edges']) == (4 if number == 1 else len(data['relationships']))
    if number > 1:
        assert data['central'] in data['characters']
        for edge in data['relationships']:
            assert edge['from'] in data['characters'] and edge['to'] in data['characters']
    assert all(item['image'] in images for item in data['quotes'] + data['conflicts'])
    assert data['hero'] in images and data['prologue']['image'] in images


def episode_navigation(number):
    previous = f'<a href="../s01e{number-1:02}/">← 上一集 · {TITLES[number-2]}</a>' if number > 1 else '<span>第一季，从这里开始</span>'
    following = f'<a href="../s01e{number+1:02}/">下一集 · {TITLES[number]} →</a>' if number < 10 else '<span>第一季完 · 不涉及后季</span>'
    return f'<nav class="episode-navigation wrap" aria-label="相邻集数">{previous}<a href="../">第一季十集目录 ↗</a>{following}</nav>'


def season_values(data, values, images, positions, photo, e):
    lines = lambda value: e(value).replace('|', '<br>')
    values.update(number=data['episode'][-2:], episode_id=e(data['episode']), title=e(data['title']),
                  question=lines(data['question']), deck=lines(data['deck']),
                  description=e(f'《风骚律师》{data["episode"]} {data["title"]}：三幕剧情、人物关系与四组冲突深读。剧透截至本集。'),
                  opening_title=lines(data['openingTitle']), reading_key=e(data['readingKey']),
                  story_title=lines(data['storyTitle']), relation_title=lines(data['relationTitle']),
                  relation_foot=e(data['relationFoot']), conflict_title=lines(data['conflictTitle']),
                  scene_count=len(data['scenes']), person_count=len(data['characters']),
                  quote_count=f'{len(data["quotes"]):02}', source_count=len(data['sources']),
                  airdate=e(data['airdate']), writer=e(data['writer']), director=e(data['director']),
                  prologue_label=e(data['prologue']['label']),
                  ending_title=lines(data['ending']['title']), ending_copy=lines(data['ending']['copy']),
                  ending_known=e(data['ending']['known']), ending_unknown=e(data['ending']['unknown']))
    values['chapter_nav'] = ''.join(f'<a href="#act-{e(a["id"])}"><b>{e(a["number"])}</b><span>{e(a["title"])}<small>{e(a["deck"])}</small></span><em>{e(a["range"])} ↘</em></a>' for a in data['acts'])
    graph = ''
    for index, edge in enumerate(data['relationships']):
        x1, y1 = positions[edge['from']]; x2, y2 = positions[edge['to']]
        ax, ay, bx, by = x1 * 7.6, y1 * 5.6, x2 * 7.6, y2 * 5.6
        label_x, label_y = (ax+bx)/2, (ay+by)/2 - 9
        shift = edge.get('labelShift', [0, 0]); label_x += shift[0]; label_y += shift[1]
        graph += f'<path class="{e(edge["kind"])}-edge" d="M{ax:.1f} {ay:.1f} L{bx:.1f} {by:.1f}"/><text id="edge-{index}" x="{label_x:.1f}" y="{label_y:.1f}">{e(data["phases"][0]["edges"][index])}</text>'
    values['graph_edges'] = graph
    feature = data['feature']
    values['feature_title'] = lines(feature['title'])
    values['feature_intro'] = e(feature['intro'])
    values['feature_steps'] = ''.join(f'<a class="feature-step" href="#scene-{e(step["scene"])}"><b>{i:02}</b><h3>{e(step["title"])}</h3><p>{e(step["text"])}</p><span>回看剧情 ↗</span></a>' for i,step in enumerate(feature['steps'],1))
    values['feature_pair'] = ''.join(f'<figure>{photo(key)}</figure>' for key in feature['pair'])
    values['feature_analysis'] = e(feature['analysis'])
    values['prologue_refs'] = ''.join(f'<a class="ref" href="#source-{e(key)}">[{list(s["id"] for s in data["sources"]).index(key)+1}]</a>' for key in data['prologue']['sources'])


def build_catalogue(complete=False):
    entries, cards = [], []
    e = lambda value: escape(str(value), quote=True)
    for number, title in enumerate(TITLES, 1):
        path = SHOW / f's01e{number:02}/content.json'
        if not path.is_file():
            assert not complete, f'Missing episode {number}'
            continue
        data = json.loads(path.read_text()); images = {p['id']: p for p in data['images']}; hero = images[data['hero']]
        question = data['question'].replace('|', '')
        image_path = f's01e{number:02}/' + hero['file']
        entry = dict(number=number, title=title, question=question, intro=data.get('deck', data['intro']).replace('|',''),
                     hero=image_path, heroAlt=hero['alt'], sceneCount=len(data['scenes']),
                     conflictCount=len(data['conflicts']), characterCount=len(data['characters']),
                     href=f's01e{number:02}/')
        entries.append(entry)
        cards.append(f'<article class="season-card" id="episode-{number:02}"><a class="season-card-image" href="{entry["href"]}" target="_blank" rel="noopener"><img src="{e(image_path)}" alt="{e(hero["alt"])}" width="{hero["width"]}" height="{hero["height"]}" loading="lazy"><span>{number:02}</span></a><div class="season-card-copy"><div class="eyebrow red">S01E{number:02} / {e(title.upper())}</div><h2><a href="{entry["href"]}" target="_blank" rel="noopener">{e(question)}</a></h2><p>{e(entry["intro"])}</p><div class="season-card-meta"><span>{entry["sceneCount"]} 个剧情节点 · {entry["conflictCount"]} 组冲突</span><a href="{entry["href"]}" target="_blank" rel="noopener">打开档案 ↗</a></div></div></article>')
    metadata = dict(season=1, complete=len(entries) == 10, episodeCount=len(entries), episodes=entries)
    (SHOW / 'season.json').write_text(json.dumps(metadata,ensure_ascii=False,indent=2)+'\n')
    navigation = ''.join(f'<a href="#episode-{n:02}">{n:02}<span>{e(TITLES[n-1])}</span></a>' for n in range(1,len(entries)+1))
    total_scenes = sum(item['sceneCount'] for item in entries)
    page = Template((SHOW / 'shared/catalogue.html').read_text()).substitute(cards=''.join(cards), navigation=navigation, total_scenes=total_scenes)
    (SHOW / 'index.html').write_text(page)
    print(f'Rendered catalogue: {len(entries)} episodes, {total_scenes} scenes')


def build(number=1):
    EPISODE = SHOW / f's01e{number:02}'
    data = json.loads((EPISODE / 'content.json').read_text())
    registry = json.loads((SHOW / 'shared' / 'portraits.json').read_text())['characters']
    validate(data, EPISODE, registry)
    portraits = {key: registry[key] for key in data['characters']}
    images = {item['id']: item for item in data['images']}
    sources = {item['id']: item for item in data['sources']}
    e = lambda value: escape(str(value), quote=True)
    words = sum(len(q['en'].split()) for q in data['quotes'])

    def image_tag(key, lazy=True):
        item = images[key]
        loading = ' loading="lazy"' if lazy else ''
        return f'<img src="{e(item["file"])}" alt="{e(item["alt"])}" width="{item["width"]}" height="{item["height"]}"{loading}>'

    def photo(key):
        return image_tag(key) + f'<figcaption>{e(images[key]["caption"])}</figcaption>'

    def avatar(key):
        p = portraits[key]
        x, y = p['position'].split()
        return f'<span class="portrait" style="--face-x:{x};--face-y:{y};--ratio:{p["ratio"]};--zoom:{p["zoom"]}"><img src="../shared/{e(p["file"])}" alt="{e(p["name"])}的剧中角色照" width="128" height="128" loading="lazy"></span>'

    def person_detail(key):
        p, c = portraits[key], data['characters'][key]
        return f'<div class="detail-heading">{avatar(key)}<div><h3>{e(p["name"])}</h3><small>{e(p["en"])}</small></div></div><p class="detail-role">{e(c["role"])}</p><h4>他 / 她想要什么 · 人物阅读</h4><p class="want">{e(c["want"])}</p><h4>手中有什么</h4><p>{e(c["leverage"])}</p><h4>本集行动 · 剧情事实</h4><p>{e(c["fact"])}</p><h4>冲突位置 · 个人解读</h4><p>{e(c["analysis"])}</p><div class="phase-detail"><strong>{e(data["phases"][0]["name"])}</strong><p>{e(data["phases"][0]["details"][key])}</p></div><div class="portrait-credit">{e(p["actor"])} 饰 · {e(p["credit"])}</div>'

    def conflict_html(conflict):
        return f'<figure class="conflict-photo">{photo(conflict["image"])}</figure><article class="conflict-copy"><div class="conflict-axis"><span>{e(conflict["left"])}</span><b>×</b><span>{e(conflict["right"])}</span></div><h3>{e(conflict["title"])}</h3><p>{e(conflict["text"])}</p><p>{e(conflict["second"])}</p><p class="fact-boundary">{e(conflict["limit"])}</p></article>'

    def quote_html(quote):
        return f'<div class="speaker">{e(quote["speaker"])}</div><blockquote lang="en">{e(quote["en"])}</blockquote><p class="translation">{e(quote["zh"])}<small>中文自译</small></p><h4>这句话发生在哪里</h4><p class="quote-context">{e(quote["context"])}</p><h4>没有说透的部分 · 个人解读</h4><p class="quote-analysis">{e(quote["analysis"])}</p>'

    acts = ''
    for act in data['acts']:
        scenes = ''
        for index, scene in enumerate(data['scenes'], 1):
            if scene['act'] != act['id']:
                continue
            refs = ''.join(f'<a class="ref" href="#source-{e(key)}" aria-label="查看第{list(sources).index(key)+1}项剧情依据">[{list(sources).index(key)+1}]</a>' for key in scene['sources'])
            scenes += f'<article class="scene" id="scene-{e(scene["id"])}"><div class="scene-top"><span class="scene-number">{index:02}</span><div><small>{e(scene["where"])}</small><h4>{e(scene["title"])}</h4></div></div><figure class="scene-photo">{photo(scene["image"])}<button class="zoom-photo" data-image="{e(scene["image"])}" aria-label="查看第{index}个场景的完整剧照">↗</button></figure><p class="scene-fact fact"><span>剧情事实</span>{e(scene["fact"])} {refs}</p><details class="scene-analysis" open><summary>这一场为什么重要 · 个人解读</summary><p>{e(scene["analysis"])}</p></details><p class="scene-turn"><span>因此 →</span>{e(scene["turn"])}</p></article>'
        extra = ''
        if number == 1 and act['id'] == 'belong':
            extra = f'<aside class="spaces"><div class="spaces-head"><h3>两间办公室，两种起跑位置。</h3><span>FRAME PAIR / 画面对照</span></div><div class="space-grid"><figure>{photo("office-wide")}</figure><figure>{photo("hhm-wide")}</figure></div><p><strong>个人解读：</strong>后屋里的吉米需要先用表演补上门面，HHM 的空间却已经替律师传达了稳定与可靠。两张画面对照的不是谁有资格做律师，而是谁更容易在开口之前就被相信。这种差距解释了吉米的焦虑，无法自动替他的骗局辩护。</p></aside>'
        acts += f'<section class="act" id="act-{e(act["id"])}"><div class="act-heading"><span class="act-roman">{e(act["number"])}</span><div><h3>{e(act["title"])}</h3><p>{e(act["deck"])}</p></div><small>{e(act["range"])}</small></div><div class="scene-grid">{scenes}</div><div class="act-summary"><strong>这一幕推进了什么</strong><p>{e(act["summary"])}</p></div>{extra}</section>'
    positions = {'jimmy':(50,50), 'chuck':(50,12), 'howard':(13.2,30.4), 'kim':(86.8,30.4), 'mike':(13.2,71.4), 'betsy':(38.2,84.8), 'craig':(61.8,84.8), 'tuco':(86.8,71.4)}
    labels = {'jimmy':'律师 / 讲述者', 'chuck':'家人 / 原则', 'howard':'机构 / 位置', 'kim':'熟悉 / 边界', 'mike':'程序 / 栏杆', 'betsy':'决策 / 体面', 'craig':'调查 / 委托', 'tuco':'结尾 / 风险'}
    central = data.get('central', 'jimmy')
    if number > 1:
        slots = [(50,11),(86,29),(86,73),(63,88),(27,88),(13,67),(13,29),(50,88)]
        outer = [key for key in portraits if key != central]
        if len(outer) == 4: slots = [(25,18),(78,18),(25,83),(78,83)]
        elif len(outer) == 5: slots = [(50,11),(86,36),(76,84),(24,84),(13,36)]
        elif len(outer) == 6: slots = [(50,11),(86,29),(86,76),(50,88),(14,76),(14,29)]
        positions = {central:(50,49), **dict(zip(outer, slots))}
        labels = {key:data['characters'][key]['role'].split('/')[0].strip() for key in portraits}
    people = ''.join(f'<button class="node {key}{" central" if key == central else ""}" data-person="{key}" style="left:{position[0]}%;top:{position[1]}%" aria-pressed="{str(key == central).lower()}" aria-label="查看{e(portraits[key]["name"])}的本集档案">{avatar(key)}<strong>{e(portraits[key]["name"])}</strong><small>{e(labels[key])}</small></button>' for key,position in positions.items())
    values = dict(intro=e(data['intro']), spoiler=e(data['spoiler']), acts=acts, people=people, initial_person=person_detail(central), initial_conflict=conflict_html(data['conflicts'][0]), initial_quote=quote_html(data['quotes'][0]), quote_words=words, graph_note=e(data['phases'][0]['note']), danger_edge='尚未关联')
    for i, label in enumerate(data['phases'][0]['edges']):
        values[f'edge{i}'] = e(label)
    values['phase_tabs'] = ''.join(f'<button data-phase="{p["id"]}" aria-pressed="{str(i == 0).lower()}">{e(p["name"])}</button>' for i,p in enumerate(data['phases']))
    values['conflict_tabs'] = ''.join(f'<button data-conflict="{c["id"]}" aria-pressed="{str(i == 0).lower()}">{e(c["label"])}</button>' for i,c in enumerate(data['conflicts']))
    for field in ['title', 'fact', 'analysis']:
        values['prologue_'+field] = e(data['prologue'][field])
    values['prologue_photo'] = photo(data['prologue']['image'])
    for prefix,key in [('hero',data['hero']),('quote',data['quotes'][0]['image'])]:
        item = images[key]
        for field in ['src', 'alt', 'width', 'height', 'caption']:
            values[prefix+'_'+field] = e(item['file'] if field == 'src' else item[field])
    values['motifs'] = ''.join(f'<article class="motif"><span class="motif-number">{e(m["number"])}</span><h3>{e(m["title"])}</h3><p>{e(m["text"])}</p><a href="#scene-{e(m["link"])}">回到相关场景 ↗</a></article>' for m in data['motifs'])
    values['source_list'] = ''.join(f'<li id="source-{e(s["id"])}"><a href="{e(s["url"])}" target="_blank" rel="noopener">{e(s["title"])} ↗</a><span>{e(s["note"])}</span></li>' for s in data['sources'])
    values['image_list'] = ''.join(f'<li>{e(p["caption"])} · <a href="{e(p["originalUrl"])}" target="_blank" rel="noopener">原图</a> / <a href="{e(p["sourceUrl"])}" target="_blank" rel="noopener">源页</a></li>' for p in data['images'])
    values['portrait_list'] = ''.join(f'<li>{e(p["name"])} · {e(p["actor"])} 饰 · {e(p["credit"])} · <a href="{e(p["originalUrl"])}" target="_blank" rel="noopener">原图</a> / <a href="{e(p["sourceUrl"])}" target="_blank" rel="noopener">源页</a></li>' for p in portraits.values())
    values['payload'] = json.dumps(dict(data,portraits=portraits,sourceHash=hashlib.sha256((EPISODE / 'content.json').read_bytes()).hexdigest()),ensure_ascii=False).replace('<','\\u003c')
    no_script_conflicts = ''.join(f'<div class="conflict-layout">{conflict_html(c)}</div>' for c in data['conflicts'][1:])
    no_script_people = ''.join(f'<article class="person-detail">{person_detail(key)}</article>' for key in portraits)
    no_script_quotes = ''.join(f'<div class="quote-layout"><figure class="quote-photo">{photo(q["image"])}</figure><div class="quote-copy">{quote_html(q)}</div></div>' for q in data['quotes'][1:])
    values['no_script_reading'] = f'<noscript><section class="wrap no-script-reading"><div class="eyebrow red">READING CONTINUES / 完整阅读</div><h2>人物档案、其余冲突与台词</h2><p>当前浏览器未启用 JavaScript，以下按顺序展示互动区其余内容。</p><div class="no-script-cast">{no_script_people}</div>{no_script_conflicts}{no_script_quotes}</section></noscript>'
    if number > 1:
        season_values(data, values, images, positions, photo, e)
    template = 'episode.html' if number == 1 else 'season-episode.html'
    page = Template((SHOW / 'shared' / template).read_text()).substitute(values)
    page = page.replace('<footer class="sources wrap"', episode_navigation(number) + '<footer class="sources wrap"', 1)
    (EPISODE / 'index.html').write_text(page)
    print(f'Rendered {data["episode"]} {data["title"]}: {len(data["scenes"])} scenes, {len(images)} images, {len(portraits)} portraits, {words} quoted words')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--episode', type=int, choices=range(1,11))
    parser.add_argument('--complete', action='store_true')
    args = parser.parse_args()
    numbers = [args.episode] if args.episode else (range(1,11) if args.complete else [1])
    for number in numbers:
        build(number)
    build_catalogue(complete=args.complete)
