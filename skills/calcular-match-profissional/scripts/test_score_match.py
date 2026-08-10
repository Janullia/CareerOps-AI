#!/usr/bin/env python3

import copy
import unittest

from score_match import calculate, classify, color


CATEGORIES = ("experience", "technical_skills", "education", "behavioral_skills", "location_modality")


def document(status="full"):
    item = {
        "requirement": "Requisito",
        "importance": 1,
        "status": status,
        "mandatory": True,
        "job_evidence": "Requisito anunciado",
        "candidate_evidence": "Evidência no currículo" if status in {"full", "partial"} else "Não informado",
    }
    return {
        "candidate_id": "candidata",
        "matches": [
            {
                "job_id": "vaga-1",
                "job_status": "aberta_confirmada",
                "categories": {category: {"items": [copy.deepcopy(item)]} for category in CATEGORIES},
                "points_strengths": [],
                "obstacles": [],
                "notes": "",
            }
        ],
    }


class ScoreMatchTests(unittest.TestCase):
    def test_full_match_is_100(self):
        result = calculate(document())["results"][0]
        self.assertEqual(result["score"], 100)
        self.assertEqual(result["classification"], "Excelente")

    def test_partial_match_is_50(self):
        result = calculate(document("partial"))["results"][0]
        self.assertEqual(result["score"], 50)

    def test_missing_evidence_invalidates_score(self):
        data = document()
        data["matches"][0]["categories"]["experience"]["items"][0]["candidate_evidence"] = ""
        result = calculate(data)
        self.assertFalse(result["results"][0]["valid"])

    def test_unconfirmed_job_is_invalid(self):
        data = document()
        data["matches"][0]["job_status"] = "nao_confirmada"
        self.assertFalse(calculate(data)["results"][0]["valid"])

    def test_missing_category_is_invalid(self):
        data = document()
        del data["matches"][0]["categories"]["education"]
        self.assertFalse(calculate(data)["results"][0]["valid"])

    def test_invalid_importance_is_invalid(self):
        data = document()
        data["matches"][0]["categories"]["experience"]["items"][0]["importance"] = 6
        self.assertFalse(calculate(data)["results"][0]["valid"])

    def test_duplicate_job_is_invalid(self):
        data = document()
        data["matches"].append(copy.deepcopy(data["matches"][0]))
        result = calculate(data)
        self.assertEqual(result["summary"]["valid"], 1)
        self.assertEqual(result["summary"]["invalid"], 1)

    def test_classification_boundaries(self):
        self.assertEqual(classify(95), "Excelente")
        self.assertEqual(classify(94), "Muito Forte")
        self.assertEqual(classify(85), "Muito Forte")
        self.assertEqual(classify(75), "Forte")
        self.assertEqual(classify(71), "Possível")
        self.assertEqual(classify(70), "Secundária")
        self.assertEqual(classify(59), "Não priorizar")

    def test_color_boundaries(self):
        self.assertEqual(color(80), "verde")
        self.assertEqual(color(79), "amarelo")
        self.assertEqual(color(71), "amarelo")
        self.assertEqual(color(70), "vermelho")

    def test_document_thresholds(self):
        result = calculate(document())["results"][0]
        self.assertTrue(result["resume_eligible"])
        self.assertTrue(result["letter_eligible"])
        partial = calculate(document("partial"))["results"][0]
        self.assertFalse(partial["resume_eligible"])
        self.assertFalse(partial["letter_eligible"])

    def test_score_75_generates_resume_but_not_letter(self):
        data = document("missing")
        for category in ("experience", "technical_skills", "education"):
            item = data["matches"][0]["categories"][category]["items"][0]
            item["status"] = "full"
            item["candidate_evidence"] = "Evidência no currículo"
        result = calculate(data)["results"][0]
        self.assertEqual(result["score"], 75)
        self.assertTrue(result["resume_eligible"])
        self.assertFalse(result["letter_eligible"])

    def test_weights_total_100(self):
        weights = calculate(document())["summary"]["weights"]
        self.assertEqual(sum(weights.values()), 100)


if __name__ == "__main__":
    unittest.main()
