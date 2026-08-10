---
name: gerar-kit-candidatura
description: Criar, revisar, validar e empacotar materiais personalizados de candidatura a partir de perfil, vagas e matches já validados. Usar para gerar planilha XLSX de oportunidades, currículos ATS DOCX de uma página para matches acima de 70, cartas DOCX de uma página para matches acima de 75, relatório executivo PDF, manifesto e ZIP final. Exigir evidências do perfil oficial, preservar notas e fontes, realizar revisão visual e impedir foto, ícones, gráficos, tabelas, duas colunas, dados inventados ou candidatura automática.
---

# Gerar kit de candidatura

## Objetivo

Transformar resultados validados em arquivos prontos para uso, mantendo rastreabilidade e compatibilidade ATS.

## Entradas

Exigir:

- perfil canônico validado por `$estruturar-perfil-profissional`;
- vagas abertas confirmadas por `$buscar-validar-vagas`;
- matches válidos por `$calcular-match-profissional`;
- nome e formato desejados para o pacote.

Não reconstruir ou corrigir silenciosamente notas, fatos ou status de vaga. Retornar ao módulo responsável quando a entrada estiver inconsistente.

## Regras de geração

Gerar:

- currículo ATS DOCX para cada nota acima de 70;
- carta DOCX para cada nota acima de 75;
- planilha XLSX com todas as vagas válidas e abas `Mapa de Oportunidades` e `Critérios do Match`;
- relatório executivo PDF;
- `manifest.json`;
- arquivo ZIP contendo todo o pacote.

Não gerar currículo para nota 70 ou menor. Não gerar carta para nota 75 ou menor.

## Fluxo

### 1. Preparar conteúdo

Usar somente fatos confirmados do perfil oficial. Personalizar ordem, resumo e palavras-chave com base na vaga, sem criar experiências, métricas, ferramentas, formação concluída ou resultados inexistentes.

Registrar lacunas como lacunas; não escondê-las por meio de linguagem ambígua.

### 2. Criar documentos ATS

Aplicar [references/ats-policy.md](references/ats-policy.md).

Criar currículo e carta em uma página, uma coluna, sem foto, ícones, gráficos, barras, caixas de texto ou tabelas. Usar títulos simples, texto selecionável e hierarquia clara.

Usar a skill de documentos disponível para criar DOCX e renderizar cada arquivo. Revisar a imagem renderizada e corrigir cortes, páginas extras, espaçamento, caracteres quebrados e inconsistências.

### 3. Criar planilha

Usar a skill de planilhas disponível. Aplicar [references/output-spec.md](references/output-spec.md).

Ordenar por maior match. Congelar o cabeçalho. Usar verde para notas iguais ou superiores a 80, amarelo para 71–79 e vermelho para 70 ou menos.

### 4. Criar relatório

Usar a skill de PDF disponível. Resumir quantidade de vagas, prioridades, principais aderências, obstáculos recorrentes, arquivos gerados, critérios e data da validação.

Renderizar e revisar visualmente o PDF.

### 5. Montar manifesto e ZIP

Criar o manifesto conforme [references/bundle-manifest.md](references/bundle-manifest.md). Incluir os arquivos produzidos no ZIP sem incluir versões temporárias.

### 6. Validar

Executar:

```bash
python3 scripts/validate_bundle.py manifest.json \
  --base-dir caminho-do-pacote \
  --output validacao-kit.json \
  --strict
```

O validador confere thresholds, extensões, existência, estrutura ATS dos DOCX, abas e congelamento da planilha, PDF, conteúdo do ZIP, revisão visual declarada e caminhos seguros.

Corrigir todos os erros antes da entrega.

## Entrega

Entregar os arquivos individualmente e o ZIP. Informar quantos currículos e cartas foram produzidos e quais vagas ficaram abaixo dos limites.

Não enviar currículo, carta, e-mail ou candidatura. A criação dos arquivos não representa aprovação para ação externa.

## Portão de qualidade

Concluir somente quando:

- todos os arquivos esperados existirem;
- currículos e cartas tiverem uma página e revisão visual concluída;
- DOCX não contiverem tabelas, desenhos ou múltiplas colunas;
- planilha possuir as duas abas exigidas e cabeçalho congelado;
- o ZIP contiver manifesto, planilha, relatório e documentos elegíveis;
- nenhum arquivo incluir fato não confirmado;
- a validação terminar sem erros.

Usar [references/evaluation-cases.md](references/evaluation-cases.md) ao alterar a skill.
