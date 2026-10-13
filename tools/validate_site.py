#!/usr/bin/env python3
"""Check static navigation, local resources, anchor integrity and image decoding."""
from collections import Counter
from html.parser import HTMLParser
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
        for key, value in attrs:
            if key in ['src', 'href'] and value:
                self.links.append(value)


def main():
    files = [ROOT / 'index.html', ROOT / 'series' / 'band-of-brothers' / 'index.html']
    files.extend(sorted((ROOT / 'series' / 'band-of-brothers').glob('s01e*/index.html')))
    assert len(files) == 12, f'Expected catalogue and ten episode pages; found {len(files)}'
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
    images = list((ROOT / 'series' / 'band-of-brothers').glob('s01e*/assets/*'))
    raster_images = [path for path in images if path.suffix.lower() in ['.jpg', '.jpeg', '.png', '.webp']]
    for path in raster_images:
        with Image.open(path) as picture:
            picture.verify()
    print(f'Validated {len(files)} HTML pages, {links} local links/anchors, {len(raster_images)} raster images')


if __name__ == '__main__':
    main()
