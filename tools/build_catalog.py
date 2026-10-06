#!/usr/bin/env python3
"""Build a reproducible, source-grounded catalog from saved public web reads."""
from __future__ import annotations

import argparse
from collections import Counter
from datetime import date
import json
from pathlib import Path
import re
from urllib.parse import unquote, urlsplit, urlunsplit

ROOT = Path(__file__).resolve().parents[1]
COLORS = {
    'blau': 'blue', 'blue': 'blue', 'grün': 'green', 'green': 'green',
    'schwarz': 'black', 'black': 'black', 'weiß': 'white', 'white': 'white',
    'gelb': 'yellow', 'yellow': 'yellow', 'rot': 'red', 'red': 'red',
    'braun': 'brown', 'brown': 'brown', 'grau': 'grey', 'gray': 'grey',
    'grey': 'grey', 'beige': 'beige', 'orange': 'orange', 'violett': 'violet',
    'lila': 'purple', 'rosa': 'pink', 'rosé': 'pink', 'pink': 'pink',
    'bunt': 'multicolor', 'mehrfarbig': 'multicolor',
}
ATTRIBUTE_KEYS = sorted([
    'Preisgruppe', 'Farbe', 'Härtegrad', 'Strukturtyp', 'Outdoor', 'Synonyme',
    'Gruppe', 'Petrographische Zuordnung', 'Alter', 'Vorkommen', 'Neuheit',
    'Price group', 'Colour', 'Hardness', 'Structure Type', 'Synonyms', 'Group',
    'Petrographic Assignment', 'Age', 'Deposit', 'Novelty', 'Zusammensetzung',
    'Material', 'Gewicht', 'Breite', 'Höhe', 'Länge', 'Dicke',
], key=len, reverse=True)
EXPECTED = {'product': 78, 'stone': 135, 'wood': 7, 'leather': 72, 'fabric': 108}


def canonical(url):
    p = urlsplit(url.strip())
    host = p.netloc.lower().removeprefix('www.')
    return urlunsplit(('https', host, unquote(p.path), p.query, ''))


def clean(text):
    return re.sub(r'【\d+†([^】]+)】', lambda m: m[1].split('†')[0], text).strip()


def parse_result(result):
    text = '\n'.join(c.get('text', '') for c in result.get('content', []) if c.get('type') == 'text')
    for block in re.split(r'\n-{20,}\n', text):
        header = re.search(r'^(.*?) \((https?://[^\n]+)\)\n【([^】]+)】', block)
        if not header:
            continue
        lines = [(int(m[1]), m[2], clean(m[3]))
                 for m in re.finditer(r'^L(\d+)(?:@P([\d-]+))?: ?(.*)$', block, re.M)]
        declared = re.search(r'Total lines: (\d+)', block)
        total = int(declared[1]) if declared else None
        complete = bool(lines) and (total is None or
                    (len(lines) == total and lines[0][0] == 0 and lines[-1][0] == total - 1))
        if not lines or 'Failed to fetch' in block[:700]:
            continue
        yield {
            'source_url': header[2], 'title': header[1] or unquote(urlsplit(header[2]).path.rsplit('/', 1)[-1]),
            'text_quality': ('encoding_artifacts' if any(token in block for token in
                              ('Ó±¼', 'ÐÎ', 'ÜÛ', 'ïç', '\ufffd')) else 'not_flagged'),
            'source_crawled': re.search(r'Crawled: ([^;\n]+)', block)[1]
                              if re.search(r'Crawled: ([^;\n]+)', block) else None,
            'source_line_count': total, 'captured_line_count': len(lines),
            'capture_complete': complete,
            'text': '\n'.join(line for _, _, line in lines),
            'numbered_text': '\n'.join(f'L{n}' + (f'@P{p}' if p is not None else '') + ': ' + line
                                      for n, p, line in lines),
        }


def kind_for(url):
    path = urlsplit(url).path
    for segment, kind in [('stein', 'stone'), ('holz', 'wood'), ('leder', 'leather'), ('stoff-1', 'fabric')]:
        if re.search(r'/material/' + re.escape(segment) + r'/[^/]+\.html$', path):
            return kind
    if re.search(r'/produkte/[^/]+/[^/]+\.html$', path):
        return 'product'
    return None


def parse_attributes(text):
    attrs = {}
    for line in text.splitlines():
        if ' | ' in line:
            key, value = re.split(r'\s*\|\s*', line, maxsplit=1)
            if key in ATTRIBUTE_KEYS and value:
                attrs.setdefault(key, value.strip())
        else:
            for key in ATTRIBUTE_KEYS:
                if line.startswith(key + ' '):
                    value = line[len(key):].strip()
                    if value:
                        attrs.setdefault(key, value)
                    break
    return attrs


def download_labels(text):
    match = re.search(r'^##\s+Downloads\s*\n(.*?)(?=^## |^Weitere Material|\Z)', text, re.M | re.S)
    if not match:
        return []
    rows = []
    for line in match[1].splitlines():
        label = re.sub(r'^\s*\*\s*', '', line).strip()
        fmt = ('dwg' if re.search(r'\bdwg', label, re.I) else
               '3ds' if re.search(r'\b3ds', label, re.I) else
               'pdf' if re.search(r'Produktinformation|Product\s?information', label, re.I) else None)
        if fmt:
            rows.append({'label': label, 'format': fmt, 'url': None, 'status': 'unresolved'})
    return rows


def make_record(page, checked_on, assets):
    url, text = page['source_url'], page['text']
    kind = kind_for(url)
    headings = re.findall(r'^#\s+(.+)$', text, re.M)
    name = headings[0].strip() if headings else page['title'].split(' - ')[0]
    attrs = parse_attributes(text)
    model = re.search(r'Modell[-\s]?Nr\.?\s*:\s*([^\n]+)', text, re.I)
    color_raw = attrs.get('Farbe') or attrs.get('Colour')
    color = COLORS.get((color_raw or '').strip().lower())
    downloads = []
    observed = assets.get(canonical(url), [])
    labels = download_labels(text)
    for option in observed:
        key = (option.get('label'), option.get('url'))
        if key not in {(x.get('label'), x.get('url')) for x in downloads}:
            downloads.append({k: v for k, v in option.items() if k != 'product_source_url'})
    for label in labels:
        if not any(x.get('label') == label['label'] for x in downloads):
            downloads.append(label)
    slabs = []
    for line in text.splitlines():
        match = re.search(r'(?:Platte|Slab)\s+(\d+-\d+)\s+(verfügbar|reserviert|available|reserved)\s+(?:Länge|Length):\s*(\d+)\s*mm\s+(?:Breite|Width):\s*(\d+)\s*mm', line)
        if match:
            slab = {'number': match[1], 'status': match[2], 'length_mm': int(match[3]), 'width_mm': int(match[4])}
            if slab not in slabs:
                slabs.append(slab)
    path = urlsplit(url).path
    slug = path.rsplit('/', 1)[-1].removesuffix('.html')
    return {
        'id': kind + ':' + slug, 'kind': kind, 'category': path.split('/')[-2],
        'name': name, 'model_number': model[1].strip() if model else None,
        'source_url': url, 'source_crawled': page['source_crawled'], 'checked_on': checked_on,
        'capture_complete': page['capture_complete'], 'attributes': attrs,
        'color': color, 'color_original': color_raw, 'description': text,
        'download_options': downloads,
        'available_model_formats': sorted({x['format'] for x in downloads
            if x.get('format') in ('dwg', '3ds') and x.get('status') == 'link_observed' and x.get('url')}),
        'document_source_urls': list(dict.fromkeys(x['url'] for x in downloads
            if x.get('format') == 'pdf' and x.get('url'))),
        'has_image_gallery': bool(re.search(r'\bImage\b', text)), 'slabs': slabs,
    }


def build(root):
    pages, assets = {}, {}
    paths = sorted((root / 'data' / 'raw').glob('*.json'))
    initial = root / 'data' / 'web-snapshots.json'
    if initial.exists():
        paths.append(initial)
    checked_on = None
    attempts = 0
    for path in paths:
        data = json.loads(path.read_text())
        checked_on = max(checked_on or '', data.get('checked_on', '')) or None
        for asset in data.get('assets', []):
            product = asset.get('product_source_url')
            if product:
                assets.setdefault(canonical(product), []).append(asset)
        for result in data.get('batches', []):
            attempts += 1
            for page in parse_result(result):
                page['raw_snapshot'] = str(path.relative_to(root))
                key = canonical(page['source_url'])
                old = pages.get(key)
                if old is None or (page['capture_complete'], page['captured_line_count']) >= (
                    old['capture_complete'], old['captured_line_count']):
                    pages[key] = page
    checked_on = checked_on or date.today().isoformat()
    records = [make_record(page, checked_on, assets) for page in pages.values() if kind_for(page['source_url'])]
    records.sort(key=lambda r: (r['kind'], r['name'].casefold(), r['source_url']))
    counts = dict(Counter(r['kind'] for r in records))
    model_links = sum(1 for r in records for x in r['download_options']
                      if x.get('format') in ('dwg', '3ds') and x.get('url') and x.get('status') == 'link_observed')
    incomplete = [r['source_url'] for r in records if not r['capture_complete']]
    summary = {
        'counts_by_kind': counts, 'total_records': len(records), 'source_pages': len(pages),
        'snapshot_batches': attempts, 'observed_model_links': model_links,
        'products_with_observed_model_links': sum(bool(r['available_model_formats']) for r in records if r['kind'] == 'product'),
        'incomplete_detail_sources': incomplete,
        'expected_detail_counts_from_category_pages': EXPECTED,
        'category_coverage_complete': all(counts.get(k, 0) == n for k, n in EXPECTED.items()) and not incomplete,
    }
    catalog = {'schema_version': 1, 'checked_on': checked_on, 'summary': summary, 'records': records,
               'limitations': ['页面读取日期与搜索服务缓存抓取日期可能不同。',
                              '下载入口已解析不代表 ZIP 内部文件、尺寸或二维/三维属性已经检查。',
                              '库存、价格、下载链接和现行规格须在用户请求时重新核实。',
                              '类别覆盖指所读取目录中可见的产品与材料条目，不代表官网所有新闻、项目与历史版本。']}
    (root / 'data' / 'catalog.json').write_text(json.dumps(catalog, ensure_ascii=False, indent=2) + '\n')
    (root / 'data' / 'source-pages.json').write_text(json.dumps({'checked_on': checked_on, 'pages': list(pages.values())}, ensure_ascii=False, indent=2) + '\n')
    write_index(root, catalog)
    print(json.dumps(summary, ensure_ascii=False, indent=2))


def write_index(root, catalog):
    lines = ['# 官网知识库覆盖与检索索引', '', f"核实日期：{catalog['checked_on']}。", '',
             '目录中的产品和材料详情已经归档；库存和下载可用性仍需实时核实。', '',
             '| 类型 | 条目数 |', '|---|---:|']
    titles = {'product': '产品', 'stone': '石材', 'wood': '木材', 'leather': '皮革', 'fabric': '面料'}
    for kind in EXPECTED:
        lines.append(f"| {titles[kind]} | {catalog['summary']['counts_by_kind'].get(kind, 0)} |")
    lines.extend(['', '## 产品型号索引', '', '| 产品 | 完整型号 | 类别 | 已解析官方模型格式 |', '|---|---|---|---|'])
    for r in catalog['records']:
        if r['kind'] == 'product':
            lines.append(f"| [{r['name']}]({r['source_url']}) | {r['model_number'] or '页面未列明'} | {r['category']} | {', '.join(r['available_model_formats']).upper() or '本次未解析到'} |")
    lines.extend(['', '## 使用', '', '`python tools/query.py "Adler" --kind product --json`', '',
                  '`python tools/query.py --kind stone --color 蓝色 --limit 20 --json`', '',
                  '`python tools/query.py --kind product --format 3ds --json`', '',
                  '完整页面原文与 PDF 文字见 `data/source-pages.json`，通过 `tools/source.py` 精确读取。'])
    (root / 'knowledge').mkdir(exist_ok=True)
    (root / 'knowledge' / 'catalog-index.md').write_text('\n'.join(lines) + '\n')


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=ROOT)
    build(parser.parse_args().root)
