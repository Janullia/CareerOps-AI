---
name: estruturar-perfil-profissional
description: Converter um currículo oficial e as restrições declaradas pela pessoa em um perfil profissional estruturado, rastreável e reutilizável por agentes de vagas, match e candidatura. Usar ao iniciar uma recolocação, substituir uma versão antiga do currículo, atender uma nova candidata, preparar dados para busca de vagas ou impedir mistura e invenção de experiências, formação, competências, projetos, ferramentas e preferências. Manter fatos profissionais separados das regras de busca e exigir evidência para toda informação confirmada.
---

# Estruturar perfil profissional

## Objetivo

Produzir a única fonte de verdade da candidata para uma execução. Separar fatos profissionais extraídos do currículo oficial das preferências de busca declaradas pela pessoa.

## Entradas

Exigir:

- um currículo identificado como versão oficial;
- nome da candidata;
- data de recebimento ou validação da versão;
- preferências atuais de localização, modalidade, senioridade, jornada e áreas.

Desconsiderar versões anteriores quando a pessoa indicar uma substituição. Não combinar currículos de pessoas diferentes. Pedir confirmação quando o documento ou a identidade forem ambíguos.

## Fluxo

### 1. Registrar a fonte

Criar `candidate_id` estável para a execução. Registrar nome do arquivo, versão, data de recebimento e indicação `is_official: true`.

### 2. Extrair fatos profissionais

Extrair identidade profissional, formação, experiências, competências técnicas e comportamentais, ferramentas, idiomas, projetos e certificações.

Representar cada dado como fato com valor, status, fonte e evidência. Aplicar [references/profile-schema.md](references/profile-schema.md).

Usar somente o currículo oficial para fatos profissionais. Não transformar requisito de vaga, memória de outra conversa, perfil de outra candidata ou conhecimento provável em fato.

### 3. Registrar preferências separadamente

Guardar localidade, modalidade, país elegível para trabalho remoto, dias disponíveis, senioridades e áreas desejadas em `search_policy`.

Usar `source_type: declaracao_usuario` quando a preferência vier diretamente da pessoa. Não apresentar preferência como experiência ou competência.

### 4. Tratar ausência e incerteza

Usar:

- `Não informado` com status `not_informed` quando o currículo não trouxer o dado;
- `Não confirmado` com status `not_confirmed` quando houver referência insuficiente;
- status `confirmed` somente com evidência textual no currículo oficial.

Não inferir conclusão de curso, senioridade, duração, métricas, volume, domínio de ferramenta, nível de idioma ou resultado alcançado.

### 5. Validar

Salvar o perfil em JSON e executar:

```bash
python3 scripts/validate_profile.py perfil.json \
  --output validacao-perfil.json \
  --strict
```

Corrigir todos os erros antes de liberar o perfil. O script verifica fonte oficial, marcadores de incerteza, evidências, identificadores e separação entre fatos e preferências.

### 6. Entregar

Entregar:

- perfil canônico validado;
- versão e fonte oficial utilizadas;
- lista de dados não informados ou não confirmados;
- política de busca atual;
- aviso explícito de que fatos profissionais só podem ser atualizados com nova fonte oficial.

Não pesquisar vagas, calcular match, adaptar currículo ou enviar candidaturas nesta skill.

## Portão de qualidade

Concluir somente quando:

- houver uma única candidata e uma única versão oficial;
- todo fato confirmado possuir evidência;
- fatos profissionais vierem exclusivamente do currículo oficial;
- preferências estiverem separadas em `search_policy`;
- ausências e incertezas estiverem marcadas;
- a validação terminar sem erros.

Usar [references/evaluation-cases.md](references/evaluation-cases.md) ao alterar a skill.
