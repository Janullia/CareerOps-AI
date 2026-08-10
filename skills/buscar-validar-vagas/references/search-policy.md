# Política de pesquisa e validação

## Hierarquia de evidências

Preferir, nesta ordem:

1. página oficial de carreiras ou sistema de candidatura da empresa;
2. página completa do anúncio em plataforma de vagas;
3. publicação verificável da empresa ou recrutador responsável;
4. agregador ou trecho de buscador, apenas como pista.

Não promover uma pista do nível 4 a `aberta_confirmada` sem abrir uma fonte superior.

## Janela de publicação

Contar dias corridos e incluir a data de referência. Para sete dias, aceitar da data de referência menos seis dias até a própria data. Não converter “há X dias” sem registrar `data_relativa_convertida`.

Quando houver ampliação autorizada para quinze dias:

- preservar a janela principal de sete dias;
- marcar `expanded_window: true` apenas nas vagas que dependem da ampliação;
- não apresentar a ampliação como se fosse a regra principal.

## Status

Usar `aberta_confirmada` quando a página estiver disponível e houver botão, formulário ou instrução atual de candidatura.

Usar `nao_confirmada` quando ocorrer login obrigatório, bloqueio, página incompleta, data incerta, link indireto ou conflito entre fontes.

Usar `encerrada` ou `expirada` quando a própria fonte indicar fechamento. Usar `excluida` para filtros de elegibilidade e duplicidades.

## Elegibilidade

Comparar o anúncio com a política recebida na execução:

- presencial/híbrido: aceitar somente localidades autorizadas;
- remoto: confirmar que o país de residência autorizado é elegível;
- senioridade: rejeitar níveis expressamente excluídos;
- jornada: rejeitar escalas ou dias incompatíveis;
- idioma, autorização de trabalho ou residência: tratar como filtro somente quando obrigatório.

Usar `null` nos campos de elegibilidade quando não houver confirmação e encaminhar a vaga para revisão.

## Duplicidades e republicações

Considerar duplicada quando houver:

- mesma URL canônica; ou
- mesma empresa, cargo, localidade e modalidade, sem diferença material; ou
- republicação do mesmo processo seletivo.

Manter o anúncio mais recente e mais próximo da fonte oficial. Registrar o identificador preservado no motivo de exclusão da duplicata.

## Limite da skill

Não atribuir nota de match, recomendar candidatura ou adaptar documentos. Entregar apenas uma base validada para o próximo módulo.
