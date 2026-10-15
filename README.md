# Skill galho 🌳🌿

Skill para o [Claude Code](https://claude.com/claude-code) que transforma uma conversa em **checklist** e deixa você resolver pontos dela em **conversas separadas** (galhos), sem perder o fio da conversa principal (o tronco).

Tudo fica registrado num mapa mental, o `arvore.md`, que você abre com a extensão Markmap no VS Code e clica para pular de uma conversa para outra.

```
🌳 Site novo: página inicial          ← conversa-tronco
├─ [x] Definir paleta de cores
├─ [ ] Tamanho da logo no topo
│   └─ 🌿 Galho 1: proporção no celular   ← conversa à parte, aberta
└─ [ ] Tipografia dos títulos
    └─ ✅ Galho 2: fonte dos títulos      ← já resolvido, com conclusão
```

## Requisitos

- **VS Code** com a extensão do **Claude Code** (os links `vscode://anthropic.claude-code/open` abrem conversas nela).
- Comando `code` no PATH (o instalador do VS Code oferece; no Mac: *Shell Command: Install 'code' command in PATH*).
- **Python 3.8+**.
- Extensão **Markmap** no VS Code, para ver o `arvore.md` como mapa mental (opcional, mas é a graça).

## Instalação

Copie a pasta `galho/` para uma destas:

- `~/.claude/skills/galho/` — vale para todos os seus projetos;
- `<seu projeto>/.claude/skills/galho/` — só para aquele projeto.

```bash
git clone https://github.com/Lamimwork/skill-galho-arvore-checklist.git
cp -r skill-galho-arvore-checklist/galho ~/.claude/skills/
```

## Como usar

| Comando | Onde | O que faz |
| --- | --- | --- |
| `/galho` (ou `/galho <trecho>`) | conversa-tronco | Monta a checklist do tema, mostra para você aprovar, grava o galho no `arvore.md` e abre uma conversa nova já com o contexto preenchido (é só apertar Enter). |
| `/galho continuar` | conversa do galho | Já vem no texto preenchido; liga a conversa nova ao mapa. |
| `/galho fechar` | conversa do galho | Resume a conclusão, marca ✅ no mapa e devolve o resumo para colar no tronco. |
| `/galho abrir N` / `/galho tronco` | qualquer uma | Abre a conversa do galho N ou do tronco. |

Quando uma árvore fica sem nenhum galho aberto, ela sai do `arvore.md` sozinha.

## Observações

- O link clicado **dentro do painel do chat** não abre nada; ele funciona pelo terminal (`code --open-url`) e clicado no Markmap. A skill já usa o terminal.
- O script acha as conversas em `~/.claude/projects/<pasta do projeto>/`. Se não achar, passe `--pasta <caminho>` ou defina `GALHO_PASTA_SESSOES`.
- A skill está em português.
