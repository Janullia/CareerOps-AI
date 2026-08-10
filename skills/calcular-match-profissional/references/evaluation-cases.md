# Casos de avaliação

1. Aderência completa em todas as categorias deve resultar em 100.
2. Aderência parcial em todas as categorias deve resultar em 50.
3. Item `full` sem evidência da candidata deve falhar e não pontuar.
4. Vaga não confirmada deve falhar e não receber nota válida.
5. Categoria ausente deve falhar.
6. Importância fora de 1–5 deve falhar.
7. Identificador de vaga duplicado deve falhar.
8. Nota 95 deve ser `Excelente`.
9. Nota 85 deve ser `Muito Forte`.
10. Nota 75 deve ser `Forte`, gerar currículo e não gerar carta.
11. Nota 71 deve ser `Possível`.
12. Nota 70 deve ser `Secundária` e não gerar currículo.

## Métricas

- pesos sempre iguais a 35/25/15/15/10;
- zero ponto sem evidência;
- mesma entrada produz a mesma nota;
- faixa, cor e limites de documentos corretos;
- zero vaga não confirmada pontuada.
