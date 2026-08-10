# Como o workflow funciona

## Etapa 1 - Perfil

Receber um currículo oficial e preferências declaradas. Estruturar fatos confirmados, campos não informados e políticas de busca sem misturar as fontes.

## Etapa 2 - Vagas

Pesquisar oportunidades e validar cada registro. Vagas antigas, encerradas, duplicadas ou incompatíveis são excluídas ou encaminhadas para revisão.

## Etapa 3 - Match

Comparar apenas fatos comprovados do perfil com requisitos explícitos da vaga. Registrar nota, decomposição, forças, lacunas e obstáculos.

## Etapa 4 - Kit

Gerar ou verificar planilhas, currículos, cartas e relatórios conforme as regras de elegibilidade e os formatos definidos.

## Etapa 5 - Aprovação

Apresentar os resultados para decisão humana. O workflow registra a aprovação, mas não executa uma candidatura automaticamente.

## Validação determinística

Os scripts Python validam:

- estrutura do perfil;
- registros de vagas;
- cálculo de match;
- pacote de materiais;
- estado e transições do workflow.

Essa camada reduz a dependência de respostas livres do modelo e torna erros mais fáceis de detectar.
