"""Behavior checks for preserved webpage and PDF evidence."""
import importlib.util
from pathlib import Path
import unittest

SPEC = importlib.util.spec_from_file_location('build_catalog', Path(__file__).resolve().parents[1] / 'tools' / 'build_catalog.py')
BUILD = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(BUILD)


class SourceEvidenceTests(unittest.TestCase):
    def test_untitled_pdf_preserves_page_range_and_units(self):
        result = {'content': [{'type': 'text', 'text':
            ' (https://draenert.de/_Resources/Adler.pdf)\n'
            '【turnview0】 Crawled: today; Content type: application/pdf; Total lines: 3\n'
            'L0@P0: ADLER\nL1@P0-1: W × L × H (cm)\nL2@P1: 105 × 200 × 73'}]}
        page, = BUILD.parse_result(result)
        self.assertTrue(page['capture_complete'])
        self.assertEqual(page['title'], 'Adler.pdf')
        self.assertIn('L1@P0-1: W × L × H (cm)', page['numbered_text'])
        self.assertIn('105 × 200 × 73', page['text'])

    def test_truncated_read_cannot_claim_complete(self):
        result = {'content': [{'type': 'text', 'text':
            'Stone (https://draenert.de/de/material/stein/example.html)\n'
            '【turnview0】 Total lines: 4\nL0: # Stone\nL1: Farbe | blau'}]}
        page, = BUILD.parse_result(result)
        self.assertFalse(page['capture_complete'])

    def test_name_does_not_supply_color(self):
        page = {'source_url': 'https://draenert.de/de/material/stein/labrador-blue-pearl.html',
                'text': '# Labrador Blue Pearl\nFarbe | schwarz\nVorkommen | Norwegen',
                'title': 'Labrador Blue Pearl', 'source_crawled': 'today', 'capture_complete': True}
        record = BUILD.make_record(page, '2026-10-05', {})
        self.assertEqual(record['color'], 'black')
        self.assertEqual(record['available_model_formats'], [])

    def test_shared_hosts_do_not_duplicate_sources(self):
        self.assertEqual(BUILD.canonical('https://www.draenert.de/_Resources/Atlas%20DWG.zip'),
                         BUILD.canonical('https://draenert.de/_Resources/Atlas DWG.zip'))

    def test_garbled_pdf_is_flagged_even_if_complete(self):
        result = {'content': [{'type': 'text', 'text':
            ' (https://draenert.de/_Resources/Outdoor.pdf)\n'
            '【turnview0】 Total lines: 1\nL0@P0: Ó±¼»´´'}]}
        page, = BUILD.parse_result(result)
        self.assertTrue(page['capture_complete'])
        self.assertEqual(page['text_quality'], 'encoding_artifacts')


if __name__ == '__main__':
    unittest.main()
