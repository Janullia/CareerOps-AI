#!/usr/bin/env python3
"""Valide um perfil profissional canônico sem acessar fontes externas."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Iterable


FACT_STATUSES = {"confirmed", "not_informed", "not_confirmed"}
PROFESSIONAL_SOURCE = "curriculo_oficial"
POLICY_SOURCES = {"curriculo_oficial", "declaracao_usuario"}
UNKNOWN_BY_STATUS = {
    "not_informed": "Não informado",
    "not_confirmed": "Não confirmado",
}


def is_fact(value: Any) -> bool:
    return isinstance(value, dict) and {"value", "status", "source_type", "evidence"} <= set(value)


def walk_facts(value: Any, path: str = "") -> Iterable[tuple[str, dict[str, Any]]]:
    if is_fact(value):
        yield path or "$", value
        return
    if isinstance(value, dict):
        for key, child in value.items():
            child_path = f"{path}.{key}" if path else key
            yield from walk_facts(child, child_path)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from walk_facts(child, f"{path}[{index}]")


def add_issue(issues: list[dict[str, str]], severity: str, code: str, path: str, message: str) -> None:
    issues.append({"severity": severity, "code": code, "path": path, "message": message})


def validate_fact(
    fact: dict[str, Any],
    path: str,
    allowed_sources: set[str],
    issues: list[dict[str, str]],
) -> None:
    status = fact.get("status")
    if status not in FACT_STATUSES:
        add_issue(issues, "error", "invalid_fact_status", path, "Status do fato não permitido.")
        return
    if fact.get("source_type") not in allowed_sources:
        add_issue(issues, "error", "invalid_fact_source", path, "Fonte não permitida para esta seção.")
    if not isinstance(fact.get("source_name"), str) or not fact.get("source_name", "").strip():
        add_issue(issues, "error", "missing_source_name", path, "Nome da fonte ausente.")

    value = fact.get("value")
    evidence = fact.get("evidence")
    if status == "confirmed":
        if value is None or value == "" or value == "Não informado" or value == "Não confirmado":
            add_issue(issues, "error", "empty_confirmed_value", path, "Fato confirmado sem valor específico.")
        if not isinstance(evidence, str) or not evidence.strip():
            add_issue(issues, "error", "missing_evidence", path, "Fato confirmado sem evidência.")
    else:
        expected = UNKNOWN_BY_STATUS[status]
        if value != expected:
            add_issue(issues, "error", "invalid_unknown_marker", path, f"Usar exatamente '{expected}'.")


def collect_ids(section: Any, path: str, issues: list[dict[str, str]]) -> None:
    if not isinstance(section, list):
        return
    seen: set[str] = set()
    for index, item in enumerate(section):
        if not isinstance(item, dict):
            add_issue(issues, "error", "invalid_list_item", f"{path}[{index}]", "Item deve ser um objeto.")
            continue
        item_id = item.get("id")
        if not isinstance(item_id, str) or not item_id.strip():
            add_issue(issues, "error", "missing_item_id", f"{path}[{index}]", "Identificador ausente.")
        elif item_id in seen:
            add_issue(issues, "error", "duplicate_item_id", f"{path}[{index}]", f"Identificador duplicado: {item_id}.")
        else:
            seen.add(item_id)


def validate_profile(profile: dict[str, Any]) -> dict[str, Any]:
    issues: list[dict[str, str]] = []

    if profile.get("schema_version") != 1:
        add_issue(issues, "error", "invalid_schema_version", "schema_version", "Usar schema_version igual a 1.")
    candidate_id = profile.get("candidate_id")
    if not isinstance(candidate_id, str) or not candidate_id.strip():
        add_issue(issues, "error", "missing_candidate_id", "candidate_id", "Identificador da candidata ausente.")

    source = profile.get("source_document")
    if not isinstance(source, dict):
        add_issue(issues, "error", "missing_source_document", "source_document", "Fonte oficial ausente.")
    else:
        if source.get("is_official") is not True:
            add_issue(issues, "error", "source_not_official", "source_document.is_official", "Documento não marcado como oficial.")
        if not isinstance(source.get("document_name"), str) or not source.get("document_name", "").strip():
            add_issue(issues, "error", "missing_document_name", "source_document.document_name", "Nome do documento ausente.")
        try:
            datetime.fromisoformat(str(source.get("received_at", "")).replace("Z", "+00:00"))
        except ValueError:
            add_issue(issues, "error", "invalid_received_at", "source_document.received_at", "Data de recebimento inválida.")

    professional = profile.get("professional_facts")
    policy = profile.get("search_policy")
    if not isinstance(professional, dict):
        add_issue(issues, "error", "missing_professional_facts", "professional_facts", "Fatos profissionais ausentes.")
        professional = {}
    if not isinstance(policy, dict):
        add_issue(issues, "error", "missing_search_policy", "search_policy", "Política de busca ausente.")
        policy = {}

    facts_count = 0
    for path, fact in walk_facts(professional, "professional_facts"):
        facts_count += 1
        validate_fact(fact, path, {PROFESSIONAL_SOURCE}, issues)
    for path, fact in walk_facts(policy, "search_policy"):
        facts_count += 1
        validate_fact(fact, path, POLICY_SOURCES, issues)

    identity = professional.get("identity", {}) if isinstance(professional, dict) else {}
    full_name = identity.get("full_name") if isinstance(identity, dict) else None
    if not is_fact(full_name) or full_name.get("status") != "confirmed":
        add_issue(issues, "error", "missing_confirmed_name", "professional_facts.identity.full_name", "Nome confirmado ausente.")

    for key in ("experiences", "education", "projects"):
        collect_ids(professional.get(key), f"professional_facts.{key}", issues)

    unknown_fields = profile.get("unknown_fields")
    if not isinstance(unknown_fields, list):
        add_issue(issues, "error", "invalid_unknown_fields", "unknown_fields", "unknown_fields deve ser uma lista.")

    counts = {
        "facts": facts_count,
        "errors": sum(issue["severity"] == "error" for issue in issues),
        "warnings": sum(issue["severity"] == "warning" for issue in issues),
    }
    return {"summary": counts, "issues": issues, "profile": profile}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--strict", action="store_true")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        profile = json.loads(args.input.read_text(encoding="utf-8"))
        if not isinstance(profile, dict):
            raise ValueError("O documento raiz deve ser um objeto.")
        report = validate_profile(profile)
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
