# Rubrica de pontuação

## Categorias

| Categoria | Máximo | Conteúdo |
|---|---:|---|
| `experience` | 35 | Experiência em funções, atividades, setores e entregas |
| `technical_skills` | 25 | Ferramentas, sistemas, métodos e conhecimentos técnicos |
| `education` | 15 | Curso, área, nível e status acadêmico exigidos |
| `behavioral_skills` | 15 | Competências comportamentais demonstradas no currículo |
| `location_modality` | 10 | Localidade, modalidade, país, jornada e idioma quando obrigatório |

## Fatores de aderência

- `full`: 1,0 — evidência direta.
- `partial`: 0,5 — evidência transferível, mas incompleta.
- `missing`: 0 — requisito ausente no perfil oficial.
- `unverified`: 0 — informação insuficiente para pontuar.

Calcular cada categoria:

`máximo da categoria × soma(importância × fator) ÷ soma(importâncias)`

Arredondar para uma casa decimal. Somar os componentes e arredondar a nota final para o inteiro mais próximo, com metade arredondada para cima.

## Importância

Usar valores de 1 a 5:

- 5: requisito obrigatório destacado ou central para a função;
- 3: requisito obrigatório comum ou responsabilidade recorrente;
- 2: desejável explicitamente valorizado;
- 1: requisito secundário ou sem ênfase.

Não aumentar importância para favorecer ou prejudicar a candidata.

## Requisitos obrigatórios

Registrar requisitos obrigatórios com status `missing` ou `unverified` em `mandatory_gaps`. Não aplicar teto adicional não previsto na fórmula; a ausência já reduz a categoria e deve aparecer como obstáculo explícito.

## Cor operacional

- verde: nota igual ou superior a 80;
- amarelo: 71 a 79;
- vermelho: 70 ou menos.
