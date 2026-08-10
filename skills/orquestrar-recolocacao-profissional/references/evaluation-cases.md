# Casos de avaliação

1. Nova execução deve iniciar em `profile`.
2. `jobs` não deve iniciar antes de `profile` concluído.
3. `match` não deve iniciar antes de `profile` e `jobs`.
4. `bundle` não deve iniciar antes de `match`.
5. Etapa obrigatória não deve concluir sem artefato existente.
6. Artefato com candidate_id diferente deve falhar.
7. Etapa bloqueada deve poder voltar a `in_progress`.
8. Etapa concluída não deve regredir.
9. Aprovação não deve concluir sem indicador explícito.
10. Aprovação explícita deve ser registrada como evento.
11. Guardrails obrigatórios ausentes devem invalidar o estado.
12. Fluxo completo deve terminar com quatro etapas técnicas concluídas e aprovação pendente ou explícita.
13. Artefato com erro de validação deve impedir conclusão da etapa.

## Métricas

- zero avanço fora de ordem;
- zero mistura de candidate_id;
- zero etapa técnica concluída sem artefato;
- 100% das transições registradas;
- zero aprovação implícita;
- zero candidatura automática.
