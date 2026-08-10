# Contrato do registro de vaga

Produzir um objeto JSON com `search` e `jobs`.

```json
{
  "candidate_id": "ana-julia-vieira",
  "search": {
    "as_of": "2026-07-29",
    "window_days": 7,
    "expanded_window": false,
    "verified_timezone": "America/Sao_Paulo"
  },
  "jobs": []
}
```

Exigir `candidate_id` idêntico ao perfil canônico utilizado na pesquisa.

## Campos de cada vaga

| Campo | Tipo | Regra |
|---|---|---|
| `job_id` | texto | Identificador estável dentro da execução |
| `title` | texto | Cargo anunciado ou `Não informado` |
| `company` | texto | Empresa anunciada ou `Não informado` |
| `area` | texto | Área da vaga ou `Não informado` |
| `location` | texto | Local informado no anúncio |
| `modality` | texto | `presencial`, `hibrido`, `remoto` ou `Não confirmado` |
| `publication_date` | texto | Data ISO `AAAA-MM-DD`, `Não informado` ou `Não confirmado` |
| `publication_evidence` | texto | `data_exata`, `data_relativa_convertida` ou `nao_confirmada` |
| `source_name` | texto | Nome da fonte |
| `source_url` | texto | URL da página original |
| `application_url` | texto | URL direta de candidatura ou `Não confirmado` |
| `status` | texto | Um dos status permitidos abaixo |
| `status_evidence` | texto | Evidência que sustenta o status |
| `verified_at` | texto | Data/hora ISO da última verificação |
| `seniority` | texto | Senioridade anunciada ou `Não informado` |
| `employment_type` | texto | Regime ou `Não informado` |
| `work_schedule` | texto | Jornada ou `Não informado` |
| `salary` | texto | Valor anunciado ou `Não informado` |
| `benefits` | lista | Itens anunciados; usar lista vazia se ausentes |
| `description` | texto | Resumo fiel do anúncio |
| `required_requirements` | lista | Requisitos obrigatórios explícitos |
| `desired_requirements` | lista | Requisitos desejáveis explícitos |
| `location_eligible` | booleano/nulo | `true`, `false` ou `null` se não confirmado |
| `remote_country_eligible` | booleano/nulo | Usar `true` fora do remoto; no remoto, confirmar o país |
| `seniority_eligible` | booleano/nulo | Compatibilidade com a política informada |
| `schedule_eligible` | booleano/nulo | Compatibilidade com a disponibilidade informada |
| `eligibility_evidence` | lista | Trechos curtos ou fatos que sustentam os quatro campos anteriores |
| `expanded_window` | booleano | Marcar `true` quando a vaga só entra pela janela ampliada |
| `exclusion_reason` | texto/nulo | Motivo objetivo quando excluída |
| `notes` | texto | Observações sem inferências |

## Status permitidos

- `aberta_confirmada`: página ou candidatura ativa verificada.
- `nao_confirmada`: não foi possível confirmar status, link ou elegibilidade essencial.
- `encerrada`: anúncio ou candidatura explicitamente encerrado.
- `expirada`: prazo de candidatura finalizado.
- `excluida`: incompatível com os filtros obrigatórios ou duplicada.

## Consistência

Exigir para `aberta_confirmada`:

- `publication_date` em formato ISO e dentro da janela;
- `publication_evidence` diferente de `nao_confirmada`;
- URLs válidas para fonte e candidatura;
- `status_evidence` diferente de `Não confirmado`;
- `location_eligible`, `remote_country_eligible`, `seniority_eligible` e `schedule_eligible` iguais a `true`;
- pelo menos um item em `eligibility_evidence`;
- `exclusion_reason` vazio.

Manter `Não informado` e `Não confirmado` exatamente com essa grafia para facilitar auditoria.
