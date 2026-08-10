# Contrato do perfil profissional

## Estrutura principal

```json
{
  "schema_version": 1,
  "candidate_id": "ana-julia-vieira",
  "source_document": {
    "document_name": "curriculo.pdf",
    "version_label": "2026-07-29",
    "received_at": "2026-07-29T12:00:00-03:00",
    "is_official": true
  },
  "professional_facts": {},
  "search_policy": {},
  "unknown_fields": []
}
```

## Objeto de fato

Representar cada informação atômica assim:

```json
{
  "value": "Brasília/DF",
  "status": "confirmed",
  "source_type": "curriculo_oficial",
  "source_name": "curriculo.pdf",
  "evidence": "Localização: Brasília/DF"
}
```

Status permitidos:

- `confirmed`: exigir valor específico e evidência.
- `not_informed`: exigir valor `Não informado`.
- `not_confirmed`: exigir valor `Não confirmado`.

Fontes permitidas:

- em `professional_facts`: somente `curriculo_oficial`;
- em `search_policy`: `declaracao_usuario` ou `curriculo_oficial`.

## Conteúdo de `professional_facts`

Usar:

- `identity`: nome, localização e contatos;
- `summary`: objetivo ou resumo existente;
- `education`: lista com identificador e fatos de curso, instituição, status e datas;
- `experiences`: lista com identificador e fatos de empresa, cargo, datas e atividades;
- `technical_skills`: lista de fatos;
- `behavioral_skills`: lista de fatos;
- `tools`: lista de fatos;
- `languages`: lista de idioma e nível, ambos como fatos;
- `projects`: lista com identificador, nome, descrição, tecnologias e link;
- `certifications`: lista de fatos.

Manter atividades, resultados e métricas como fatos separados. Não criar métricas ausentes.

## Conteúdo de `search_policy`

Registrar como fatos:

- `onsite_locations`;
- `accepted_modalities`;
- `remote_countries`;
- `available_weekdays`;
- `allowed_seniorities`;
- `excluded_seniorities`;
- `priority_areas`;
- `secondary_areas`;
- `application_requires_approval`.

## Identificadores

Exigir identificadores únicos em experiências, formações e projetos. Usar nomes estáveis e legíveis, sem dados sensíveis desnecessários.
