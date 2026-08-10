# Como publicar no GitHub

## Antes de começar

Confirmar que o projeto contém apenas dados fictícios. Executar:

```bash
python3 scripts/run_all_tests.py
```

## Criar o repositório

No GitHub, criar um repositório chamado `careerops-ai`. Começar como privado para revisar os arquivos antes de torná-lo público.

## Enviar os arquivos

Abrir o terminal dentro da pasta do projeto e executar um comando por vez:

```bash
git init
git add .
git commit -m "feat: publica MVP inicial do CareerOps AI"
git branch -M main
git remote add origin https://github.com/SEU-USUARIO/careerops-ai.git
git push -u origin main
```

Substituir `SEU-USUARIO` pelo nome de usuário correto do GitHub.

## Revisão final

No site do GitHub, verificar:

- se o README aparece corretamente;
- se os testes ficaram verdes;
- se não existem currículos ou dados pessoais;
- se as cinco skills estão presentes;
- se o repositório continua privado durante a primeira revisão.
