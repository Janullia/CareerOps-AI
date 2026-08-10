---
name: calcular-match-profissional
description: Calcular e justificar a aderência entre um perfil profissional validado e vagas abertas confirmadas usando evidências e pesos fixos. Usar para criar nota de match 0–100, decompor experiência, competências técnicas, formação, competências comportamentais e localização/modalidade, registrar pontos fortes, lacunas e obstáculos, classificar oportunidades e definir elegibilidade para currículo ou carta personalizados. Exigir perfil produzido por fonte oficial e vagas previamente validadas; nunca pontuar competências ou experiências não comprovadas.
---

# Calcular match profissional

## Objetivo

Produzir notas reproduzíveis e auditáveis. Medir aderência ao anúncio, não probabilidade de contratação.

## Entradas

Exigir:

- perfil validado por `$estruturar-perfil-profissional`;
- vagas com status `aberta_confirmada` produzidas por `$buscar-validar-vagas`;
- requisitos e responsabilidades extraídos das vagas;
- evidências correspondentes no perfil oficial.

Não calcular match para vagas pendentes, encerradas, expiradas, excluídas ou duplicadas.

## Pesos fixos

Aplicar:

- Experiência: 35 pontos;
- Competências técnicas: 25 pontos;
- Formação: 15 pontos;
- Competências comportamentais: 15 pontos;
- Localização e modalidade: 10 pontos.

Não alterar os pesos entre vagas. Aplicar [references/scoring-rubric.md](references/scoring-rubric.md).

## Fluxo

### 1. Mapear requisitos

Separar cada requisito ou responsabilidade na categoria correta. Registrar se é obrigatório ou desejável e atribuir importância de 1 a 5 conforme a ênfase explícita do anúncio. Usar peso 1 quando não houver ênfase verificável.

### 2. Ligar evidências

Para cada item, registrar:

- evidência da vaga;
- status `full`, `partial`, `missing` ou `unverified`;
- evidência da candidata no perfil oficial;
- indicação de requisito obrigatório.

Usar `full` somente quando o perfil comprovar aderência direta. Usar `partial` para experiência transferível comprovada. Usar `missing` quando o currículo não trouxer o requisito. Usar `unverified` quando a vaga ou o perfil não permitir avaliação.

Não transformar conhecimento semelhante, interesse, curso em andamento ou vontade de aprender em domínio comprovado.

### 3. Calcular

Salvar o mapa em JSON conforme [references/match-schema.md](references/match-schema.md) e executar:

```bash
python3 scripts/score_match.py mapa-match.json \
  --output resultado-match.json \
  --strict
```

O script calcula cobertura ponderada dentro de cada categoria, soma os cinco componentes, aplica a faixa, a cor e os limites de geração de documentos.

### 4. Interpretar

Usar as faixas:

- 95–100: `Excelente`;
- 85–94: `Muito Forte`;
- 75–84: `Forte`;
- 71–74: `Possível`;
- 60–70: `Secundária`;
- abaixo de 60: `Não priorizar`.

Ordenar por maior nota. Informar pontos fortes, obstáculos, lacunas e justificativa sem suavizar requisito obrigatório ausente.

### 5. Entregar

Entregar:

- nota total e cinco componentes;
- faixa e cor;
- evidências utilizadas;
- pontos fortes, lacunas e obstáculos;
- requisitos obrigatórios ausentes;
- indicação de currículo personalizado para nota acima de 70;
- indicação de carta personalizada para nota acima de 75;
- aviso de que o score mede aderência documental.

Não pesquisar novas vagas, criar documentos ou enviar candidatura nesta skill.

## Portão de qualidade

Concluir somente quando:

- todas as vagas pontuadas estiverem abertas e confirmadas;
- os pesos totalizarem 100;
- cada ponto concedido possuir evidência no perfil;
- dados ausentes não receberem pontuação;
- a soma for reproduzível pelo script;
- a validação terminar sem erros.

Usar [references/evaluation-cases.md](references/evaluation-cases.md) ao alterar a skill.
