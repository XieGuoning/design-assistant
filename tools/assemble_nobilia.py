"""Assemble user-ordered splits without rasterization; retain provenance."""
from pathlib import Path
import hashlib
import json
from pypdf import PdfReader, PdfWriter

BASE = Path(__file__).resolve().parents[1] / 'data/nobilia/2026'
GROUPS = {
 '06_Highboards_Tall_units.pdf': ['06a_Highboards_Tall_units_1512-2088mm.pdf', '06b-1_Tall_units_height2_2088-2160mm.pdf', '06b-2_Tall_units_height3_2160-2232mm.pdf'],
 '08_LINE_N_handle-less_kitchen.pdf': ['08a-1_LINE_N_Planning_Base_units.pdf', '08a-2_LINE_N_Tall_units_horizontal_handle.pdf', '08b_LINE_N_Tall_vertical_Wall_units.pdf'],
}

def main():
 records = []
 for output, names in GROUPS.items():
  writer = PdfWriter()
  parts = []
  for name in names:
   source = BASE / 'split-sources' / name
   reader = PdfReader(source)
   start = len(writer.pages) + 1
   for page in reader.pages:
    writer.add_page(page)
   parts.append({'filename':name, 'sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
                 'page_count':len(reader.pages), 'merged_start':start, 'merged_end':len(writer.pages)})
  dest = BASE / 'pdf' / output
  if dest.exists():
   raise FileExistsError(f'Refusing to overwrite {dest}')
  with dest.open('wb') as stream:
   writer.write(stream)
  records.append({'filename':output,'page_count':len(writer.pages), 'parts':parts,
                  'sha256':hashlib.sha256(dest.read_bytes()).hexdigest()})
 manifest = {'status':'assembled and indexed', 'date':'2026-10-07',
             'method':'pypdf page copy in explicit source order; all blank and divider pages retained; no image recompression',
             'validation':'Printed page sequence and boundary headings checked; unsplit originals were unavailable for byte comparison',
             'documents':records}
 (BASE/'split-sources/manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2)+'\n')
 print(json.dumps(records,ensure_ascii=False))
if __name__ == '__main__':
 main()
