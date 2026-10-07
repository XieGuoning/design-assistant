#!/usr/bin/env python3
"""Page-level nobilia retrieval; query needs only the Python standard library."""
import argparse
import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'data/nobilia/2026'
TOPICS = [
 ('导言与总览', ['总览', '介绍', '导言']),
 ('门板', ['门板', 'front', 'fronts']),
 ('设计总览、配置与特殊制作', ['定制', '特殊制作', '配置', 'special productions']),
 ('地柜', ['地柜', 'base units']),
 ('台面、墙面板、石英石与陶瓷', ['台面', '挡水板', '墙面板', '石英石', '陶瓷', 'worktop', 'quartz', 'ceramic']),
 ('侧板、顶板、Sakura、装饰柱与壁架', ['侧板', '顶板', '壁架', '装饰柱', 'sakura']),
 ('半高柜与高柜', ['高柜', '半高柜', 'tall units', 'highboard']),
 ('吊柜', ['吊柜', 'wall units']),
 ('LINE N 无拉手厨房', ['无拉手', '无把手', 'line n', 'handleless']),
 ('厨房以外空间（文件后部含第10章）', ['卫浴', '客厅', '衣帽间', '厨房以外', 'more than kitchen']),
]
ALIASES = {
 '门板': ['front'], '台面': ['worktop'], '石英石': ['quartz'], '陶瓷': ['ceramic'],
 '抽屉': ['drawer'], '拉篮': ['pull-out'], '水槽': ['sink'], '转角': ['corner'],
 '洗碗机': ['dishwasher'], '冰箱': ['refrigerator', 'fridge'], '烤箱': ['oven'],
 '高度': ['height'], '宽度': ['width'], '深度': ['depth'], '尺寸': ['dimensions'],
 '安装': ['installation'], '把手': ['handle'], '拉手': ['handle'],
 '踢脚板': ['plinth'], '照明': ['lighting'], '玻璃': ['glass'], '橡木': ['oak'],
 '颜色': ['colour', 'color'], '承重': ['load'], '定制': ['special'],
}

def build(source, allow_incomplete=False):
 from pypdf import PdfReader
 files = sorted(Path(source).rglob('*.pdf'), key=lambda p:p.name)
 files = [p for p in files if re.match(r'0[0-9]_', p.name)]
 if len({p.name[:2] for p in files}) != len(files):
  raise ValueError('Duplicate source file IDs; merge split parts before importing')
 if not files or (len(files) != 10 and not allow_incomplete):
  raise ValueError('Expected PDFs 00–09; use --allow-incomplete to explicitly record missing files')
 docs = []
 for src in files:
  chapter = src.name[:2]
  dest = DATA / 'pdf' / src.name
  dest.parent.mkdir(parents=True, exist_ok=True)
  if dest.exists() and dest.read_bytes() != src.read_bytes():
   raise ValueError(f'Refusing to overwrite changed original: {dest}')
  if src.resolve() != dest.resolve():
   shutil.copyfile(src, dest)
  reader = PdfReader(dest)
  # Poppler layout preserves spacing in tables; neither layout nor text proves cell associations.
  text = subprocess.run(['pdftotext', '-layout', str(dest), '-'], check=True, capture_output=True).stdout.decode('utf-8')
  pages = text.split('\f')
  if pages[-1].strip() == '':
   pages.pop()
  if len(pages) != len(reader.pages):
   raise ValueError(f'Page count mismatch: {src.name}')
  records = []
  directory = DATA / 'pages' / chapter
  directory.mkdir(parents=True, exist_ok=True)
  for number, body in enumerate(pages, 1):
   path = directory / f'{number:03}.txt'
   path.write_text(body, encoding='utf-8')
   records.append({'manual_chapter': '10' if chapter == '09' and number >= 185 else chapter, 'page': number, 'path': str(path.relative_to(ROOT)), 'characters': len(body.strip()),
                   'needs_visual_review': len(body.strip()) < 80,
                   'sha256': hashlib.sha256(path.read_bytes()).hexdigest()})
  docs.append({'chapter': chapter, 'title_zh': TOPICS[int(chapter)][0], 'filename': src.name,
               'pdf': str(dest.relative_to(ROOT)), 'sha256': hashlib.sha256(dest.read_bytes()).hexdigest(),
               'bytes': dest.stat().st_size, 'page_count': len(pages), 'pages': records})
 manifest = {'edition': '2025/2026 collection; sales manual 2026', 'import_date': '2026-10-07',
             'source': 'User-uploaded split PDFs', 'extraction': 'pdftotext -layout; no OCR',
             'missing_source_files': sorted(set(f'{i:02}' for i in range(10)) - {d['chapter'] for d in docs}),
             'documents': docs, 'total_pages': sum(d['page_count'] for d in docs)}
 (DATA / 'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
 print(json.dumps({'documents':len(docs), 'pages':manifest['total_pages'],
                   'low_text_pages':sum(p['needs_visual_review'] for d in docs for p in d['pages'])}))

def load():
 return json.loads((DATA / 'manifest.json').read_text(encoding='utf-8'))

def search(query, chapter=None, limit=8):
 q = query.casefold()
 terms = re.findall(r'[a-z0-9]+(?:[-.][a-z0-9]+)*', q)
 for key, values in ALIASES.items():
  if key in q:
   terms.extend(values)
 terms = sorted(set(terms))
 routes = {f'{i:02}' for i, (_, aliases) in enumerate(TOPICS) if any(a in q for a in aliases)}
 results = []
 for doc in load()['documents']:
  for page in doc['pages']:
   if chapter is not None and page['manual_chapter'] != chapter:
    continue
   body = (ROOT / page['path']).read_text(encoding='utf-8')
   folded = body.casefold()
   hits = [t for t in terms if re.search(r'(?<!\w)'+re.escape(t)+r'(?!\w)', folded)]
   exact = bool(q.strip()) and q in folded
   routed = doc['chapter'] in routes or (page['manual_chapter'] == '10' and any(k in q for k in ['规划', '安装', '第10章', '第十章']))
   if not hits and not exact and not routed:
    continue
   score = 100 * exact + 10 * len(hits) + 5 * routed
   lines = body.splitlines()
   relevant = [i for i,line in enumerate(lines) if any(t in line.casefold() for t in hits)]
   start = max(0, relevant[0]-1) if relevant else 0
   results.append({'source_file_id':doc['chapter'], 'chapter':page['manual_chapter'], 'title_zh':doc['title_zh'], 'pdf':doc['pdf'],
                   'pdf_page':page['page'], 'printed_page_candidates':re.findall(r'M\s*\d{1,2}\.\s*\d+',body), 'text':page['path'], 'score':score,
                   'matched_terms':hits, 'excerpt':'\n'.join(lines[start:start+12])})
 return sorted(results,key=lambda r:(-r['score'],r['chapter'],r['pdf_page']))[:limit]

def verify():
 manifest = load()
 assert len(manifest['documents']) + len(manifest['missing_source_files']) == 10
 count = 0
 for doc in manifest['documents']:
  assert hashlib.sha256((ROOT/doc['pdf']).read_bytes()).hexdigest() == doc['sha256'], doc['pdf']
  assert len(doc['pages']) == doc['page_count']
  for p in doc['pages']:
   assert hashlib.sha256((ROOT/p['path']).read_bytes()).hexdigest() == p['sha256'], p['path']
   count += 1
 assert count == manifest['total_pages']
 print(f"Verified {len(manifest['documents'])} PDFs and {count} page texts against SHA-256 manifests. Missing source files: {manifest['missing_source_files']}")

def main():
 parser = argparse.ArgumentParser(description=__doc__)
 commands = parser.add_subparsers(dest='command',required=True)
 b = commands.add_parser('build'); b.add_argument('source'); b.add_argument('--allow-incomplete',action='store_true')
 s = commands.add_parser('search'); s.add_argument('query'); s.add_argument('--chapter', choices=[f'{i:02}' for i in range(11)]); s.add_argument('--limit',type=int,default=8)
 p = commands.add_parser('page'); p.add_argument('chapter',choices=[f'{i:02}' for i in range(10)]); p.add_argument('number',type=int)
 commands.add_parser('verify')
 args = parser.parse_args()
 if args.command == 'build': build(args.source,args.allow_incomplete)
 elif args.command == 'verify': verify()
 elif args.command == 'search':
  if args.limit < 1: parser.error('--limit must be positive')
  print(json.dumps({'missing_source_files':load()['missing_source_files'], 'results':search(args.query,args.chapter,args.limit)},ensure_ascii=False,indent=2))
 else:
  doc = next(d for d in load()['documents'] if d['chapter'] == args.chapter)
  if not 1 <= args.number <= doc['page_count']: parser.error('PDF page out of range')
  print(f"Source: {doc['filename']} | PDF page {args.number} (not printed page number)")
  print((ROOT/doc['pages'][args.number-1]['path']).read_text(encoding='utf-8'))
if __name__ == '__main__': main()
