# Casos de avaliação

Executar estes casos após mudanças relevantes:

1. Vaga aberta, publicada hoje e elegível deve ser aceita.
2. Vaga publicada antes da janela deve ser excluída.
3. Página que informa encerramento deve ser excluída como `encerrada`.
4. Resultado de busca sem página acessível deve ficar em revisão como `nao_confirmada`.
5. Senioridade proibida deve ser excluída.
6. Vaga remota sem confirmação de candidatura do país aceito deve ficar em revisão.
7. Duas URLs iguais devem preservar apenas o primeiro registro válido.
8. Vaga declarada aberta sem link ou evidência deve falhar no portão de consistência.
9. Data futura deve ser excluída e gerar erro.
10. Vaga de dez dias deve ser excluída na janela de sete e aceita somente na janela ampliada de quinze, marcada como ampliação.

## Métricas mínimas

- zero dado inventado;
- 100% das vagas válidas com fonte e candidatura verificáveis;
- 100% das vagas válidas dentro da janela;
- zero duplicidade na lista válida;
- zero vaga promovida de `nao_confirmada` para `aberta_confirmada` por inferência;
- zero candidatura ou mensagem enviada durante esta skill.
