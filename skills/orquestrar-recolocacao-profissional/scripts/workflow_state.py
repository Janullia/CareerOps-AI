#!/usr/bin/env python3
"""Crie, atualize e valide o estado do agente de recolocação."""

from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any


STAGES = ("profile", "jobs", "match", "bundle", "approval")
DEPENDENCIES = {
    "profile": (),
    "jobs": ("profile",),
    "match": ("profile", "jobs"),
    "bundle": ("match",),
    "approval": ("bundle",),
}
ARTIFACT_STAGES = {"profile", "jobs", "match", "bundle"}
STATUSES = {"pending", "in_progress", "blocked", "completed"}
TRANSITIONS = {
    "pending": {"in_progress", "blocked"},
    "in_progress": {"completed", "blocked"},
    "blocked": {"in_progress"},
    "completed": set(),
}
REQUIRED_GUARDRAILS = {
    "single_candidate": True,
    "no_invention": True,
    "application_requires_approval": True,
    "automatic_application": False,
}


def now() -> str:
    return datetime.now().astimezone().isoformat(timespec="seconds")


def initial_state(run_id: str, candidate_id: str) -> dict[str, Any]:
    timestamp = now()
    return {
        "workflow_version": 1,
        "run_id": run_id,
        "candidate_id": candidate_id,
        "created_at": timestamp,
        "updated_at": timestamp,
        "current_stage": "profile",
        "stages": {
            stage: {
                "status": "pending",
                "artifact": None,
                "note": "",
                "updated_at": timestamp,
                "user_approved": False,
            }
            for stage in STAGES
        },
        "guardrails": dict(REQUIRED_GUARDRAILS),
        "events": [
            {
                "at": timestamp,
                "stage": "workflow",
                "from": None,
                "to": "initialized",
                "note": "Execução criada",
            }
        ],
    }


def artifact_candidate_id(path: Path) -> str | None:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    if not isinstance(data, dict):
        return None
    candidate_id = data.get("candidate_id")
    if isinstance(candidate_id, str):
        return candidate_id
    profile = data.get("profile")
    if isinstance(profile, dict) and isinstance(profile.get("candidate_id"), str):
        return profile["candidate_id"]
    manifest = data.get("manifest")
    if isinstance(manifest, dict) and isinstance(manifest.get("candidate_id"), str):
        return manifest["candidate_id"]
    return None


def artifact_validation_errors(path: Path) -> int | None:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None
    if not isinstance(data, dict):
        return None
    summary = data.get("summary")
    if not isinstance(summary, dict):
        return None
    errors = summary.get("errors")
    if isinstance(errors, int) and not isinstance(errors, bool):
        return errors
    return None


def validate_state(state: dict[str, Any]) -> list[dict[str, str]]:
    issues: list[dict[str, str]] = []

    def issue(code, path, message):
        issues.append({"severity": "error", "code": code, "path": path, "message": message})

    if state.get("workflow_version") != 1:
        issue("invalid_version", "workflow_version", "Usar workflow_version igual a 1.")
    for field in ("run_id", "candidate_id"):
        if not isinstance(state.get(field), str) or not state.get(field, "").strip():
            issue(f"missing_{field}", field, f"{field} ausente.")
    stages = state.get("stages")
    if not isinstance(stages, dict):
        issue("missing_stages", "stages", "Mapa de etapas ausente.")
        stages = {}
    for stage in STAGES:
        data = stages.get(stage)
        if not isinstance(data, dict):
            issue("missing_stage", f"stages.{stage}", "Etapa ausente.")
            continue
        if data.get("status") not in STATUSES:
            issue("invalid_stage_status", f"stages.{stage}.status", "Status inválido.")
        if data.get("status") == "completed" and stage in ARTIFACT_STAGES:
            artifact = data.get("artifact")
            if not isinstance(artifact, str) or not Path(artifact).is_file():
                issue("missing_artifact", f"stages.{stage}.artifact", "Etapa concluída sem artefato existente.")
        for dependency in DEPENDENCIES[stage]:
            if data.get("status") in {"in_progress", "completed"}:
                dependency_status = stages.get(dependency, {}).get("status")
                if dependency_status != "completed":
                    issue("dependency_not_completed", f"stages.{stage}", f"Dependência não concluída: {dependency}.")
    guardrails = state.get("guardrails")
    if not isinstance(guardrails, dict):
        issue("missing_guardrails", "guardrails", "Guardrails ausentes.")
    else:
        for key, expected in REQUIRED_GUARDRAILS.items():
            if guardrails.get(key) is not expected:
                issue("invalid_guardrail", f"guardrails.{key}", f"Guardrail deve ser {expected}.")
    if not isinstance(state.get("events"), list):
        issue("invalid_events", "events", "events deve ser uma lista.")
    return issues


def next_stage(state: dict[str, Any]) -> str:
    for stage in STAGES:
        if state["stages"][stage]["status"] != "completed":
            return stage
    return "completed"


def transition(
    state: dict[str, Any],
    stage: str,
    status: str,
    artifact: str | None = None,
    note: str = "",
    user_approved: bool = False,
) -> dict[str, Any]:
    if stage not in STAGES:
        raise ValueError("Etapa inválida.")
    if status not in STATUSES:
        raise ValueError("Status inválido.")
    current = state["stages"][stage]["status"]
    if status not in TRANSITIONS[current]:
        raise ValueError(f"Transição inválida: {current} -> {status}.")
    for dependency in DEPENDENCIES[stage]:
        if state["stages"][dependency]["status"] != "completed":
            raise ValueError(f"Dependência não concluída: {dependency}.")

    if status == "completed" and stage in ARTIFACT_STAGES:
        if not artifact:
            raise ValueError("Etapa técnica concluída exige artefato.")
        artifact_path = Path(artifact).resolve()
        if not artifact_path.is_file():
            raise ValueError("Artefato não encontrado.")
        found_candidate = artifact_candidate_id(artifact_path)
        if found_candidate is None:
            raise ValueError("Artefato sem candidate_id verificável.")
        if found_candidate != state["candidate_id"]:
            raise ValueError("candidate_id do artefato não corresponde à execução.")
        validation_errors = artifact_validation_errors(artifact_path)
        if validation_errors is None:
            raise ValueError("Artefato sem resumo de validação.")
        if validation_errors != 0:
            raise ValueError("Artefato contém erros de validação.")
        artifact = str(artifact_path)

    if stage == "approval" and status == "completed" and not user_approved:
        raise ValueError("Aprovação explícita obrigatória.")

    timestamp = now()
    state["stages"][stage].update(
        {
            "status": status,
            "artifact": artifact if artifact is not None else state["stages"][stage].get("artifact"),
            "note": note,
            "updated_at": timestamp,
            "user_approved": bool(user_approved and stage == "approval"),
        }
    )
    state["events"].append(
        {
            "at": timestamp,
            "stage": stage,
            "from": current,
            "to": status,
            "note": note,
            "user_approved": bool(user_approved and stage == "approval"),
        }
    )
    state["updated_at"] = timestamp
    state["current_stage"] = next_stage(state)
    return state


def save_state(path: Path, state: dict[str, Any]) -> None:
    path = path.resolve()
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(state, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def load_state(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError("Estado deve ser um objeto.")
    return data


def build_parser():
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    init_parser = subparsers.add_parser("init")
    init_parser.add_argument("--run-id", required=True)
    init_parser.add_argument("--candidate-id", required=True)
    init_parser.add_argument("--output", required=True, type=Path)

    transition_parser = subparsers.add_parser("transition")
    transition_parser.add_argument("state", type=Path)
    transition_parser.add_argument("--stage", required=True, choices=STAGES)
    transition_parser.add_argument("--status", required=True, choices=STATUSES)
    transition_parser.add_argument("--artifact")
    transition_parser.add_argument("--note", default="")
    transition_parser.add_argument("--user-approved", action="store_true")

    validate_parser = subparsers.add_parser("validate")
    validate_parser.add_argument("state", type=Path)

    summary_parser = subparsers.add_parser("summary")
    summary_parser.add_argument("state", type=Path)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        if args.command == "init":
            state = initial_state(args.run_id, args.candidate_id)
            save_state(args.output, state)
            print(json.dumps({"created": str(args.output.resolve()), "current_stage": "profile"}, ensure_ascii=False))
            return 0

        state = load_state(args.state)
        if args.command == "transition":
            transition(state, args.stage, args.status, args.artifact, args.note, args.user_approved)
            issues = validate_state(state)
            if issues:
                raise ValueError(issues[0]["message"])
            save_state(args.state, state)
            print(json.dumps({"stage": args.stage, "status": args.status, "current_stage": state["current_stage"]}, ensure_ascii=False))
            return 0
        if args.command == "validate":
            issues = validate_state(state)
            print(json.dumps({"valid": not issues, "issues": issues}, ensure_ascii=False, indent=2))
            return 1 if issues else 0
        if args.command == "summary":
            print(
                json.dumps(
                    {
                        "run_id": state.get("run_id"),
                        "candidate_id": state.get("candidate_id"),
                        "current_stage": state.get("current_stage"),
                        "stages": {key: value.get("status") for key, value in state.get("stages", {}).items()},
                    },
                    ensure_ascii=False,
                    indent=2,
                )
            )
            return 0
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        print(f"Erro: {exc}", file=sys.stderr)
        return 2
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
