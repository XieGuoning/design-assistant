"""Behavioral tests of catalog lookup; run with python -m unittest discover."""

import contextlib
import importlib.util
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


SCRIPT = Path(__file__).resolve().parents[1] / "tools" / "query.py"
spec = importlib.util.spec_from_file_location("design_assistant_query", SCRIPT)
query = importlib.util.module_from_spec(spec)
spec.loader.exec_module(query)


def record(record_id, name, kind="product", **fields):
    data = {
        "id": record_id, "name": name, "kind": kind, "model_number": None,
        "category": "", "source_url": "https://draenert.de/" + record_id,
        "checked_on": "2026-10-05", "source_crawled": "2026-09-29",
        "description": "", "attributes": {}, "color": None,
        "download_options": [], "available_model_formats": [], "slabs": [],
    }
    data.update(fields)
    return data


class CatalogQueryTests(unittest.TestCase):
    def setUp(self):
        self.catalog = {
            "schema_version": 1, "checked_on": "2026-10-05", "summary": {},
            "records": [
                record("adler", "1224 Adler", model_number="1224", category="Esstische", description="Ausziehbarer Tisch aus Naturstein", download_options=[
                    {"label": "DWG", "url": "https://draenert.de/files/adler.dwg", "status": "link_observed", "format": "DWG"},
                    {"label": "3DS", "url": None, "status": "unresolved", "format": "3ds"},
                ], available_model_formats=["dwg", "3ds"]),
                record("magnum", "1224 Adler Magnum", model_number="1224", category="Esstische"),
                record("outdoor", "1224 Adler Outdoor", model_number="1224", category="Outdoor", download_options=[
                    {"label": "3DS", "url": "https://draenert.de/files/adler-outdoor.3ds", "status": "link_observed", "format": "3ds"},
                ]),
                record("number-boundary", "12240 Example", model_number="12240"),
                record("tadao-iii", "Tadao III", model_number="1515 III", description="Also see Tadao V"),
                record("tadao-v", "Tadao V", model_number="1515 V", description="Also see Tadao III"),
                record("false-dwg", "1500 Example", model_number="1500", download_options=[
                    {"label": "DWG", "url": "https://draenert.de/files/no-file", "status": "link_observed", "format": None},
                ], available_model_formats=["dwg"]),
                record("unresolved-url", "1600 Example", model_number="1600", download_options=[
                    {"label": "DWG", "url": "https://draenert.de/files/maybe.dwg", "status": "unresolved", "format": "dwg"},
                ]),
                record("resolved-3ds", "1700 Example", model_number="1700", download_options=[
                    {"label": "3DS model", "url": "https://draenert.de/files/example.3ds", "status": "link_observed", "format": "3ds"},
                ]),
                record("honey-blue", "Honey Blue", "stone", color="blue", description="Quarzit aus Brasilien", attributes={"Synonyme": "Azure Honey; Honey Azul"}),
                record("bahia-blue", "Bahia Blue", "stone", color="blau", description="Sodalith aus Brasilien", attributes={"Synonyme": "Azul Bahia"}),
                record("blue-pearl", "Blue Pearl", "stone", color="black", description="Blue reflections"),
            ],
        }

    def ids(self, *args, **kwargs):
        return [item["id"] for item in query.query_catalog(self.catalog, *args, **kwargs)["results"]]

    def test_explicit_blue_filter_uses_catalog_color_not_name(self):
        for color in ("blue", "blau", "蓝色", "蓝"):
            self.assertEqual(set(self.ids(kind="石材", color=color)), {"honey-blue", "bahia-blue"})

    def test_chinese_color_and_material_prose(self):
        self.assertEqual(self.ids("请帮我找到蓝色的石英岩板子"), ["honey-blue"])

    def test_exact_blue_pearl_name_does_not_impose_blue_color(self):
        self.assertEqual(self.ids("Blue Pearl"), ["blue-pearl"])

    def test_exact_model_number_does_not_return_variants_or_number_prefix(self):
        self.assertEqual(self.ids("1224"), ["adler"])

    def test_model_variant_must_match_explicit_variant(self):
        self.assertEqual(self.ids("1224 magnum"), ["magnum"])
        self.assertEqual(self.ids("1224 户外模型"), ["outdoor"])

    def test_exact_product_name_is_resolved_before_longer_variants(self):
        self.assertEqual(self.ids("Adler"), ["adler"])
        self.assertEqual(self.ids("1224 Adler"), ["adler"])

    def test_roman_variant_cannot_match_a_description_of_another_variant(self):
        self.assertEqual(self.ids("1515 III"), ["tadao-iii"])
        self.assertEqual(self.ids("1515 V"), ["tadao-v"])
        self.assertEqual(set(self.ids("1515")), {"tadao-iii", "tadao-v"})

    def test_format_filter_requires_observed_url_and_exact_format_field(self):
        self.assertEqual(self.ids(file_format="DWG"), ["adler"])
        self.assertEqual(set(self.ids(file_format=".3ds")), {"outdoor", "resolved-3ds"})

    def test_exact_name_is_resolved_before_format_filter(self):
        self.assertEqual(self.ids("Adler", file_format="3ds"), [])
        self.assertEqual(self.ids("Adler 3ds"), [])
        self.assertEqual(self.ids("Adler Outdoor", file_format="3ds"), ["outdoor"])
        self.assertEqual(self.ids("Adler Outdoor 3ds"), ["outdoor"])

    def test_exact_name_and_synonym_are_resolved_before_color_filter(self):
        self.catalog["records"].append(record(
            "blue-pearl-longer", "Blue Pearl Extra", "stone", color="blue",
            attributes={"Synonyme": "Azul Bahia Extra"},
        ))
        self.assertEqual(self.ids("Blue Pearl", color="blue"), [])
        self.assertEqual(self.ids("Azul Bahia", color="black"), [])
        self.assertEqual(self.ids("蓝色的 Blue Pearl"), [])
        self.assertEqual(self.ids("黑色的 Azul Bahia"), [])

    def test_natural_format_query_is_subject_to_same_evidence_rule(self):
        self.assertEqual(self.ids("1224 DWG模型"), ["adler"])
        self.assertEqual(self.ids("1224 3DS模型"), [])

    def test_recorded_synonym_resolves_without_inventing_record(self):
        self.assertEqual(self.ids("Azul Bahia"), ["bahia-blue"])
        self.assertEqual(self.ids("Honey Azul"), ["honey-blue"])

    def test_filters_and_id_are_composed_and_return_original_provenance(self):
        result = query.query_catalog(self.catalog, record_id="honey-blue", kind="stone", color="蓝色")
        self.assertEqual(result["returned_count"], 1)
        self.assertEqual(result["results"][0]["source_url"], "https://draenert.de/honey-blue")
        self.assertEqual(result["catalog_checked_on"], "2026-10-05")
        self.assertIn("不保证当前库存", result["notes"][0])
        self.assertEqual(self.ids(record_id="blue-pearl", color="blue"), [])

    def test_limit_preserves_total_count_and_does_not_mutate_catalog(self):
        before = json.dumps(self.catalog, ensure_ascii=False)
        result = query.query_catalog(self.catalog, kind="stone", limit=1)
        self.assertEqual(result["total_matched"], 3)
        self.assertEqual(result["returned_count"], 1)
        self.assertEqual(json.dumps(self.catalog, ensure_ascii=False), before)

    def test_no_match_returns_empty_results(self):
        self.assertEqual(self.ids("an undocumented product"), [])
        self.assertEqual(self.ids("9999"), [])

    def test_cli_works_outside_project_and_emits_json(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "fixture.json"
            path.write_text(json.dumps(self.catalog), encoding="utf-8")
            process = subprocess.run(
                [sys.executable, str(SCRIPT), "1224", "--catalog", str(path), "--json"],
                cwd=directory, check=True, text=True, capture_output=True,
            )
        result = json.loads(process.stdout)
        self.assertEqual([item["id"] for item in result["results"]], ["adler"])

    def test_text_output_labels_unresolved_downloads_and_stock(self):
        result = query.query_catalog(self.catalog, "1224")
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            query.print_result(result)
        text = output.getvalue()
        self.assertIn("https://draenert.de/files/adler.dwg", text)
        self.assertIn("链接尚未解析", text)
        self.assertIn("不保证当前库存", text)
        self.assertIn("2026-10-05", text)

    def test_brief_preserves_slabs_download_association_and_provenance(self):
        stone = self.catalog["records"][-3]
        stone["slabs"] = [
            {"number": f"test-{index}", "status": "verfügbar", "length_mm": 3000 + index, "width_mm": 1600}
            for index in range(7)
        ]
        before = json.dumps(self.catalog, ensure_ascii=False)
        result = query.query_catalog(self.catalog, record_id=stone["id"], brief=True)
        entry = result["results"][0]
        self.assertNotIn("description", entry)
        self.assertEqual(entry["id"], stone["id"])
        self.assertEqual(entry["slab_count"], 7)
        self.assertEqual(entry["slabs"], stone["slabs"][:5])
        for field in ("source_url", "checked_on", "source_crawled", "attributes", "download_options"):
            self.assertEqual(entry[field], stone[field])
        product = query.query_catalog(self.catalog, "1224", brief=True)["results"][0]
        self.assertEqual(product["download_options"], self.catalog["records"][0]["download_options"])
        self.assertEqual(product["source_url"], self.catalog["records"][0]["source_url"])
        self.assertEqual(json.dumps(self.catalog, ensure_ascii=False), before)
        full = query.query_catalog(self.catalog, record_id=stone["id"])["results"][0]
        self.assertIn("description", full)
        self.assertEqual(len(full["slabs"]), 7)
        self.assertNotIn("slab_count", full)

    def test_brief_text_excludes_description_and_counts_unshown_slabs(self):
        stone = self.catalog["records"][-3]
        stone["description"] = "LONG PAGE TEXT TO OMIT"
        stone["slabs"] = [{"number": str(index)} for index in range(6)]
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            query.print_result(query.query_catalog(self.catalog, record_id=stone["id"], brief=True))
        self.assertNotIn(stone["description"], output.getvalue())
        self.assertIn("另有 1 块", output.getvalue())

    def test_invalid_options_and_bad_schema_fail_clearly(self):
        with self.assertRaises(ValueError):
            query.query_catalog(self.catalog, color="not-a-color")
        with self.assertRaises(ValueError):
            query.query_catalog(self.catalog, limit=0)
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "bad.json"
            path.write_text('{"schema_version": 7, "records": []}', encoding="utf-8")
            with self.assertRaises(ValueError):
                query.load_catalog(path)


if __name__ == "__main__":
    unittest.main()
