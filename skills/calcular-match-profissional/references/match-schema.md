# Contrato do mapa de match

```json
{
  "candidate_id": "candidata-exemplo",
  "matches": [
    {
      "job_id": "vaga-1",
      "job_status": "aberta_confirmada",
      "categories": {
        "experience": {"items": []},
        "technical_skills": {"items": []},
        "education": {"items": []},
        "behavioral_skills": {"items": []},
        "location_modality": {"items": []}
      },
      "points_strengths": [],
      "obstacles": [],
      "notes": ""
    }
  ]
}
```

Cada item deve conter:

```json
{
  "requirement": "Experiência com atendimento B2B",
  "importance": 3,
  "status": "full",
  "mandatory": true,
  "job_evidence": "Atender carteira de clientes empresariais",
  "candidate_evidence": "Atendimento corporativo B2B no currículo oficial"
}
```

Exigir evidência da vaga em todos os itens. Exigir evidência da candidata para `full` e `partial`. Usar `Não informado` no campo de evidência da candidata para `missing` e `unverified`.
