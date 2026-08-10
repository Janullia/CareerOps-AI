#!/usr/bin/env python3

import copy
import unittest

from validate_profile import validate_profile


def fact(value, source_type="curriculo_oficial", evidence="Trecho do currículo"):
    return {
        "value": value,
        "status": "confirmed",
        "source_type": source_type,
        "source_name": "curriculo.pdf",
        "evidence": evidence,
    }


def valid_profile():
    return {
        "schema_version": 1,
        "candidate_id": "candidata-exemplo",
        "source_document": {
            "document_name": "curriculo.pdf",
            "version_label": "2026-07-29",
            "received_at": "2026-07-29T12:00:00-03:00",
            "is_official": True,
        },
        "professional_facts": {
            "identity": {"full_name": fact("Candidata Exemplo")},
            "experiences": [
                {
                    "id": "empresa-cargo",
                    "company": fact("Empresa"),
                    "title": fact("Assistente"),
                    "activities": [fact("Atendimento")],
                }
            ],
            "education": [],
            "projects": [],
            "technical_skills": [fact("Excel")],
        },
        "search_policy": {
            "accepted_modalities": fact(
                ["presencial", "remoto"],
                source_type="declaracao_usuario",
                evidence="Preferência declarada pela pessoa",
            )
        },
        "unknown_fields": [],
    }


class ValidateProfileTests(unittest.TestCase):
    def test_accepts_valid_profile(self):
        self.assertEqual(validate_profile(valid_profile())["summary"]["errors"], 0)

    def test_rejects_nonofficial_source(self):
        profile = valid_profile()
        profile["source_document"]["is_official"] = False
        self.assertGreater(validate_profile(profile)["summary"]["errors"], 0)

    def test_rejects_confirmed_fact_without_evidence(self):
        profile = valid_profile()
        profile["professional_facts"]["technical_skills"][0]["evidence"] = ""
        self.assertGreater(validate_profile(profile)["summary"]["errors"], 0)

    def test_rejects_user_statement_as_professional_fact(self):
        profile = valid_profile()
        profile["professional_facts"]["technical_skills"][0]["source_type"] = "declaracao_usuario"
        self.assertGreater(validate_profile(profile)["summary"]["errors"], 0)

    def test_accepts_user_statement_as_search_policy(self):
        self.assertEqual(validate_profile(valid_profile())["summary"]["errors"], 0)

    def test_rejects_wrong_not_informed_marker(self):
        profile = valid_profile()
        profile["professional_facts"]["technical_skills"][0].update(
            {"status": "not_informed", "value": "Ausente"}
        )
        self.assertGreater(validate_profile(profile)["summary"]["errors"], 0)

    def test_rejects_wrong_not_confirmed_marker(self):
        profile = valid_profile()
        profile["professional_facts"]["technical_skills"][0].update(
            {"status": "not_confirmed", "value": "Talvez"}
        )
        self.assertGreater(validate_profile(profile)["summary"]["errors"], 0)

    def test_rejects_duplicate_experience_id(self):
        profile = valid_profile()
        profile["professional_facts"]["experiences"].append(
            copy.deepcopy(profile["professional_facts"]["experiences"][0])
        )
        self.assertGreater(validate_profile(profile)["summary"]["errors"], 0)

    def test_rejects_invalid_received_at(self):
        profile = valid_profile()
        profile["source_document"]["received_at"] = "ontem"
        self.assertGreater(validate_profile(profile)["summary"]["errors"], 0)

    def test_rejects_missing_confirmed_name(self):
        profile = valid_profile()
        profile["professional_facts"]["identity"]["full_name"]["status"] = "not_confirmed"
        profile["professional_facts"]["identity"]["full_name"]["value"] = "Não confirmado"
        self.assertGreater(validate_profile(profile)["summary"]["errors"], 0)


if __name__ == "__main__":
    unittest.main()
