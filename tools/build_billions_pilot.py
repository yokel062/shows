#!/usr/bin/env python3
"""Render the Billions pilot and catalogue from reviewed editorial sources."""
import json
from html import escape
from pathlib import Path
from string import Template

ROOT = Path(__file__).resolve().parents[1]
SHOW = ROOT / 'series' / 'billions'
EPISODE = SHOW / 's01e01'


def build():
    data = json.loads((EPISODE / 'content.json').read_text())
    registry = json.loads((SHOW / 'shared' / 'portraits.json').read_text())['characters']
    portraits = {key: registry[key] for key in data['characters']}
    images = {Path(item['file']).stem: item for item in data['images']}
    sources = {item['id']: item for item in data['sources']}
    e = lambda value: escape(str(value), quote=True)
    assert data['version'] == 2 and len(data['scenes']) == 12
    assert len({s['id'] for s in data['scenes']}) == len(data['scenes'])
    assert len(data['quotes']) == 4 and sum(len(q['en'].split()) for q in data['quotes']) <= 25
    assert all(len([s for s in data['scenes'] if s['act'] == a['id']]) == 4 for a in data['acts'])
    for item in data['images']:
        assert (EPISODE / item['file']).is_file()
        assert item['sourceUrl'].startswith('https://') and item['originalUrl'].startswith('https://')
        assert item['kind'] in ['episode-still', 'episode-production-still']
        assert item['width'] > 0 and item['height'] > 0
    for key, person in portraits.items():
        assert (SHOW / 'shared' / person['file']).is_file()
        assert person['actor'] and person['kind'] == 'character-still'
        assert key in data['characters']
        assert all(key in phase['details'] for phase in data['phases'])
    for flow in data['flows']:
        assert all(node['scene'] in {s['id'] for s in data['scenes']} for node in flow['nodes'])
    used_images = set()
    def pic(name):
        used_images.add(name)
        return images[name]
    def image_tag(name, lazy=True):
        item = pic(name)
        loading = ' loading="lazy"' if lazy else ''
        return f'<img src="{e(item["file"])}" alt="{e(item["alt"])}" width="{item["width"]}" height="{item["height"]}"{loading}>'
    def photo(name, label=None):
        item = pic(name)
        caption = label or item['caption']
        return f'<figure>{image_tag(name)}<figcaption>{e(caption)}</figcaption></figure>'
    def avatar(key):
        p = portraits[key]
        return f'<span class="portrait" style="--position:{e(p["position"])};--zoom:{p["zoom"]};--origin:{e(p.get("origin", "50% 50%"))}"><img src="../shared/{e(p["file"])}" alt="{e(p["name"])}的剧中角色照" loading="lazy" width="160" height="160"></span>'
    def person_detail(key):
        p, c = portraits[key], data['characters'][key]
        return f'<div class="detail-heading">{avatar(key)}<div><h3>{e(p["name"])}</h3><small>{e(p["en"])}</small></div></div><p class="detail-role">{e(c["role"])}</p><h4>本集行动 · 剧情事实</h4><p>{e(c["fact"])}</p><h4>人物阅读 · 个人解读</h4><p>{e(c["analysis"])}</p><div class="phase-detail"><strong>{e(data["phases"][0]["name"])}</strong><p>{e(data["phases"][0]["details"][key])}</p></div><div class="portrait-credit">{e(p["actor"])} 饰 · 统一剧中角色照</div>'
    def flow_html(flow):
        nodes = ''
        for i, node in enumerate(flow['nodes'], 1):
            portrait = avatar(node['portrait']) if node['portrait'] else f'<span class="flow-number">{i:02}</span>'
            nodes += f'<a class="flow-node" href="#scene-{e(node["scene"])}">{portrait}<span><strong>{e(node["name"])}</strong><small>{e(node["role"])}</small></span></a>'
        return f'<div class="flow-heading"><h3>{e(flow["title"])}</h3><p>{e(flow["intro"])}</p></div><div class="flow-nodes">{nodes}</div><p class="flow-result">{e(flow["result"])}</p>'
    def quote_html(quote):
        return f'<div class="speaker">{e(quote["speaker"])}</div><blockquote lang="en">{e(quote["en"])}</blockquote><p class="translation">{e(quote["zh"])}</p><h4>这句话发生在哪里</h4><p>{e(quote["context"])}</p><div class="quote-reading"><h4>潜台词 · 个人解读</h4><p>{e(quote["analysis"])}</p></div>'
    acts = ''
    for act in data['acts']:
        cards = ''
        for index, scene in enumerate(data['scenes'], 1):
            if scene['act'] != act['id']:
                continue
            item = pic(scene['image'])
            refs = ''.join(f'<a class="ref" href="#source-{e(key)}" aria-label="查看剧情依据">[{list(sources).index(key)+1}]</a>' for key in scene['sources'])
            detail = f'<p class="scene-detail">{e(scene["detail"])}</p>' if scene.get('detail') else ''
            cards += f'<article class="scene" id="scene-{e(scene["id"])}" data-index="{index}" data-lane="{e(scene["lane"])}"><div class="scene-top"><span class="scene-num">{index:02}</span><div class="scene-title"><small>{e(scene["where"])}</small><h4>{e(scene["title"])}</h4></div></div><figure class="scene-photo">{image_tag(scene["image"])}<button class="zoom-photo" data-image="{e(scene["image"])}" aria-label="查看第{index}个场景的完整图片">↗</button><figcaption class="caption">{e(item["caption"])}</figcaption></figure><p class="scene-fact"><span class="fact-tag">剧情事实</span>{e(scene["fact"])}{refs}</p><details class="scene-analysis" open><summary>这一场为什么重要 · 个人解读</summary><p>{e(scene["analysis"])}</p></details><p class="scene-turn">{e(scene["turn"])}</p>{detail}</article>'
        evidence = ''
        if act['id'] == 'pressure':
            evidence = f'<aside class="evidence"><div class="evidence-images">{photo("axe-basketball", "现场说出的结论 · 本集篮球场截图")}{photo("warehouse", "结论背后的信息来源 · 本集工厂插叙截图")}</div><div class="evidence-copy"><div class="eyebrow">EVIDENCE PAIR / 并排再看</div><h3>赛场边只听见答案，<br>工厂里才看见它的来处。</h3><p>同一笔交易的两个画面，回答不同问题：意见为什么被接受？这份把握怎样获得？插叙让观众知道的，比交易现场正式说出的更多。<a href="#scene-certainty">回看节点 06 ↗</a></p></div></aside>'
        acts += f'<section class="act" id="act-{act["id"]}"><div class="act-heading"><span class="roman">{act["number"]}</span><div><h3>{e(act["title"])}</h3><p>{e(act["deck"])}</p></div><span class="range">{act["range"]}</span></div><div class="scene-grid">{cards}</div><div class="act-summary"><strong>这一幕推进了什么</strong><p>{e(act["summary"])}</p></div>{evidence}</section>'
    keys = ['chuck','axe','wendy']
    cast_labels = {'chuck':'规则 / 起诉 / 不能输','axe':'信息 / 声誉 / 不愿屈服','wendy':'专业 / 婚姻 / 自己的事业'}
    cast_strip = ''.join(f'<a class="cast-item" href="#relations">{avatar(key)}<div><small>{e(portraits[key]["en"])}</small><p><strong>{e(portraits[key]["name"])}</strong></p><p>{cast_labels[key]}</p></div></a>' for key in keys)
    main_people = ''.join(f'<button class="person {key}" data-person="{key}" aria-pressed="{str(key == "wendy").lower()}" aria-label="查看{e(portraits[key]["name"])}的关系">{avatar(key)}<strong>{e(portraits[key]["name"])}</strong><small>{e(portraits[key]["en"])}</small></button>' for key in keys)
    support_people = ''.join(f'<button class="support-person" data-person="{key}" aria-pressed="false" aria-label="查看{e(portraits[key]["name"])}的关系">{avatar(key)}<strong>{e(portraits[key]["name"])}</strong></button>' for key in ['senior','lara','bryan','hall'])
    phase_tabs = ''.join(f'<button data-phase="{p["id"]}" aria-pressed="{str(i == 0).lower()}">{e(p["name"])}</button>' for i,p in enumerate(data['phases']))
    values = dict(intro=e(data['intro']),opening_fact=e(data['openingFact']),opening_reading=e(data['openingReading']),acts=acts,cast_strip=cast_strip,main_people=main_people,support_people=support_people,phase_tabs=phase_tabs,graph_note=e(data['phases'][0]['note']),initial_person=person_detail('wendy'),initial_flow=flow_html(data['flows'][0]),initial_quote=quote_html(data['quotes'][0]),chuck_warning_photo=photo('chuck-bryan','查克与 Bryan 讨论时机 · 本集配图，不冒充警告原句的镜头'),wendy_warning_photo=photo('axe-office','与温迪谈话中的阿克斯 · 本集办公室截图'))
    for i in range(3):
        values[f'edge{i}'] = e(data['phases'][0]['edges'][i])
    for prefix,name in [('hero',data['hero']),('quote',data['quotes'][0]['image']),('closing','closing-house')]:
        item = pic(name)
        for field in ['src','alt','width','height','caption']:
            values[prefix+'_'+field] = e(item['file'] if field == 'src' else item[field])
    for q in data['quotes']:
        pic(q['image'])
    rendered_images = [item for name,item in images.items() if name in used_images]
    values['source_list'] = ''.join(f'<li id="source-{e(s["id"])}"><a href="{e(s["url"])}" target="_blank" rel="noopener">{e(s["title"])} ↗</a><span>{e(s["note"])}</span></li>' for s in data['sources'])
    values['image_list'] = ''.join(f'<li>{e(item["caption"])} · <a href="{e(item["originalUrl"])}" target="_blank" rel="noopener">原图</a> / <a href="{e(item["sourceUrl"])}" target="_blank" rel="noopener">源页</a></li>' for item in rendered_images)
    values['portrait_list'] = ''.join(f'<li>{e(p["name"])} · {e(p["actor"])} 饰 · <a href="{e(p["originalUrl"])}" target="_blank" rel="noopener">原图</a> / <a href="{e(p["sourceUrl"])}" target="_blank" rel="noopener">源页</a></li>' for p in portraits.values())
    values['payload'] = json.dumps(dict(data,portraits=portraits),ensure_ascii=False).replace('<','\\u003c')
    page = Template((SHOW / 'shared' / 'episode.html').read_text()).substitute(values)
    (EPISODE / 'index.html').write_text(page)
    hero = images[data['hero']]
    catalogue = f'''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="theme-color" content="#161c20"><meta name="description" content="《亿万》图文阅读档案，当前收录第一季第一集 Pilot。"><title>亿万 · 阅读档案 — 剧中人</title><link rel="icon" href="shared/emblem.svg" type="image/svg+xml" sizes="any"><link rel="stylesheet" href="shared/episode.css?v=2"></head><body><header class="masthead"><a class="brand" href="../../"><b>✦</b>剧中人</a><a class="episode-label" href="../../">全部作品 ↗</a></header><main class="catalogue wrap"><div class="eyebrow">THE POWER FILES / 权力的剧场</div><h1>BILLIONS <span>亿万</span></h1><p>用画面跟上选择，用关系理解动机。当前收录：第一季第一集。</p><article class="catalogue-card"><a href="s01e01/" target="_blank" rel="noopener"><img src="s01e01/{e(hero['file'])}" alt="{e(hero['alt'])}" width="{hero['width']}" height="{hero['height']}"></a><div class="catalogue-copy"><div class="eyebrow">SEASON 01 / EPISODE 01 · PILOT</div><h2>谁能决定，游戏的规则？</h2><p>从一条异常交易线索，到一栋海边豪宅。三幕、十二个节点，讲清查克的试探、阿克斯的反制，以及温迪坚持的职业边界。</p><p style="margin-top:14px">人物关系 · 消息流 · 场景对照 · 台词笔记<br>只剧透 S01E01 结尾；配图与解读默认完整展示。</p><a class="read-link" href="s01e01/" target="_blank" rel="noopener">打开首集图解 ↗</a></div></article><p class="catalogue-credit">封面：首集走廊交锋宣传剧照 · Showtime / Edna。详细来源见单集篇末。</p></main><footer class="sources wrap"><div class="footer-bottom"><a href="../../">← 全部作品</a><a href="https://github.com/yokel062/shows">源码与内容 / GitHub ↗</a></div></footer></body></html>'''
    (SHOW / 'index.html').write_text(catalogue+'\n')
    print(f'Rendered Billions v2: 3 acts, 12 scenes, {len(rendered_images)} editorial images, {len(portraits)} portraits')


if __name__ == '__main__':
    build()
