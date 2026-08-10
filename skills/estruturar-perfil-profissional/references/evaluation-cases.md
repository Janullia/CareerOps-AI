# Casos de avaliação

1. Perfil com currículo oficial e evidências deve ser aceito.
2. Documento não marcado como oficial deve falhar.
3. Fato confirmado sem evidência deve falhar.
4. Fato profissional baseado em declaração da pessoa deve falhar.
5. Preferência de busca baseada em declaração da pessoa deve ser aceita.
6. `not_informed` com valor diferente de `Não informado` deve falhar.
7. `not_confirmed` com valor diferente de `Não confirmado` deve falhar.
8. Duas experiências com o mesmo identificador devem falhar.
9. Data de recebimento inválida deve falhar.
10. Perfil sem nome confirmado deve falhar.
11. Informação de outra candidata inserida como fonte diferente deve falhar.

## Métricas

- zero fato profissional inventado;
- 100% dos fatos confirmados com evidência;
- zero mistura entre candidatas;
- zero preferência apresentada como experiência;
- validação estrutural sem erros.
