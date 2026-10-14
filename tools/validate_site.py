#!/usr/bin/env python3
"""Check static navigation, local resources, anchor integrity and image decoding."""
from collections import Counter
from html.parser import HTMLParser
import json
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
    images = list(show.glob('s01e*/assets/*')) + list((show / 'shared' / 'portraits').glob('*'))
    raster_images = [path for path in images if path.suffix.lower() in ['.jpg', '.jpeg', '.png', '.webp', '.gif']]
    extra_images = [path for path in image_paths if path.suffix.lower() in ['.jpg', '.jpeg', '.png', '.webp', '.gif']]
    raster_images = sorted(set(raster_images + extra_images))
    for path in raster_images:
        with Image.open(path) as picture:
            picture.verify()
    print(f'Validated {len(files)} HTML pages, {links} local links/anchors, {len(raster_images)} raster images, {len(portraits)} shared character portraits')


if __name__ == '__main__':
    main()
