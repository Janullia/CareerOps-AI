#!/usr/bin/env python3
"""Valide a estrutura de um kit de candidatura."""

from __future__ import annotations

import argparse
import json
import re
import sys
import zipfile
from datetime import datetime
from pathlib import Path
from typing import Any
from xml.etree import ElementTree


REQUIRED_SHEETS = {"Mapa de Oportunidades", "Critérios do Match"}


def add_issue(issues, severity, code, path, message):
    issues.append({"severity": severity, "code": code, "path": path, "message": message})


def safe_path(base_dir: Path, relative: Any) -> Path | None:
    if not isinstance(relative, str) or not relative.strip():
        return None
    base = base_dir.resolve()
    candidate = (base / relative).resolve()
    try:
        candidate.relative_to(base)
    except ValueError:
        return None
    return candidate


def verify_file(base_dir, relative, suffix, issues, path):
    file_path = safe_path(base_dir, relative)
    if file_path is None:
        add_issue(issues, "error", "unsafe_or_missing_path", path, "Caminho ausente ou fora do pacote.")
        return None
    if file_path.suffix.casefold() != suffix:
        add_issue(issues, "error", "invalid_extension", path, f"Extensão esperada: {suffix}.")
    if not file_path.is_file() or file_path.stat().st_size == 0:
        add_issue(issues, "error", "missing_file", path, "Arquivo ausente ou vazio.")
        return None
    return file_path


def inspect_docx(file_path: Path, issues, path):
    try:
        with zipfile.ZipFile(file_path) as archive:
            xml = archive.read("word/document.xml").decode("utf-8", errors="replace")
    except (zipfile.BadZipFile, KeyError, OSError):
        add_issue(issues, "error", "invalid_docx", path, "DOCX inválido.")
        return
    if "<w:tbl" in xml:
        add_issue(issues, "error", "docx_table", path, "DOCX contém tabela.")
    if "<w:drawing" in xml or "<w:pict" in xml:
        add_issue(issues, "error", "docx_drawing", path, "DOCX contém desenho ou imagem.")
    if re.search(r"<w:cols\b[^>]*\bw:num=\"(?:[2-9]|\d{2,})\"", xml):
        add_issue(issues, "error", "docx_multicolumn", path, "DOCX contém múltiplas colunas.")


def inspect_workbook(file_path: Path, issues, path):
    try:
        with zipfile.ZipFile(file_path) as archive:
            workbook_xml = archive.read("xl/workbook.xml")
            sheet_xml = archive.read("xl/worksheets/sheet1.xml").decode("utf-8", errors="replace")
        root = ElementTree.fromstring(workbook_xml)
        names = {
            element.attrib.get("name")
            for element in root.iter()
            if element.tag.endswith("sheet") and element.attrib.get("name")
        }
    except (zipfile.BadZipFile, KeyError, OSError, ElementTree.ParseError):
        add_issue(issues, "error", "invalid_workbook", path, "XLSX inválido.")
        return
    missing = REQUIRED_SHEETS - names
    if missing:
        add_issue(issues, "error", "missing_sheets", path, f"Abas ausentes: {', '.join(sorted(missing))}.")
    if not re.search(r"<pane\b[^>]*\bstate=\"frozen\"", sheet_xml):
        add_issue(issues, "error", "header_not_frozen", path, "Cabeçalho da primeira aba não está congelado.")


def inspect_pdf(file_path: Path, issues, path):
    try:
        header = file_path.read_bytes()[:5]
    except OSError:
        header = b""
    if header != b"%PDF-":
        add_issue(issues, "error", "invalid_pdf", path, "PDF inválido.")


def inspect_archive(file_path: Path, expected_names: set[str], issues, path):
    try:
        with zipfile.ZipFile(file_path) as archive:
            basenames = {Path(name).name for name in archive.namelist() if not name.endswith("/")}
    except (zipfile.BadZipFile, OSError):
        add_issue(issues, "error", "invalid_archive", path, "ZIP inválido.")
        return
    missing = expected_names - basenames
    if missing:
        add_issue(issues, "error", "archive_missing_files", path, f"Arquivos ausentes no ZIP: {', '.join(sorted(missing))}.")


def validate_bundle(manifest: dict[str, Any], base_dir: Path) -> dict[str, Any]:
    issues: list[dict[str, str]] = []
    if manifest.get("bundle_version") != 1:
        add_issue(issues, "error", "invalid_bundle_version", "bundle_version", "Usar bundle_version igual a 1.")
    if not isinstance(manifest.get("candidate_id"), str) or not manifest.get("candidate_id", "").strip():
        add_issue(issues, "error", "missing_candidate_id", "candidate_id", "candidate_id ausente.")
    try:
        datetime.fromisoformat(str(manifest.get("generated_at", "")).replace("Z", "+00:00"))
    except ValueError:
        add_issue(issues, "error", "invalid_generated_at", "generated_at", "Data de geração inválida.")

    global_files = manifest.get("global_files")
    if not isinstance(global_files, dict):
        global_files = {}
        add_issue(issues, "error", "missing_global_files", "global_files", "Arquivos globais ausentes.")

    workbook = verify_file(base_dir, global_files.get("workbook"), ".xlsx", issues, "global_files.workbook")
    report_pdf = verify_file(base_dir, global_files.get("report_pdf"), ".pdf", issues, "global_files.report_pdf")
    archive_zip = verify_file(base_dir, global_files.get("archive_zip"), ".zip", issues, "global_files.archive_zip")
    if workbook:
        inspect_workbook(workbook, issues, "global_files.workbook")
    if report_pdf:
        inspect_pdf(report_pdf, issues, "global_files.report_pdf")

    jobs = manifest.get("jobs")
    if not isinstance(jobs, list):
        jobs = []
        add_issue(issues, "error", "invalid_jobs", "jobs", "jobs deve ser uma lista.")
    seen_jobs: set[str] = set()
    expected_names = {"manifest.json"}
    for key in ("workbook", "report_pdf"):
        if isinstance(global_files.get(key), str):
            expected_names.add(Path(global_files[key]).name)

    for index, job in enumerate(jobs):
        path = f"jobs[{index}]"
        if not isinstance(job, dict):
            add_issue(issues, "error", "invalid_job", path, "Entrada de vaga inválida.")
            continue
        job_id = job.get("job_id")
        if not isinstance(job_id, str) or not job_id.strip():
            add_issue(issues, "error", "missing_job_id", path, "job_id ausente.")
        elif job_id in seen_jobs:
            add_issue(issues, "error", "duplicate_job_id", path, "job_id duplicado.")
        else:
            seen_jobs.add(job_id)
        score = job.get("score")
        if not isinstance(score, int) or isinstance(score, bool) or not 0 <= score <= 100:
            add_issue(issues, "error", "invalid_score", path, "Score deve ser inteiro entre 0 e 100.")
            continue

        for kind, eligible, suffix in (
            ("resume", score > 70, ".docx"),
            ("letter", score > 75, ".docx"),
        ):
            relative = job.get(f"{kind}_file")
            field_path = f"{path}.{kind}_file"
            if eligible and not isinstance(relative, str):
                add_issue(issues, "error", f"missing_{kind}", field_path, f"{kind} obrigatório para esta nota.")
                continue
            if not eligible and relative is not None:
                add_issue(issues, "error", f"unexpected_{kind}", field_path, f"{kind} não permitido para esta nota.")
                continue
            if not eligible:
                continue
            file_path = verify_file(base_dir, relative, suffix, issues, field_path)
            if file_path:
                inspect_docx(file_path, issues, field_path)
                expected_names.add(file_path.name)
            if job.get(f"{kind}_pages") != 1:
                add_issue(issues, "error", f"invalid_{kind}_pages", path, f"{kind} deve ter uma página.")
            if job.get(f"{kind}_visual_reviewed") is not True:
                add_issue(issues, "error", f"{kind}_not_reviewed", path, f"{kind} sem revisão visual.")

    if archive_zip:
        inspect_archive(archive_zip, expected_names, issues, "global_files.archive_zip")
    summary = {
        "jobs": len(jobs),
        "resumes_expected": sum(isinstance(job, dict) and isinstance(job.get("score"), int) and job["score"] > 70 for job in jobs),
        "letters_expected": sum(isinstance(job, dict) and isinstance(job.get("score"), int) and job["score"] > 75 for job in jobs),
        "errors": sum(issue["severity"] == "error" for issue in issues),
        "warnings": sum(issue["severity"] == "warning" for issue in issues),
    }
    return {"summary": summary, "issues": issues, "manifest": manifest}


def build_parser():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--base-dir", required=True, type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--strict", action="store_true")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
        if not isinstance(manifest, dict):
            raise ValueError("O manifesto deve ser um objeto.")
        report = validate_bundle(manifest, args.base_dir)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        print(f"Erro: {exc}", file=sys.stderr)
        return 2
    rendered = json.dumps(report, ensure_ascii=False, indent=2)
    if args.output:
        args.output.write_text(rendered + "\n", encoding="utf-8")
    else:
        print(rendered)
    return 1 if args.strict and report["summary"]["errors"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
