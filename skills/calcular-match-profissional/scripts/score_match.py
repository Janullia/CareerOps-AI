#!/usr/bin/env python3
"""Calcule match profissional a partir de um mapa de evidências."""

from __future__ import annotations

import argparse
import json
import sys
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path
from typing import Any


CATEGORY_WEIGHTS = {
    "experience": Decimal("35"),
    "technical_skills": Decimal("25"),
    "education": Decimal("15"),
    "behavioral_skills": Decimal("15"),
    "location_modality": Decimal("10"),
}
STATUS_FACTORS = {
    "full": Decimal("1"),
    "partial": Decimal("0.5"),
    "missing": Decimal("0"),
    "unverified": Decimal("0"),
}
UNKNOWN_VALUES = {"", "Não informado", "Não confirmado"}


def add_issue(issues, index, job_id, severity, code, message):
    issues.append(
        {
            "index": index,
            "job_id": job_id,
            "severity": severity,
            "code": code,
            "message": message,
        }
    )


def classify(score: int) -> str:
    if score >= 95:
        return "Excelente"
    if score >= 85:
        return "Muito Forte"
    if score >= 75:
        return "Forte"
    if score >= 71:
        return "Possível"
    if score >= 60:
        return "Secundária"
    return "Não priorizar"


def color(score: int) -> str:
    if score >= 80:
        return "verde"
    if score >= 71:
        return "amarelo"
    return "vermelho"


def score_item(item: dict[str, Any], issues, index: int, job_id: str, category: str) -> tuple[Decimal, Decimal]:
    try:
        importance = Decimal(str(item.get("importance")))
    except Exception:
        importance = Decimal("0")
    if importance < 1 or importance > 5:
        add_issue(issues, index, job_id, "error", "invalid_importance", f"Importância inválida em {category}.")
        importance = Decimal("0")

    status = item.get("status")
    factor = STATUS_FACTORS.get(status)
    if factor is None:
        add_issue(issues, index, job_id, "error", "invalid_item_status", f"Status inválido em {category}.")
        factor = Decimal("0")

    job_evidence = item.get("job_evidence")
    if not isinstance(job_evidence, str) or job_evidence in UNKNOWN_VALUES:
        add_issue(issues, index, job_id, "error", "missing_job_evidence", f"Falta evidência da vaga em {category}.")
        factor = Decimal("0")

    candidate_evidence = item.get("candidate_evidence")
    if status in {"full", "partial"} and (
        not isinstance(candidate_evidence, str) or candidate_evidence in UNKNOWN_VALUES
    ):
        add_issue(
            issues,
            index,
            job_id,
            "error",
            "missing_candidate_evidence",
            f"Ponto sem evidência da candidata em {category}.",
        )
        factor = Decimal("0")
    return importance, factor


def calculate(document: dict[str, Any]) -> dict[str, Any]:
    candidate_id = document.get("candidate_id")
    matches = document.get("matches")
    if not isinstance(candidate_id, str) or not candidate_id.strip():
        raise ValueError("candidate_id ausente.")
    if not isinstance(matches, list):
        raise ValueError("matches deve ser uma lista.")

    issues: list[dict[str, Any]] = []
    results: list[dict[str, Any]] = []
    seen_jobs: set[str] = set()

    for index, match in enumerate(matches):
        if not isinstance(match, dict):
            add_issue(issues, index, f"linha-{index + 1}", "error", "invalid_match", "Match deve ser um objeto.")
            continue
        job_id = str(match.get("job_id") or f"vaga-{index + 1}")
        local_error_start = sum(issue["severity"] == "error" for issue in issues)

        if job_id in seen_jobs:
            add_issue(issues, index, job_id, "error", "duplicate_job_id", "Identificador de vaga duplicado.")
        seen_jobs.add(job_id)
        if match.get("job_status") != "aberta_confirmada":
            add_issue(issues, index, job_id, "error", "job_not_confirmed", "Somente vaga aberta confirmada pode ser pontuada.")

        categories = match.get("categories")
        if not isinstance(categories, dict):
            categories = {}
            add_issue(issues, index, job_id, "error", "missing_categories", "Categorias ausentes.")

        component_scores: dict[str, float] = {}
        mandatory_gaps: list[str] = []
        for category, maximum in CATEGORY_WEIGHTS.items():
            category_data = categories.get(category)
            items = category_data.get("items") if isinstance(category_data, dict) else None
            if not isinstance(items, list) or not items:
                add_issue(issues, index, job_id, "error", "empty_category", f"Categoria sem itens: {category}.")
                component_scores[category] = 0.0
                continue

            total_importance = Decimal("0")
            earned = Decimal("0")
            for item in items:
                if not isinstance(item, dict):
                    add_issue(issues, index, job_id, "error", "invalid_item", f"Item inválido em {category}.")
                    continue
                importance, factor = score_item(item, issues, index, job_id, category)
                total_importance += importance
                earned += importance * factor
                if item.get("mandatory") is True and item.get("status") in {"missing", "unverified"}:
                    mandatory_gaps.append(str(item.get("requirement") or "Requisito obrigatório não identificado"))

            if total_importance == 0:
                score = Decimal("0")
            else:
                score = (maximum * earned / total_importance).quantize(Decimal("0.1"), rounding=ROUND_HALF_UP)
            component_scores[category] = float(score)

        raw_total = sum(Decimal(str(value)) for value in component_scores.values())
        total = int(raw_total.quantize(Decimal("1"), rounding=ROUND_HALF_UP))
        local_error_end = sum(issue["severity"] == "error" for issue in issues)
        valid = local_error_end == local_error_start

        results.append(
            {
                "candidate_id": candidate_id,
                "job_id": job_id,
                "valid": valid,
                "score": total if valid else None,
                "components": component_scores,
                "classification": classify(total) if valid else "Inválido",
                "color": color(total) if valid else "vermelho",
                "resume_eligible": bool(valid and total > 70),
                "letter_eligible": bool(valid and total > 75),
                "mandatory_gaps": mandatory_gaps,
                "points_strengths": match.get("points_strengths", []),
                "obstacles": match.get("obstacles", []),
                "notes": match.get("notes", ""),
            }
        )

    results.sort(
        key=lambda item: (
            item["score"] is None,
            0 if item["score"] is None else -item["score"],
            item["job_id"],
        )
    )
    summary = {
        "total": len(matches),
        "valid": sum(result["valid"] for result in results),
        "invalid": sum(not result["valid"] for result in results),
        "errors": sum(issue["severity"] == "error" for issue in issues),
        "weights": {key: int(value) for key, value in CATEGORY_WEIGHTS.items()},
    }
    return {"candidate_id": candidate_id, "summary": summary, "results": results, "issues": issues}


def build_parser():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--strict", action="store_true")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        document = json.loads(args.input.read_text(encoding="utf-8"))
        if not isinstance(document, dict):
            raise ValueError("O documento raiz deve ser um objeto.")
        report = calculate(document)
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
