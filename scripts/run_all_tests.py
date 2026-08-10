#!/usr/bin/env python3
"""Executa as suítes unitárias de todas as skills do CareerOps AI."""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TEST_FILES = [
    ROOT / "skills" / "estruturar-perfil-profissional" / "scripts" / "test_validate_profile.py",
    ROOT / "skills" / "buscar-validar-vagas" / "scripts" / "test_validate_jobs.py",
    ROOT / "skills" / "calcular-match-profissional" / "scripts" / "test_score_match.py",
    ROOT / "skills" / "gerar-kit-candidatura" / "scripts" / "test_validate_bundle.py",
    ROOT / "skills" / "orquestrar-recolocacao-profissional" / "scripts" / "test_workflow_state.py",
]


def main() -> int:
    total = 0
    failed = []

    for test_file in TEST_FILES:
        if not test_file.is_file():
            print(f"[ERRO] Arquivo ausente: {test_file.relative_to(ROOT)}")
            failed.append(test_file)
            continue

        print(f"\n==> {test_file.relative_to(ROOT)}")
        result = subprocess.run(
            [sys.executable, test_file.name],
            cwd=test_file.parent,
            capture_output=True,
            text=True,
            check=False,
        )
        output = "\n".join(part for part in (result.stdout, result.stderr) if part)
        print(output.rstrip())

        match = re.search(r"Ran (\d+) tests?", output)
        if match:
            total += int(match.group(1))
        if result.returncode != 0:
            failed.append(test_file)

    if failed:
        print(f"\n[FALHA] {len(failed)} suíte(s) apresentaram erro.")
        return 1

    expected = 60
    if total != expected:
        print(f"\n[FALHA] Esperados {expected} testes, mas foram encontrados {total}.")
        return 1

    print(f"\n[OK] {total} testes executados com sucesso em {len(TEST_FILES)} módulos.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
