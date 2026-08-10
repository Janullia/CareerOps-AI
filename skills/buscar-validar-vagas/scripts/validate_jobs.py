#!/usr/bin/env python3
"""Valide e classifique registros de vagas sem acessar a rede."""

from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit, urlunsplit


ALLOWED_STATUSES = {
    "aberta_confirmada",
    "nao_confirmada",
    "encerrada",
    "expirada",
    "excluida",
}
CONFIRMED_PUBLICATION_EVIDENCE = {"data_exata", "data_relativa_convertida"}
UNKNOWN_VALUES = {"Não informado", "Não confirmado", ""}
ELIGIBILITY_FIELDS = (
    "location_eligible",
    "remote_country_eligible",
    "seniority_eligible",
    "schedule_eligible",
)


def normalize_text(value: Any) -> str:
    text = unicodedata.normalize("NFKD", str(value or ""))
    text = "".join(char for char in text if not unicodedata.combining(char))
    return re.sub(r"\s+", " ", text).strip().casefold()


def canonical_url(value: Any) -> str | None:
    if not isinstance(value, str) or value in UNKNOWN_VALUES:
        return None
    try:
        parts = urlsplit(value.strip())
    except ValueError:
        return None
    if parts.scheme not in {"http", "https"} or not parts.netloc:
        return None
    clean_path = parts.path.rstrip("/") or "/"
    return urlunsplit((parts.scheme.casefold(), parts.netloc.casefold(), clean_path, parts.query, ""))


def parse_iso_date(value: Any) -> date | None:
    if not isinstance(value, str) or value in UNKNOWN_VALUES:
        return None
    try:
        return date.fromisoformat(value)
    except ValueError:
        return None


def parse_iso_datetime(value: Any) -> datetime | None:
    if not isinstance(value, str) or value in UNKNOWN_VALUES:
        return None
    try:
        return datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        return None


def add_issue(
    issues: list[dict[str, Any]],
    index: int,
    job_id: str,
    severity: str,
    code: str,
    message: str,
) -> None:
    issues.append(
        {
            "index": index,
            "job_id": job_id,
            "severity": severity,
            "code": code,
            "message": message,
        }
    )


def validate_document(
    document: dict[str, Any],
    as_of: date,
    window_days: int,
) -> dict[str, Any]:
    candidate_id = document.get("candidate_id")
    if not isinstance(candidate_id, str) or not candidate_id.strip():
        raise ValueError("O campo 'candidate_id' é obrigatório.")
    jobs = document.get("jobs")
    if not isinstance(jobs, list):
        raise ValueError("O campo 'jobs' deve ser uma lista.")
    if window_days < 1:
        raise ValueError("A janela deve ter pelo menos um dia.")

    cutoff = as_of - timedelta(days=window_days - 1)
    standard_cutoff = as_of - timedelta(days=6)
    issues: list[dict[str, Any]] = []
    output_jobs: list[dict[str, Any]] = []
    seen_urls: dict[str, str] = {}
    seen_fingerprints: dict[tuple[str, str, str, str], str] = {}

    for index, original in enumerate(jobs):
        if not isinstance(original, dict):
            add_issue(issues, index, f"linha-{index + 1}", "error", "invalid_record", "A vaga deve ser um objeto.")
            continue

        job = dict(original)
        job_id = str(job.get("job_id") or f"vaga-{index + 1}")
        job["job_id"] = job_id
        local_issues: list[str] = []
        duplicate_of: str | None = None

        status = job.get("status")
        if status not in ALLOWED_STATUSES:
            add_issue(issues, index, job_id, "error", "invalid_status", "Status ausente ou não permitido.")
            local_issues.append("invalid_status")

        for field in ("title", "company", "source_name"):
            if not isinstance(job.get(field), str) or not job.get(field, "").strip():
                add_issue(issues, index, job_id, "error", f"missing_{field}", f"Campo obrigatório ausente: {field}.")
                local_issues.append(f"missing_{field}")

        source_url = canonical_url(job.get("source_url"))
        application_url = canonical_url(job.get("application_url"))
        if source_url is None:
            add_issue(issues, index, job_id, "error", "invalid_source_url", "A URL da fonte é inválida ou não confirmada.")
            local_issues.append("invalid_source_url")

        published = parse_iso_date(job.get("publication_date"))
        if isinstance(job.get("publication_date"), str) and job.get("publication_date") not in UNKNOWN_VALUES and published is None:
            add_issue(issues, index, job_id, "error", "invalid_publication_date", "A data de publicação não está em formato ISO.")
            local_issues.append("invalid_publication_date")

        if published and published > as_of:
            add_issue(issues, index, job_id, "error", "future_publication_date", "A data de publicação está no futuro.")
            local_issues.append("future_publication_date")

        outside_window = bool(published and published < cutoff)
        if outside_window and status == "aberta_confirmada":
            add_issue(issues, index, job_id, "warning", "outside_window", "A vaga aberta está fora da janela autorizada.")
            local_issues.append("outside_window")
        depends_on_expansion = bool(window_days > 7 and published and published < standard_cutoff)
        if depends_on_expansion and job.get("expanded_window") is not True:
            add_issue(
                issues,
                index,
                job_id,
                "error",
                "missing_expanded_window_marker",
                "A vaga depende da janela ampliada, mas não foi identificada como ampliação.",
            )
            local_issues.append("missing_expanded_window_marker")

        verified_at = parse_iso_datetime(job.get("verified_at"))
        if status == "aberta_confirmada" and verified_at is None:
            add_issue(issues, index, job_id, "error", "missing_verification", "A vaga aberta não possui data/hora válida de verificação.")
            local_issues.append("missing_verification")

        if status == "aberta_confirmada":
            if published is None:
                add_issue(issues, index, job_id, "error", "unconfirmed_publication", "A vaga aberta não possui data confirmada.")
                local_issues.append("unconfirmed_publication")
            if job.get("publication_evidence") not in CONFIRMED_PUBLICATION_EVIDENCE:
                add_issue(issues, index, job_id, "error", "missing_publication_evidence", "A evidência da publicação não foi confirmada.")
                local_issues.append("missing_publication_evidence")
            if application_url is None:
                add_issue(issues, index, job_id, "error", "invalid_application_url", "A vaga aberta não possui link de candidatura válido.")
                local_issues.append("invalid_application_url")
            if job.get("status_evidence") in UNKNOWN_VALUES or not isinstance(job.get("status_evidence"), str):
                add_issue(issues, index, job_id, "error", "missing_status_evidence", "A vaga aberta não possui evidência de status.")
                local_issues.append("missing_status_evidence")
            for field in ELIGIBILITY_FIELDS:
                if job.get(field) is not True:
                    code = f"unconfirmed_{field}"
                    add_issue(issues, index, job_id, "error", code, f"Elegibilidade obrigatória não confirmada: {field}.")
                    local_issues.append(code)
            evidence = job.get("eligibility_evidence")
            if not isinstance(evidence, list) or not evidence:
                add_issue(issues, index, job_id, "error", "missing_eligibility_evidence", "Falta evidência para os filtros de elegibilidade.")
                local_issues.append("missing_eligibility_evidence")
            if job.get("exclusion_reason") not in (None, ""):
                add_issue(issues, index, job_id, "error", "open_with_exclusion", "Vaga aberta não pode possuir motivo de exclusão.")
                local_issues.append("open_with_exclusion")

        fingerprint = (
            normalize_text(job.get("company")),
            normalize_text(job.get("title")),
            normalize_text(job.get("location")),
            normalize_text(job.get("modality")),
        )
        if source_url and source_url in seen_urls:
            duplicate_of = seen_urls[source_url]
        elif all(fingerprint) and fingerprint in seen_fingerprints:
            duplicate_of = seen_fingerprints[fingerprint]

        if duplicate_of:
            add_issue(issues, index, job_id, "warning", "duplicate", f"Duplicata de {duplicate_of}.")
            local_issues.append("duplicate")
        else:
            if source_url:
                seen_urls[source_url] = job_id
            if all(fingerprint):
                seen_fingerprints[fingerprint] = job_id

        if status in {"encerrada", "expirada", "excluida"} or outside_window or duplicate_of:
            classification = "excluded"
        elif status == "nao_confirmada":
            classification = "review"
        elif status == "aberta_confirmada" and not local_issues:
            classification = "accepted"
        else:
            classification = "excluded"

        job["_validation"] = {
            "classification": classification,
            "duplicate_of": duplicate_of,
            "issue_codes": local_issues,
        }
        output_jobs.append(job)

    counts = {
        "total": len(jobs),
        "accepted": sum(job["_validation"]["classification"] == "accepted" for job in output_jobs),
        "review": sum(job["_validation"]["classification"] == "review" for job in output_jobs),
        "excluded": sum(job["_validation"]["classification"] == "excluded" for job in output_jobs),
        "errors": sum(issue["severity"] == "error" for issue in issues),
        "warnings": sum(issue["severity"] == "warning" for issue in issues),
        "duplicates": sum(issue["code"] == "duplicate" for issue in issues),
    }
    return {
        "candidate_id": candidate_id,
        "validation": {
            "as_of": as_of.isoformat(),
            "window_days": window_days,
            "cutoff": cutoff.isoformat(),
            "generated_at": datetime.now().astimezone().isoformat(timespec="seconds"),
        },
        "summary": counts,
        "jobs": output_jobs,
        "issues": issues,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path, help="Arquivo JSON com search e jobs.")
    parser.add_argument("--as-of", required=True, type=date.fromisoformat, help="Data de referência AAAA-MM-DD.")
    parser.add_argument("--window-days", type=int, default=7, help="Número de dias corridos, incluindo a data de referência.")
    parser.add_argument("--output", type=Path, help="Arquivo de saída; omitir para imprimir no terminal.")
    parser.add_argument("--strict", action="store_true", help="Retornar código 1 quando houver erros de consistência.")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        document = json.loads(args.input.read_text(encoding="utf-8"))
        if not isinstance(document, dict):
            raise ValueError("O documento raiz deve ser um objeto.")
        report = validate_document(document, args.as_of, args.window_days)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        print(f"Erro: {exc}", file=sys.stderr)
        return 2

    rendered = json.dumps(report, ensure_ascii=False, indent=2)
    if args.output:
        args.output.write_text(rendered + "\n", encoding="utf-8")
    else:
        print(rendered)
    if args.strict and report["summary"]["errors"]:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
