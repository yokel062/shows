#!/usr/bin/env python3
"""Check static navigation, local resources, anchor integrity and image decoding."""
from collections import Counter
from html.parser import HTMLParser
import json
import hashlib
import re
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]


class Page(HTMLParser):
    def __init__(self, path):
        super().__init__()
        self.path = path
        self.links = []
        self.ids = []
        self.images = []

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        if attributes.get('id'):
            self.ids.append(attributes['id'])
        if tag == 'img':
            assert attributes.get('alt'), f'{self.path}: image has no description'
            self.images.append(attributes.get('src'))
        if tag == 'details' and 'scene-analysis' in attributes.get('class', '').split():
            assert 'open' in attributes, f'{self.path}: scene analysis must be expanded by default'
        for key, value in attrs:
            if key in ['src', 'href'] and value:
                self.links.append(value)


def main():
    files = [ROOT / 'index.html']
    files.extend(sorted((ROOT / 'series').rglob('index.html')))
    files.extend(sorted((ROOT / 'movies').rglob('index.html')))
    bob_episodes = list((ROOT / 'series' / 'band-of-brothers').glob('s01e*/index.html'))
    assert len(bob_episodes) == 10, f'Expected ten Band of Brothers episodes; found {len(bob_episodes)}'
    pages = {}
    for path in files:
        parser = Page(path)
        parser.feed(path.read_text())
        duplicates = [key for key, count in Counter(parser.ids).items() if count > 1]
        assert not duplicates, f'{path}: duplicate anchors {duplicates}'
        pages[path.resolve()] = parser
    links = 0
    image_paths = set()
    for path, page in pages.items():
        for value in page.links:
            url = urlsplit(value)
            if url.scheme or url.netloc:
                continue
            target = (path.parent / unquote(url.path)).resolve() if url.path else path
            if target.is_dir():
                target /= 'index.html'
            assert target.is_relative_to(ROOT), f'{path}: local link leaves the project: {value}'
            assert target.is_file(), f'{path}: missing target: {value}'
            if url.fragment and target in pages:
                assert unquote(url.fragment) in pages[target].ids, f'{path}: broken anchor: {value}'
            links += 1
        for image in page.images:
            image_paths.add((path.parent / image).resolve())
    from PIL import Image
    show = ROOT / 'series' / 'band-of-brothers'
    registry = json.loads((show / 'shared' / 'portraits.json').read_text())
    portraits = registry['characters']
    assert all(key in portraits for key in registry['aliases'].values())
    for key, portrait in portraits.items():
        assert portrait['actor'] and portrait['kind'] == 'character-still'
        assert portrait['sourceUrl'].startswith('https://') and portrait['originalUrl'].startswith('https://')
        assert .8 <= portrait['zoom'] <= 3
        assert re.fullmatch(r'\d+% \d+%', portrait['position'])
        assert (show / 'shared' / portrait['file']).resolve().is_relative_to(show / 'shared' / 'portraits')
        assert (show / 'shared' / portrait['file']).is_file(), f'Missing portrait: {key}'
    for path in show.glob('s01e*/content.json'):
        source = json.loads(path.read_text())
        page = (path.parent / 'index.html').read_text()
        payload = json.loads(re.search(r'<script type="application/json" id="episode-data">(.*?)</script>', page, re.DOTALL)[1])
        for character, rendered in zip(source['characters'], payload['characters'], strict=True):
            key = registry['aliases'].get(character['id'], character['id'])
            expected = '../shared/' + portraits[key]['file']
            assert rendered['portrait']['key'] == key and rendered['portrait']['src'] == expected
            assert expected in pages[(path.parent / 'index.html').resolve()].images
    first = show / 's01e01'
    assert '<details class="scene-analysis" open>' in (first / 'app.js').read_text()
    for key in ['sink', 'sobel', 'winters', 'nixon']:
        assert '../shared/' + portraits[key]['file'] in pages[(first / 'index.html').resolve()].images
    billions = ROOT / 'series' / 'billions'
    from build_billions import SEASON_TITLES, validate
    billions_portraits = json.loads((billions / 'shared' / 'portraits.json').read_text())['characters']
    checked_seasons = []
    for season_number in SEASON_TITLES:
        metadata = billions / ('season.json' if season_number == 1 else f'season-{season_number}/season.json')
        if not metadata.is_file():
            assert season_number != 1
            assert not any(billions.glob(f's{season_number:02}e??/content.json')), f'Billions season {season_number} has source files but no catalogue; run the season builder'
            continue
        season = json.loads(metadata.read_text())
        assert season['season'] == season_number and season['complete']
        assert [e['episode'] for e in season['episodes']] == list(range(1, 13)), f'Billions season {season_number} must contain all twelve episodes'
        checked_seasons.append(season_number)
        for number in range(1, 13):
            directory = billions / f's{season_number:02}e{number:02}'
            source = json.loads((directory / 'content.json').read_text())
            source.setdefault('episode', number)
            source.setdefault('season', season_number)
            assert (source['season'], source['episode']) == (season_number, number), f'{directory}: wrong source identity'
            validate(source, directory, billions_portraits)
            html = (directory / 'index.html').read_text()
            payload = json.loads(re.search(r'<script type="application/json" id="episode-data">(.*?)</script>', html, re.DOTALL)[1])
            if (season_number, number) == (1, 1):
                assert (payload.get('season', 1), payload.get('episode', 1)) == (1, 1), f'{directory}: wrong pilot identity'
            else:
                assert (payload['season'], payload['episode']) == (season_number, number), f'{directory}: wrong rendered identity'
            for key, value in source.items():
                if key in ['episode', 'season', 'sources']:
                    continue
                assert payload[key] == value, f'{directory}: stale rendered field {key}'
            for item in source['sources']:
                assert item in payload['sources'], f'{directory}: stale rendered source {item["id"]}'
            rendered_page = pages[(directory / 'index.html').resolve()]
            for scene in source['scenes']:
                assert 'scene-' + scene['id'] in rendered_page.ids
            assert html.count('<details class="scene-analysis" open>') == len(source['scenes'])
            for key in source['characters']:
                assert payload['portraits'][key] == billions_portraits[key], f'{directory}: stale portrait {key}'
                assert '../shared/' + billions_portraits[key]['file'] in rendered_page.images
            for item in source['images']:
                with Image.open(directory / item['file']) as picture:
                    assert picture.size == (item['width'], item['height']), f'{directory}: wrong image dimensions'
    succession = ROOT / 'series' / 'succession'
    if succession.is_dir():
        season = json.loads((succession / 'season.json').read_text())
        assert season['complete'] and [e['episode'] for e in season['episodes']] == list(range(1, 11))
        registry = json.loads((succession / 'shared/portraits.json').read_text())['characters']
        for number, entry in enumerate(season['episodes'], 1):
            directory = succession / f's01e{number:02}'
            path = directory / 'content.json'
            data = json.loads(path.read_text())
            html = (directory / 'index.html').read_text()
            payload = json.loads(re.search(r'<script type="application/json" id="episode-data">(.*?)</script>', html, re.DOTALL)[1])
            assert payload['sourceHash'] == hashlib.sha256(path.read_bytes()).hexdigest(), f'{directory}: stale editorial source'
            people = {p['id']: registry[p['id']] for p in data['characters']}
            digest = hashlib.sha256(json.dumps(people, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
            assert payload['portraitHash'] == digest, f'{directory}: stale registered portraits'
            assert payload['images'] == data['images'] and payload['phases'] == data['phases']
            assert entry['title'] == data['title'] and entry['question'] == data['question'].replace('|', '')
            assert entry['sceneCount'] == len(data['scenes']) and entry['conflictCount'] == len(data['conflicts'])
            assert html.count('<details class="scene-analysis" open>') == len(data['scenes'])
            assert sum(len(q['en'].split()) for q in data['quotes']) <= 25
            rendered = pages[(directory / 'index.html').resolve()]
            for scene in data['scenes']:
                assert 'scene-' + scene['id'] in rendered.ids
            for person in data['characters']:
                portrait = registry[person['id']]
                assert portrait['actor'] and portrait['kind'] == 'character-still'
                assert '../shared/' + portrait['file'] in rendered.images
            for item in data['images']:
                assert item['kind'] == 'episode-still' and item['episode'] == f'S01E{number:02}'
                assert item['originalUrl'].endswith(f'S_S1_E{number}_{item["frame"]:04}.jpg')
                with Image.open(directory / item['file']) as picture:
                    assert picture.size == (item['width'], item['height'])
        print('Succession: all ten episodes match editorial sources, catalogues and portrait registration')
    images = list(show.glob('s01e*/assets/*')) + list((show / 'shared' / 'portraits').glob('*'))
    images += list(billions.glob('s??e??/assets/*')) + list((billions / 'shared' / 'portraits').glob('*'))
    raster_images = [path for path in images if path.suffix.lower() in ['.jpg', '.jpeg', '.png', '.webp', '.gif']]
    extra_images = [path for path in image_paths if path.suffix.lower() in ['.jpg', '.jpeg', '.png', '.webp', '.gif']]
    raster_images = sorted(set(raster_images + extra_images))
    for path in raster_images:
        with Image.open(path) as picture:
            picture.verify()
    print(f'Validated {len(files)} HTML pages, {links} local links/anchors, {len(raster_images)} raster images, {len(portraits) + len(billions_portraits)} shared character portraits; Billions seasons {checked_seasons} data matches rendered pages')


if __name__ == '__main__':
    main()
