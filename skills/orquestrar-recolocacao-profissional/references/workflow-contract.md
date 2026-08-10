# Contrato do workflow

## Ordem

1. `profile` — perfil canônico.
2. `jobs` — vagas validadas.
3. `match` — matches reproduzíveis.
4. `bundle` — kit validado.
5. `approval` — decisão humana, sem execução automática.

Cada etapa pode estar em:

- `pending`;
- `in_progress`;
- `blocked`;
- `completed`.

Uma etapa só inicia quando todas as dependências estiverem `completed`. Uma etapa concluída não regride; correções devem criar nova execução ou nova versão do artefato antes da conclusão.

## Estado mínimo

```json
{
  "workflow_version": 1,
  "run_id": "execucao-2026-07-29",
  "candidate_id": "candidata",
  "current_stage": "profile",
  "stages": {},
  "guardrails": {
    "single_candidate": true,
    "no_invention": true,
    "application_requires_approval": true,
    "automatic_application": false
  },
  "events": []
}
```

## Artefatos primários

- `profile`: relatório de validação contendo o perfil canônico;
- `jobs`: relatório de validação das vagas;
- `match`: resultado validado de match;
- `bundle`: relatório de validação contendo o manifesto;
- `approval`: sem artefato obrigatório; exigir registro de aprovação explícita.

Exigir `candidate_id` correspondente e `summary.errors` igual a zero em todos os quatro artefatos técnicos.
