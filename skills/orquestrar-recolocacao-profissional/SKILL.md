---
name: orquestrar-recolocacao-profissional
description: Orquestrar o agente de recolocação profissional ponta a ponta, controlando ordem das skills, estado, artefatos, erros, contexto, rastreabilidade e aprovação humana. Usar quando a pessoa pedir o processo completo de pesquisa de vagas, mapa de oportunidades, cálculo de match e materiais personalizados, ou quando for necessário continuar, retomar ou auditar uma execução anterior. Acionar estruturar-perfil-profissional, buscar-validar-vagas, calcular-match-profissional e gerar-kit-candidatura em sequência; nunca avançar com validação falha, misturar candidatas ou realizar candidatura sem aprovação explícita.
---

# Orquestrar recolocação profissional

## Objetivo

Atuar como harness do agente. Coordenar módulos especializados, preservar o estado da execução e impedir que uma etapa contamine ou ignore outra.

## Princípios

- Manter uma candidata por execução.
- Usar o perfil canônico como única fonte de fatos profissionais.
- Executar etapas na ordem definida.
- Bloquear avanço quando a validação produzir erros.
- Registrar artefatos, decisões, falhas e horários.
- Manter ações externas fora do fluxo automático.
- Exigir aprovação explícita antes de qualquer candidatura, mensagem ou envio.

## Inicialização

Confirmar currículo oficial, identidade da candidata, política de busca e entregáveis desejados. Criar o estado:

```bash
python3 scripts/workflow_state.py init \
  --run-id execucao-AAAA-MM-DD \
  --candidate-id candidata \
  --output estado.json
```

Aplicar [references/workflow-contract.md](references/workflow-contract.md).

## Etapas

### 1. Perfil

Acionar `$estruturar-perfil-profissional`. Validar o JSON. Salvar o relatório de validação que contém o perfil canônico como artefato da etapa `profile`.

Não iniciar pesquisa quando identidade ou versão oficial estiverem ambíguas.

### 2. Vagas

Acionar `$buscar-validar-vagas` com o perfil, o mesmo `candidate_id` e a política de busca. Salvar a validação como artefato da etapa `jobs`.

Encaminhar apenas vagas `aberta_confirmada` ao match. Preservar pendentes e excluídas para auditoria.

### 3. Match

Acionar `$calcular-match-profissional`. Salvar o resultado como artefato da etapa `match`.

Rejeitar notas sem evidência, pesos divergentes ou vaga não confirmada.

### 4. Kit

Acionar `$gerar-kit-candidatura`. Criar arquivos, revisar visualmente, validar o manifesto e salvar como artefato da etapa `bundle`.

### 5. Aprovação

Apresentar ranking, arquivos e ressalvas. Manter `approval` pendente até receber uma autorização inequívoca.

Marcar aprovação no estado somente depois da resposta explícita da pessoa. A aprovação registrada não executa candidatura; apenas libera um fluxo externo separado.

## Controle do estado

Antes de iniciar uma etapa:

```bash
python3 scripts/workflow_state.py transition estado.json \
  --stage profile \
  --status in_progress \
  --note "Iniciando perfil oficial"
```

Depois da validação, usar como artefato o relatório JSON com `summary.errors` igual a zero:

```bash
python3 scripts/workflow_state.py transition estado.json \
  --stage profile \
  --status completed \
  --artifact perfil.json \
  --note "Perfil validado sem erros"
```

Usar `blocked` quando faltar informação ou houver erro. Retomar por `in_progress` após corrigir a causa.

Validar o estado:

```bash
python3 scripts/workflow_state.py validate estado.json
```

## Política da janela principal

Aplicar [references/context-policy.md](references/context-policy.md).

Manter na janela principal somente:

- objetivo e política atual;
- candidate_id e versão do currículo;
- resumo das contagens;
- etapa atual, bloqueios e decisões;
- caminhos ou identificadores dos artefatos;
- aprovações.

Manter anúncios completos, resultados intermediários, renderizações e logs extensos nos artefatos. Recarregar apenas o necessário para a etapa atual.

## Tratamento de falhas

Não substituir dado ausente por inferência. Registrar o bloqueio e voltar ao módulo responsável:

- perfil incorreto → etapa `profile`;
- status ou link duvidoso → `jobs`;
- nota inconsistente → `match`;
- arquivo ou layout inválido → `bundle`.

Não apagar evidência anterior. Gerar nova versão do artefato e registrar o evento.

## Conclusão

Concluir a execução quando `profile`, `jobs`, `match` e `bundle` estiverem completos e validados. Entregar os arquivos e manter `approval` pendente se não houver autorização explícita.

Não iniciar candidatura automaticamente. Não interpretar silêncio, elogio, pedido de arquivo ou pedido de revisão como aprovação para envio.

Usar [references/evaluation-cases.md](references/evaluation-cases.md) ao alterar o harness.
