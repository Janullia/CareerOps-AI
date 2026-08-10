---
name: buscar-validar-vagas
description: Pesquisar, normalizar e validar vagas de emprego antes do cálculo de match ou da criação de materiais de candidatura. Usar quando a pessoa pedir busca de vagas recentes, mapa de oportunidades, verificação de links e inscrições, eliminação de vagas antigas, encerradas, duplicadas, republicadas, incompatíveis por localidade, modalidade, senioridade ou jornada, ou preparação de uma base confiável de vagas para outro agente. Exigir perfil ou currículo oficial e regras de elegibilidade; nunca completar informações por inferência.
---

# Buscar e validar vagas

## Objetivo

Produzir uma base auditável de vagas confirmadas, separando oportunidades válidas, pendentes de confirmação e excluídas. Encerrar esta skill antes de calcular match, adaptar currículo, gerar cartas ou realizar candidaturas.

## Entradas obrigatórias

Obter antes da pesquisa:

- currículo ou perfil oficial da pessoa;
- `candidate_id` do perfil canônico;
- localidades aceitas para vagas presenciais e híbridas;
- países aceitos para vagas remotas;
- senioridades e jornadas permitidas;
- áreas e cargos prioritários;
- data de referência e janela de publicação.

Usar sete dias corridos, contando a data de referência, quando a pessoa não definir outra janela. Ampliar para quinze dias somente quando solicitado ou quando o fluxo principal autorizar expressamente; identificar todas as vagas da janela ampliada.

Não misturar dados de candidatas diferentes. Interromper e pedir o perfil oficial quando não houver uma fonte inequívoca.

## Fluxo obrigatório

### 1. Pesquisar

Pesquisar em fontes públicas e páginas oficiais disponíveis. Registrar a página original do anúncio e o link direto de candidatura quando forem diferentes.

Não tratar trecho de buscador, agregador ou data relativa isolada como confirmação suficiente. Abrir a página da vaga sempre que a ferramenta disponível permitir.

### 2. Extrair sem inferir

Preencher os campos definidos em [references/job-record-schema.md](references/job-record-schema.md).

Usar `Não informado` quando o anúncio não trouxer um dado. Usar `Não confirmado` quando o dado existir em fonte secundária, trecho de busca, publicação relativa ou página inacessível, mas não puder ser validado.

Não inventar ou completar empresa, cargo, salário, benefícios, requisitos, datas, modalidade, regime ou quantidade de candidatos.

### 3. Confirmar a oportunidade

Aplicar [references/search-policy.md](references/search-policy.md).

Classificar como `aberta_confirmada` somente quando houver evidência atual de candidatura ativa e todos os filtros obrigatórios forem atendidos. Classificar como `nao_confirmada` quando a página não permitir confirmar um requisito essencial.

Excluir:

- anúncio encerrado, expirado ou indisponível;
- publicação fora da janela autorizada;
- duplicidade ou republicação equivalente;
- senioridade, localidade, modalidade ou jornada incompatível;
- vaga remota que não confirme elegibilidade no país aceito;
- oportunidade que exija uma condição obrigatória incompatível com o perfil.

Não excluir uma vaga apenas porque falta uma competência: registrar isso posteriormente como possível lacuna de match. Excluir apenas incompatibilidades de elegibilidade ou filtros obrigatórios desta etapa.

### 4. Normalizar e validar

Salvar os registros em JSON conforme o esquema. Executar:

```bash
python3 scripts/validate_jobs.py vagas.json \
  --as-of AAAA-MM-DD \
  --window-days 7 \
  --output validacao.json \
  --strict
```

Usar `--window-days 15` apenas para uma ampliação autorizada. O script verifica estrutura, datas, evidências, elegibilidade declarada, links, duplicidades e consistência do status; ele não substitui a abertura da página nem realiza uma candidatura.

Corrigir inconsistências e executar novamente até o relatório não conter erros. Manter vagas legitimamente encerradas ou incompatíveis como excluídas, com motivo, sem convertê-las em abertas.

Preservar o mesmo `candidate_id` no documento de entrada e no relatório validado.

### 5. Entregar ao próximo módulo

Entregar:

- vagas válidas, ordenadas pela data mais recente;
- vagas pendentes de confirmação;
- vagas excluídas com motivo;
- fontes e data/hora de verificação;
- contagem de anúncios encontrados, válidos, pendentes e excluídos;
- aviso de que o status pode mudar após a verificação.

Não calcular match nesta skill. Não gerar currículo, carta, planilha final ou relatório executivo. Não enviar candidatura, mensagem ou e-mail.

## Portão de qualidade

Considerar a execução concluída somente quando:

- cada vaga válida possuir fonte e link verificáveis;
- cada vaga válida estiver dentro da janela;
- cada status `aberta_confirmada` possuir evidência;
- duplicidades estiverem removidas da lista válida;
- filtros de localidade, modalidade, senioridade e jornada estiverem registrados;
- todo dado ausente ou incerto estiver sinalizado;
- nenhuma ação externa de candidatura tiver sido realizada.

Usar [references/evaluation-cases.md](references/evaluation-cases.md) para testar alterações futuras na skill.
