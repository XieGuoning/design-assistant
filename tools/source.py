#!/usr/bin/env python3
"""Read one archived official page or product PDF by exact source URL."""
import argparse
import json
from pathlib import Path
from urllib.parse import unquote, urlsplit, urlunsplit

ROOT = Path(__file__).resolve().parents[1]


def canonical(url):
    p = urlsplit(url)
    return urlunsplit(('https', p.netloc.lower().removeprefix('www.'), unquote(p.path), p.query, ''))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('url')
    parser.add_argument('--json', action='store_true')
    args = parser.parse_args()
    path = ROOT / 'data' / 'source-pages.json'
    data = json.loads(path.read_text())
    matches = [p for p in data['pages'] if canonical(p['source_url']) == canonical(args.url)]
    if not matches:
        parser.exit(1, '本地未保存该来源正文。请重新读取官网的对应链接。\n')
    page = matches[0]
    if args.json:
        print(json.dumps(page, ensure_ascii=False, indent=2))
    else:
        print(page['title'])
        print(page['source_url'])
        print('核实日期：' + data['checked_on'] + '；来源缓存抓取时间：' + (page.get('source_crawled') or '未提供'))
        print(page['numbered_text'])


if __name__ == '__main__':
    main()
