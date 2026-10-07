import importlib.util
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location('nobilia', Path(__file__).resolve().parents[1] / 'tools/nobilia.py')
n = importlib.util.module_from_spec(spec)
spec.loader.exec_module(n)

class NobiliaRetrievalTests(unittest.TestCase):
 def test_corner_query_uses_chinese_and_points_to_source(self):
  hits = n.search('转角 地柜', '03')
  self.assertTrue(hits)
  self.assertTrue(all(h['chapter'] == '03' for h in hits))
  self.assertIn('corner',hits[0]['matched_terms'])
  self.assertTrue((n.ROOT/hits[0]['pdf']).is_file())

 def test_chapter10_is_in_file09(self):
  hits = n.search('worktop overhangs', '10')
  self.assertTrue(hits)
  self.assertEqual(hits[0]['source_file_id'],'09')
  self.assertIn(hits[0]['pdf_page'],[243,244])
  self.assertIn('M 10.', ' '.join(hits[0]['printed_page_candidates']))

 def test_missing_chapters_are_not_invented(self):
  manifest = n.load()
  for source in manifest['missing_source_files']:
   self.assertEqual(n.search('front',source),[])

 def test_unknown_code_returns_no_hits(self):
  self.assertEqual(n.search('ZZZZNOTAREALMODEL99999'),[])

 def test_original_and_page_integrity(self):
  n.verify()

if __name__ == '__main__': unittest.main()
