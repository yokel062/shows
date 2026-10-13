#!/usr/bin/env python3
"""Validate episode records and render standalone static reading pages."""
import argparse
import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SHOW = ROOT / 'series' / 'band-of-brothers'
TITLES = ['Currahee', 'Day of Days', 'Carentan', 'Replacements', 'Crossroads', 'Bastogne', 'The Breaking Point', 'The Last Patrol', 'Why We Fight', 'Points']


def attach_portraits(data):
    registry = json.loads((SHOW / 'shared' / 'portraits.json').read_text())
    for character in data['characters']:
        key = registry['aliases'].get(character['id'], character['id'])
        assert key in registry['characters'], f'Missing portrait for {character["id"]}'
        portrait = registry['characters'][key]
        assert (SHOW / 'shared' / portrait['file']).is_file()
        character['portrait'] = {
            'key': key, 'src': '../shared/' + portrait['file'],
            'position': portrait['position'], 'zoom': portrait['zoom'],
            'actor': portrait['actor'], 'sourceUrl': portrait['sourceUrl'],
        }


def esc(value):
    return html.escape(str(value), quote=True)


def update_first_episode_portraits():
    registry = json.loads((SHOW / 'shared' / 'portraits.json').read_text())
    path = SHOW / 's01e01' / 'index.html'
    page = path.read_text()
    credits = []
    for key in ['sink', 'sobel', 'winters', 'nixon']:
        portrait = registry['characters'][key]
        pattern = rf'(<button[^>]*data-person="{key}"[^>]*>).*?(<strong>.*?</button>)'
        def replace(match):
            button = re.sub(r' data-actor="[^"]*"', '', match[1])
            button = button[:-1] + f' data-actor="{esc(portrait["actor"])}">'
            avatar = f'<span class="avatar character-photo" style="--portrait-position:{esc(portrait["position"])};--portrait-zoom:{portrait["zoom"]}"><img src="../shared/{esc(portrait["file"])}" alt="{esc(portrait["name"])}的剧中角色照" loading="lazy" width="160" height="160"></span>'
            return button + avatar + match[2]
        page, count = re.subn(pattern, replace, page, flags=re.DOTALL)
        assert count == 1, f'First episode missing character {key}'
        credits.append(f'<li><a href="{esc(portrait["sourceUrl"])}" target="_blank" rel="noopener">{esc(portrait["name"])} · {esc(portrait["actor"])} 饰 · 全季统一角色照 ↗</a></li>')
    block = '<!-- PORTRAIT_CREDITS_START --><p>人物关系图使用全季统一的剧中角色照，仅用于辨认人物，不代表本集对应镜头。</p><ul>' + ''.join(credits) + '</ul><!-- PORTRAIT_CREDITS_END -->'
    if '<!-- PORTRAIT_CREDITS_START -->' in page:
        page = re.sub(r'<!-- PORTRAIT_CREDITS_START -->.*?<!-- PORTRAIT_CREDITS_END -->', lambda match: block, page, flags=re.DOTALL)
    else:
        page = page.replace('<p>译名采用：', block + '<p>译名采用：')
    path.write_text(page)


def validate(data, directory):
    required = ['episode', 'title', 'chineseTitle', 'subtitle', 'period', 'question', 'intro', 'introSource', 'hero', 'heroAlt', 'heroCaption', 'sources', 'images', 'scenes', 'characters', 'phases', 'relationships', 'comparison', 'quotes', 'motifs', 'ending']
    assert all(key in data for key in required), f'{directory}: missing required fields'
    number = data['episode']
    assert 2 <= number <= 10 and directory.name == f's01e{number:02d}'
    assert data['title'] == TITLES[number - 1], f'{directory}: incorrect title'
    source_ids = [source['id'] for source in data['sources']]
    assert len(source_ids) >= 3 and len(set(source_ids)) == len(source_ids)
    assert all(source['url'].startswith('https://') for source in data['sources'])
    assert 6 <= len(data['scenes']) <= 8
    assert len({scene['id'] for scene in data['scenes']}) == len(data['scenes'])
    assert len({scene['time'] for scene in data['scenes']}) == len(data['scenes'])
    assert 4 <= len(data['characters']) <= 6
    character_ids = {character['id'] for character in data['characters']}
    assert len(character_ids) == len(data['characters'])
    assert len(data['phases']) == 3 and 6 <= len(data['relationships']) <= 9
    assert len(data['quotes']) == 3 and len(data['motifs']) == 3
    quote_words = sum(len(re.findall(r"[A-Za-z]+(?:['’-][A-Za-z]+)*", quote['en'])) for quote in data['quotes'])
    assert quote_words <= 25, f'{directory}: quote word budget exceeded ({quote_words})'
    image_files = {image['file'] for image in data['images']}
    assert len(image_files) >= 2, f'{directory}: insufficient real images'
    assert all((directory / path).is_file() for path in image_files)
    assert all(image['sourceUrl'].startswith('https://') for image in data['images'])
    assert data['hero'] in image_files
    assert data['introSource'] in source_ids
    for collection in ['scenes', 'characters', 'relationships', 'quotes', 'motifs']:
        for item in data[collection]:
            assert item['source'] in source_ids, f'{directory}: unknown source in {collection}'
            if item.get('image'):
                assert item['image'] in image_files, f'{directory}: uncredited image'
    for relation in data['relationships']:
        assert relation['from'] in character_ids and relation['to'] in character_ids
        assert relation['from'] != relation['to']
        assert relation['phases'] and all(phase in [0, 1, 2] for phase in relation['phases'])
        assert relation['type'] in ['trust', 'command', 'conflict', 'care', 'contrast', 'loss', 'tension', 'memory', 'peer']
    assert len(data['comparison']['rows']) == 3
    for side in ['left', 'right']:
        assert data['comparison'][side]['image'] in image_files
    assert data['ending']['image'] in image_files
    for note in data.get('historicalNotes', []):
        assert note['title'] and note['text'] and note['source'] in source_ids
    return quote_words


def render(data):
    number = data['episode']
    sources = {source['id']: index + 1 for index, source in enumerate(data['sources'])}
    images = {image['file']: image for image in data['images']}

    def ref(source):
        return f'<a class="ref" href="#source-{esc(source)}">[{sources[source]}]</a>'

    def image(path, caption=None):
        item = images[path]
        return f'<figure><img src="{esc(path)}" alt="{esc(item["alt"])}" loading="lazy" width="1200" height="675"><figcaption>{esc(caption or item["caption"])}</figcaption></figure>'

    scenes = []
    for index, scene in enumerate(data['scenes']):
        picture = (f'<img src="{esc(scene["image"])}" alt="{esc(scene["caption"])}" loading="lazy" width="1200" height="675"><span class="scene-caption">{esc(scene["caption"])}</span>' if scene.get('image') else f'<div class="scene-graphic"><span class="graphic-icon">{esc(scene.get("graphic", scene["title"]))}</span><p>{esc(scene["where"])}</p><small>剧情示意图</small></div>')
        scenes.append(f'<article class="scene-card" id="scene-{esc(scene["id"])}" data-time="{scene["time"]}" data-screen="{index}"><div class="scene-top"><span class="scene-num">{index+1:02d}</span><div class="scene-location">{esc(scene["where"])}<strong>{esc(scene["title"])}</strong></div></div><div class="scene-picture">{picture}</div><p class="scene-fact"><span class="fact-tag">剧情事实</span>{esc(scene["fact"])}{ref(scene["source"])}</p><details class="scene-analysis" open><summary>这一场为什么重要 · 个人解读</summary><p>{esc(scene["analysis"])}</p></details></article>')

    phase_buttons = ''.join(f'<button data-phase="{i}" class="{"active" if i == 0 else ""}" aria-pressed="{"true" if i == 0 else "false"}"><small>阶段 {i+1:02d}</small>{esc(phase["title"])}</button>' for i, phase in enumerate(data['phases']))
    character_buttons = ''.join(f'<button class="person" data-person="{esc(character["id"])}" aria-label="查看{esc(character["name"])}的关系" aria-pressed="false"><span class="avatar character-photo" style="--portrait-position:{esc(character["portrait"]["position"])};--portrait-zoom:{character["portrait"]["zoom"]}"><img src="{esc(character["portrait"]["src"])}" alt="{esc(character["name"])}的剧中角色照" loading="lazy" width="160" height="160"></span><strong>{esc(character["name"])}</strong><small>{esc(character["en"])}</small></button>' for character in data['characters'])
    comparison = data['comparison']
    leaders = ''.join(f'<article class="leader">{image(comparison[side]["image"])}<div class="leader-name"><h3>{esc(comparison[side]["title"])}</h3></div><p>{esc(comparison[side]["summary"])}</p></article>' for side in ['left', 'right'])
    rows = ''.join(f'<div><small>{esc(row["label"])}</small><p>{esc(row["left"])}</p><span>↔</span><p>{esc(row["right"])}</p></div>' for row in comparison['rows'])
    quote = data['quotes'][0]
    motifs = ''.join(f'<article><span class="motif-number">{i+1:02d}</span><h3>{esc(motif["title"])}</h3><p><span class="fact-tag dark">剧情事实</span>{esc(motif["fact"])}{ref(motif["source"])}</p><p class="motif-analysis"><span>个人解读</span>{esc(motif["analysis"])}</p><div class="mini-diagram">'+ '<b>→</b>'.join(f'<span>{esc(step)}</span>' for step in motif['steps']) +'</div></article>' for i, motif in enumerate(data['motifs']))
    source_list = ''.join(f'<li id="source-{esc(source["id"])}"><a href="{esc(source["url"])}" target="_blank" rel="noopener">{esc(source["title"])} ↗</a><span>{esc(source["note"])}</span></li>' for source in data['sources'])
    image_list = ''.join(f'<li><a href="{esc(item["sourceUrl"])}" target="_blank" rel="noopener">{esc(item["caption"])} ↗</a></li>' for item in data['images'])
    image_list += ''.join(f'<li><a href="{esc(character["portrait"]["sourceUrl"])}" target="_blank" rel="noopener">{esc(character["name"])} · {esc(character["portrait"]["actor"])} 饰 · 全季统一角色照 ↗</a></li>' for character in data['characters'])
    previous = f'<a href="../s01e{number-1:02d}/"><small>上一集 / {number-1:02d}</small>{esc(TITLES[number-2])} <span>←</span></a>'
    next_link = f'<a href="../s01e{number+1:02d}/"><small>下一集 / {number+1:02d}</small>{esc(TITLES[number])} <span>→</span></a>' if number < 10 else '<a href="../"><small>整季阅读完成</small>回到十集目录 <span>↑</span></a>'
    history = ''
    if data.get('historicalNotes'):
        notes = ''.join(f'<article><h3>{esc(note["title"])}</h3><p>{esc(note["text"])}{ref(note["source"])}</p></article>' for note in data['historicalNotes'])
        history = f'<section class="historical-notes content-width" id="historical-notes"><div class="eyebrow">HISTORICAL CONTEXT / 历史补充与校正</div><h2>区分剧集呈现与历史记录。</h2><div>{notes}</div></section>'
    payload = json.dumps(data, ensure_ascii=False).replace('</', '<\\/')
    return f'''<!doctype html>
<html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="theme-color" content="#171c16"><meta name="description" content="《兄弟连》第{number}集 {esc(data['title'])}：剧情时间线、人物关系、台词与主题图解。包含截至第{number}集的剧情。"><title>{esc(data['title'])} · 兄弟连第{number}集图解</title><link rel="icon" href="../s01e01/assets/insignia.svg" type="image/svg+xml"><link rel="stylesheet" href="../shared/episode.css"><link rel="stylesheet" href="../shared/portraits.css"><script src="../shared/episode.js" defer></script></head>
<body><a class="skip" href="#story">跳到剧情梳理</a><div class="reading-progress" aria-hidden="true"><span id="progress"></span></div><header class="masthead"><a class="brand" href="../../../"><span class="brand-mark">✦</span>剧中人 <span class="brand-en">STORY FIELDNOTES</span></a><nav aria-label="章节导航"><a href="../">整季目录</a><a href="#story">剧情</a><a href="#relations">人物</a><a href="#leadership">深读</a><a href="#quotes">台词</a></nav><span class="episode-label">档案 {number:03d} <i></i> S01 · E{number:02d}</span></header>
<main><section class="hero episode-hero" id="top"><img class="hero-image" src="{esc(data['hero'])}" alt="{esc(data['heroAlt'])}" fetchpriority="high" width="1200" height="675"><div class="hero-scrim"></div><div class="hero-content"><div class="eyebrow"><span class="tiny-line"></span>BAND OF BROTHERS / 第 {number:02d} 集</div><h1>{esc(data['title'].upper())}<span>{esc(data['subtitle'])}</span></h1><p class="hero-deck">{esc(data['chineseTitle'])} · {esc(data['period'])}</p><div class="hero-actions"><a class="primary" href="#story">翻开这一集 <span>↓</span></a><span class="scope">包含截至第 {number} 集的剧情<br><small>剧情事实 × 个人解读</small></span></div></div><div class="hero-foot"><span>{number:02d} / {esc(data['title'].upper())}</span><span>{esc(data['period'])}</span><span class="photo-credit">{esc(data['heroCaption'])}</span></div></section>
<section class="opening content-width"><div class="section-index">阅读线索<br><span>THE QUESTION</span></div><div class="opening-text"><h2>{esc(data['question'])}</h2><p>{esc(data['intro'])}{ref(data['introSource'])}</p><p class="interpretation"><span>本页范围</span>回顾本集与必要的前集背景；以下主题分析针对剧集呈现，历史补充另作说明。</p></div><div class="field-stamp"><span>{number:02d}</span><strong>EASY COMPANY</strong><small>101st AIRBORNE<br>FIELDNOTES</small></div></section>
<section id="story" class="story-section"><div class="content-width"><div class="section-heading"><div><div class="eyebrow">01 / THE STORY</div><h2>沿着场景，读懂选择。</h2><p>{len(data['scenes'])} 个关键场景，连起本集的因果与变化。</p></div><div class="segmented" role="group" aria-label="时间线排列顺序"><button class="active" data-order="screen" aria-pressed="true">播出顺序</button><button data-order="time" aria-pressed="false">故事时间</button></div></div><p class="order-note" id="order-note" aria-live="polite">按剧中叙事顺序排列。批注默认展开，可直接阅读场景的意义。</p><div class="timeline" id="timeline">{''.join(scenes)}</div></div></section>
<section id="relations" class="relations-section content-width"><div class="section-heading"><div><div class="eyebrow">02 / THE PEOPLE</div><h2>人物之间，发生了什么？</h2><p>切换阶段，点人物或关系，阅读具体证据。</p></div><span class="margin-label">关系图 · 截至本集</span></div><div class="phase-tabs" role="group" aria-label="人物关系阶段">{phase_buttons}</div><div class="relationship-layout"><div class="graph-panel"><div class="graph-canvas"><svg class="graph-lines" viewBox="0 0 700 510" aria-hidden="true"></svg>{character_buttons}</div><div class="graph-legend"><span><i class="line command"></i>指挥 / 对照</span><span><i class="line conflict"></i>压力 / 失去</span><span><i class="line trust"></i>信任 / 照护</span></div><p class="graph-note" id="graph-note">{esc(data['phases'][0]['note'])}</p><div class="relation-options" id="relation-options" role="group" aria-label="选择人物关系"></div></div><aside class="person-detail" aria-live="polite" aria-atomic="true" id="person-detail"><div class="detail-kicker">PERSONNEL FILE / 人物档案</div><h3>{esc(data['characters'][0]['name'])}</h3><p>{esc(data['characters'][0]['fact'])}</p></aside></div></section>
<section id="leadership" class="leadership-section"><div class="content-width"><div class="section-heading"><div><div class="eyebrow">03 / A CLOSER LOOK</div><h2>{esc(comparison['title'])}</h2><p>用具体场景对照本集的两种处境。</p></div><span class="analysis-badge">个人解读</span></div><div class="leader-pair">{leaders}</div><div class="comparison">{rows}</div><div class="reading-insight"><span>把矛盾留在画面里</span><p>{esc(comparison['conclusion'])}</p></div></div></section>
<section id="quotes" class="quotes-section content-width"><div class="section-heading"><div><div class="eyebrow">04 / BETWEEN THE LINES</div><h2>台词，放回场景里读。</h2><p>短句原文、中文自译，以及它在这一刻的分量。</p></div><span class="margin-label">03 张台词笔记</span></div><div class="quote-layout"><div class="quote-visual"><img id="quote-image" src="{esc(quote['image'])}" alt="{esc(images[quote['image']]['alt'])}" loading="lazy"><span id="quote-scene">台词场景 / {esc(quote['scene'])}</span><div class="quote-controls"><button id="quote-prev" aria-label="上一张台词卡">←</button><span id="quote-count" aria-live="polite">01 / 03</span><button id="quote-next" aria-label="下一张台词卡">→</button></div></div><article class="quote-note" id="quote-note" aria-live="polite" aria-atomic="true"><div class="quote-speaker">{esc(quote['speaker'])}</div><blockquote lang="en">“{esc(quote['en'])}”</blockquote><p class="translation">{esc(quote['zh'])}</p><h4>发生在什么情境</h4><p>{esc(quote['context'])}</p><div class="quote-reading"><h4>放回上下文 · 个人解读</h4><p>{esc(quote['analysis'])}{ref(quote['source'])}</p></div></article></div><p class="quote-foot">英文短句核对来源列在篇末；中文为本页自译。配图的场景与出处随卡片标注。</p></section>
<section class="motifs-section content-width" id="motifs"><div class="section-heading"><div><div class="eyebrow">05 / WHAT TO NOTICE</div><h2>再看一遍，留意这三个细节。</h2><p>只沿本集与此前的线索回看，不揭示后续情节。</p></div></div><div class="motif-grid">{motifs}</div></section>
{history}<section class="closing"><img src="{esc(data['ending']['image'])}" alt="{esc(images[data['ending']['image']]['alt'])}" loading="lazy" width="1200" height="675"><div class="closing-scrim"></div><div class="closing-text"><div class="eyebrow">END OF EPISODE {number:02d}</div><h2>{esc(data['ending']['headline'])}</h2><p>{esc(data['ending']['text'])}</p><a href="#top">回到档案首页 ↑</a></div></section><nav class="episode-navigation content-width" aria-label="前后集导航">{previous}<a class="season-back" href="../"><small>十集阅读档案</small>整季目录</a>{next_link}</nav>
<footer id="sources" class="sources content-width"><div class="source-intro"><div class="eyebrow">READING NOTES / 资料与图像</div><h2>让分析有据可循。</h2><p>本页分析剧集呈现。剧情事实、历史补充与个人解读分别标注；引用资料可能包含更多剧情，首次观看请按需打开。</p></div><ol>{source_list}</ol><details class="asset-sources"><summary>查看图像来源</summary><p>剧集画面版权归 HBO 及相关权利人；用于对应作品的阅读和评论。人物关系图使用全季统一角色照，仅用于辨认人物，不代表本集对应镜头。示意图为本页原创，不作为历史证据。</p><ul>{image_list}</ul></details><div class="footer-bottom"><a class="brand" href="../../../">✦ 剧中人</a><span>BAND OF BROTHERS / {number:03d}</span><a href="../">整季目录 ↑</a></div></footer></main><script type="application/json" id="episode-data">{payload}</script></body></html>'''


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--check', action='store_true', help='Validate records without rendering')
    parser.add_argument('--complete', action='store_true', help='Require all nine new episode records')
    args = parser.parse_args()
    files = sorted(SHOW.glob('s01e*/content.json'))
    if args.complete:
        assert len(files) == 9, f'Expected 9 records; found {len(files)}'
    records = []
    for path in files:
        data = json.loads(path.read_text())
        words = validate(data, path.parent)
        attach_portraits(data)
        if not args.check:
            (path.parent / 'index.html').write_text(render(data))
        records.append({'episode': data['episode'], 'title': data['title'], 'headline': data['subtitle'], 'hero': f'{path.parent.name}/{data["hero"]}', 'alt': data['heroAlt']})
        print(f'{path.parent.name}: {len(data["scenes"])} scenes, {len(data["images"])} images, {words} quoted words')
    if not args.check:
        update_first_episode_portraits()
        script = SHOW / 'shared' / 'season.js'
        current = script.read_text()
        block = '\n'.join('  ' + json.dumps(record, ensure_ascii=False) + ',' for record in records)
        replacement = '/* EPISODE_RECORDS_START */\n' + block + '\n  /* EPISODE_RECORDS_END */'
        if '/* EPISODE_RECORDS */' in current:
            current = current.replace('/* EPISODE_RECORDS */', replacement)
        else:
            current, count = re.subn(r'/\* EPISODE_RECORDS_START \*/.*?/\* EPISODE_RECORDS_END \*/', lambda match: replacement, current, flags=re.DOTALL)
            assert count == 1
        script.write_text(current)


if __name__ == '__main__':
    main()
