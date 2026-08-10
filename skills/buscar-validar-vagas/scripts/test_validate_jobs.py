#!/usr/bin/env python3

import unittest
from datetime import date

from validate_jobs import validate_document


def base_job(job_id: str = "v1") -> dict:
    return {
        "job_id": job_id,
        "title": "Assistente Administrativo",
        "company": "Empresa Exemplo",
        "area": "Administrativo",
        "location": "Brasília/DF",
        "modality": "presencial",
        "publication_date": "2026-07-29",
        "publication_evidence": "data_exata",
        "source_name": "Carreiras da empresa",
        "source_url": f"https://example.com/jobs/{job_id}",
        "application_url": f"https://example.com/apply/{job_id}",
        "status": "aberta_confirmada",
        "status_evidence": "Formulário de candidatura ativo",
        "verified_at": "2026-07-29T12:00:00-03:00",
        "seniority": "Assistente",
        "employment_type": "CLT",
        "work_schedule": "Segunda a sexta",
        "salary": "Não informado",
        "benefits": [],
        "description": "Apoio às rotinas administrativas.",
        "required_requirements": ["Organização"],
        "desired_requirements": [],
        "location_eligible": True,
        "remote_country_eligible": True,
        "seniority_eligible": True,
        "schedule_eligible": True,
        "eligibility_evidence": ["Brasília/DF", "Segunda a sexta"],
        "expanded_window": False,
        "exclusion_reason": None,
        "notes": "",
    }


class ValidateJobsTests(unittest.TestCase):
    def run_validation(self, jobs: list[dict], days: int = 7) -> dict:
        return validate_document({"candidate_id": "candidata", "jobs": jobs}, date(2026, 7, 29), days)

    def test_accepts_confirmed_current_job(self) -> None:
        report = self.run_validation([base_job()])
        self.assertEqual(report["summary"]["accepted"], 1)
        self.assertEqual(report["summary"]["errors"], 0)

    def test_excludes_old_job(self) -> None:
        job = base_job()
        job["publication_date"] = "2026-07-20"
        report = self.run_validation([job])
        self.assertEqual(report["summary"]["excluded"], 1)
        self.assertIn("outside_window", report["jobs"][0]["_validation"]["issue_codes"])

    def test_excludes_closed_job_without_treating_as_error(self) -> None:
        job = base_job()
        job["status"] = "encerrada"
        job["exclusion_reason"] = "Inscrições encerradas"
        report = self.run_validation([job])
        self.assertEqual(report["summary"]["excluded"], 1)
        self.assertEqual(report["summary"]["errors"], 0)

    def test_routes_unconfirmed_job_to_review(self) -> None:
        job = base_job()
        job["status"] = "nao_confirmada"
        job["application_url"] = "Não confirmado"
        job["status_evidence"] = "Não confirmado"
        job["location_eligible"] = None
        report = self.run_validation([job])
        self.assertEqual(report["summary"]["review"], 1)

    def test_rejects_claimed_open_job_without_application_link(self) -> None:
        job = base_job()
        job["application_url"] = "Não confirmado"
        report = self.run_validation([job])
        self.assertEqual(report["summary"]["accepted"], 0)
        self.assertGreater(report["summary"]["errors"], 0)

    def test_rejects_ineligible_seniority(self) -> None:
        job = base_job()
        job["seniority"] = "Sênior"
        job["seniority_eligible"] = False
        report = self.run_validation([job])
        self.assertEqual(report["summary"]["accepted"], 0)
        self.assertTrue(any(issue["code"] == "unconfirmed_seniority_eligible" for issue in report["issues"]))

    def test_rejects_remote_job_without_country_confirmation(self) -> None:
        job = base_job()
        job["modality"] = "remoto"
        job["remote_country_eligible"] = None
        report = self.run_validation([job])
        self.assertEqual(report["summary"]["accepted"], 0)
        self.assertTrue(any(issue["code"] == "unconfirmed_remote_country_eligible" for issue in report["issues"]))

    def test_marks_duplicate(self) -> None:
        first = base_job("v1")
        second = base_job("v2")
        second["source_url"] = first["source_url"]
        second["title"] = "Outro título"
        report = self.run_validation([first, second])
        self.assertEqual(report["summary"]["accepted"], 1)
        self.assertEqual(report["summary"]["duplicates"], 1)

    def test_rejects_future_date(self) -> None:
        job = base_job()
        job["publication_date"] = "2026-07-30"
        report = self.run_validation([job])
        self.assertEqual(report["summary"]["accepted"], 0)
        self.assertTrue(any(issue["code"] == "future_publication_date" for issue in report["issues"]))

    def test_accepts_ten_day_old_job_only_in_expanded_window(self) -> None:
        job = base_job()
        job["publication_date"] = "2026-07-20"
        job["expanded_window"] = True
        standard = self.run_validation([job], 7)
        expanded = self.run_validation([job], 15)
        self.assertEqual(standard["summary"]["accepted"], 0)
        self.assertEqual(expanded["summary"]["accepted"], 1)

    def test_requires_expanded_window_marker(self) -> None:
        job = base_job()
        job["publication_date"] = "2026-07-20"
        job["expanded_window"] = False
        report = self.run_validation([job], 15)
        self.assertEqual(report["summary"]["accepted"], 0)
        self.assertTrue(any(issue["code"] == "missing_expanded_window_marker" for issue in report["issues"]))

    def test_requires_candidate_id(self) -> None:
        with self.assertRaises(ValueError):
            validate_document({"jobs": [base_job()]}, date(2026, 7, 29), 7)


if __name__ == "__main__":
    unittest.main()
