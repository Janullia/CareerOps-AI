#!/usr/bin/env python3

import json
import tempfile
import unittest
import zipfile
from pathlib import Path

from validate_bundle import validate_bundle


WORKBOOK_XML = """<?xml version="1.0" encoding="UTF-8"?>
<workbook xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">
<sheets><sheet name="Mapa de Oportunidades"/><sheet name="Critérios do Match"/></sheets>
</workbook>"""
SHEET_XML = """<?xml version="1.0" encoding="UTF-8"?>
<worksheet xmlns="http://schemas.openxmlformats.org/spreadsheetml/2006/main">
<sheetViews><sheetView><pane ySplit="1" state="frozen"/></sheetView></sheetViews>
</worksheet>"""
DOC_XML = """<?xml version="1.0" encoding="UTF-8"?>
<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
<w:body><w:p><w:r><w:t>Texto ATS</w:t></w:r></w:p><w:sectPr><w:cols w:num="1"/></w:sectPr></w:body>
</w:document>"""


def write_zip(path: Path, entries: dict[str, str]) -> None:
    with zipfile.ZipFile(path, "w") as archive:
        for name, content in entries.items():
            archive.writestr(name, content)


class BundleFixture:
    def __init__(self, base: Path):
        self.base = base
        write_zip(
            base / "Mapa.xlsx",
            {"xl/workbook.xml": WORKBOOK_XML, "xl/worksheets/sheet1.xml": SHEET_XML},
        )
        write_zip(base / "Curriculo.docx", {"word/document.xml": DOC_XML})
        write_zip(base / "Carta.docx", {"word/document.xml": DOC_XML})
        (base / "Relatorio.pdf").write_bytes(b"%PDF-1.4\n")
        self.manifest = {
            "bundle_version": 1,
            "candidate_id": "candidata",
            "generated_at": "2026-07-29T12:00:00-03:00",
            "global_files": {
                "workbook": "Mapa.xlsx",
                "report_pdf": "Relatorio.pdf",
                "archive_zip": "Kit.zip",
            },
            "jobs": [
                {
                    "job_id": "vaga-1",
                    "score": 85,
                    "resume_file": "Curriculo.docx",
                    "resume_pages": 1,
                    "resume_visual_reviewed": True,
                    "letter_file": "Carta.docx",
                    "letter_pages": 1,
                    "letter_visual_reviewed": True,
                }
            ],
        }
        (base / "manifest.json").write_text(json.dumps(self.manifest), encoding="utf-8")
        write_zip(
            base / "Kit.zip",
            {
                "manifest.json": "{}",
                "Mapa.xlsx": "arquivo",
                "Relatorio.pdf": "arquivo",
                "Curriculo.docx": "arquivo",
                "Carta.docx": "arquivo",
            },
        )


class ValidateBundleTests(unittest.TestCase):
    def run_case(self, mutate=None):
        with tempfile.TemporaryDirectory() as directory:
            fixture = BundleFixture(Path(directory))
            if mutate:
                mutate(fixture)
            return validate_bundle(fixture.manifest, fixture.base)

    def test_accepts_valid_bundle(self):
        self.assertEqual(self.run_case()["summary"]["errors"], 0)

    def test_requires_resume_above_70(self):
        result = self.run_case(lambda f: f.manifest["jobs"][0].update({"score": 71, "resume_file": None}))
        self.assertGreater(result["summary"]["errors"], 0)

    def test_rejects_resume_at_70(self):
        result = self.run_case(lambda f: f.manifest["jobs"][0].update({"score": 70}))
        self.assertGreater(result["summary"]["errors"], 0)

    def test_requires_letter_above_75(self):
        result = self.run_case(lambda f: f.manifest["jobs"][0].update({"score": 76, "letter_file": None}))
        self.assertGreater(result["summary"]["errors"], 0)

    def test_rejects_letter_at_75(self):
        result = self.run_case(lambda f: f.manifest["jobs"][0].update({"score": 75}))
        self.assertGreater(result["summary"]["errors"], 0)

    def test_rejects_table_in_docx(self):
        def mutate(fixture):
            write_zip(fixture.base / "Curriculo.docx", {"word/document.xml": DOC_XML.replace("<w:p>", "<w:tbl/><w:p>")})
        self.assertGreater(self.run_case(mutate)["summary"]["errors"], 0)

    def test_rejects_drawing_in_docx(self):
        def mutate(fixture):
            write_zip(fixture.base / "Curriculo.docx", {"word/document.xml": DOC_XML.replace("<w:p>", "<w:drawing/><w:p>")})
        self.assertGreater(self.run_case(mutate)["summary"]["errors"], 0)

    def test_rejects_multiple_pages_declaration(self):
        result = self.run_case(lambda f: f.manifest["jobs"][0].update({"resume_pages": 2}))
        self.assertGreater(result["summary"]["errors"], 0)

    def test_rejects_missing_sheet(self):
        def mutate(fixture):
            write_zip(
                fixture.base / "Mapa.xlsx",
                {
                    "xl/workbook.xml": WORKBOOK_XML.replace('<sheet name="Critérios do Match"/>', ""),
                    "xl/worksheets/sheet1.xml": SHEET_XML,
                },
            )
        self.assertGreater(self.run_case(mutate)["summary"]["errors"], 0)

    def test_rejects_unfrozen_header(self):
        def mutate(fixture):
            write_zip(
                fixture.base / "Mapa.xlsx",
                {"xl/workbook.xml": WORKBOOK_XML, "xl/worksheets/sheet1.xml": "<worksheet/>"},
            )
        self.assertGreater(self.run_case(mutate)["summary"]["errors"], 0)

    def test_rejects_incomplete_archive(self):
        def mutate(fixture):
            write_zip(fixture.base / "Kit.zip", {"manifest.json": "{}"})
        self.assertGreater(self.run_case(mutate)["summary"]["errors"], 0)

    def test_rejects_path_traversal(self):
        result = self.run_case(lambda f: f.manifest["global_files"].update({"report_pdf": "../Relatorio.pdf"}))
        self.assertGreater(result["summary"]["errors"], 0)


if __name__ == "__main__":
    unittest.main()
