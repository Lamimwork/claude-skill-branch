---
name: galho
description: Abre um "galho": um ponto de uma conversa que vai ser resolvido em outra conversa, com ligação visível nas duas e registro no mapa mental `arvore.md` (Markmap). Use quando o usuário digitar `/galho` (com ou sem um trecho colado), disser "abre um galho", "resolve isso em outra conversa", `/galho fechar` / "fecha o galho" para encerrar um, ou `/galho abrir N` / `/galho tronco` para abrir a conversa de um galho ou do tronco.
---

# Galho

Uma conversa é o **tronco**. Um ponto dela que precisa ser resolvido à parte vira um **galho**, tratado numa conversa nova. As duas pontas ficam marcadas, e o mapa de tudo fica em `arvore.md`, na raiz do projeto, para ser visto com a extensão Markmap.

A conversa nova abre por link da extensão do Claude Code no VS Code (`vscode://anthropic.claude-code/open`), já com o texto de abertura **preenchido, não enviado**: o usuário confere e aperta Enter. O link funciona pelo terminal (`code --open-url`) e clicado no Markmap; **clicado no painel da conversa não faz nada**, então não oferecer link clicável no chat.

## `arvore.md`

Um arquivo só, para todas as árvores. O Markmap desenha títulos e listas como ramos, então a estrutura é fixa:

```markdown
# Árvore

## 🌳 [Site novo: página inicial](vscode://anthropic.claude-code/open?session=<id do tronco>) · 15/10 · `a1b2c3d4`
- [x] Definir paleta de cores
- [ ] Tamanho da logo no topo
  - 🌿 **[Galho 1](vscode://anthropic.claude-code/open?session=<id do galho>)**: proporção da logo no celular
    - Origem: "trecho que gerou o galho…"
- [ ] Tipografia dos títulos
  - ✅ **[Galho 2](vscode://anthropic.claude-code/open?session=<id do galho>)**: fonte dos títulos
    - Conclusão: …
```

- **Árvore** = `##` com 🌳, o tema como link para a sessão-tronco, a data de abertura e os 8 primeiros caracteres do id.
- **Checklist** = os pontos do tema em aberto, `- [ ]` / `- [x]`.
- **Galho** = item aninhado no ponto de onde nasceu: 🌿 aberto, ✅ fechado, numerado na ordem da árvore (1, 2, 3…). Galho de galho: `1.1`, `1.2`, aninhado no galho de origem, que ganha a própria checklist pela mesma regra.
- **Link do galho**: enquanto a conversa do galho não começou, é o link de abertura (`?prompt=`, conversa nova com o texto preenchido); no `/galho continuar`, troca pelo link da sessão do galho (`?session=`).
- Nada de dados pessoais ou sensíveis no arquivo nem no trecho de origem.

**Limpeza:** quando uma árvore fica **sem nenhum galho 🌿 aberto**, ela sai do `arvore.md` inteira. Se o projeto tiver um registro de histórico (um `LOG.md`, por exemplo), antes de apagar anotar nele uma linha com o tema da árvore, os galhos e a conclusão de cada um. Se o arquivo ficar sem árvores, fica só o `# Árvore`.

## Id da sessão e links

Tudo pelo `scripts/galho_link.py` (pasta desta skill):

- `python galho_link.py sessao`: id da conversa atual (o `.jsonl` mais recente da pasta de sessões do projeto, em `~/.claude/projects/`). Se não achar, aceita `--pasta <caminho>` ou a variável `GALHO_PASTA_SESSOES`.
- `python galho_link.py link --session <id>`: link que abre aquela conversa.
- `python galho_link.py link --prompt-file <arquivo>`: link que abre conversa nova com o texto do arquivo preenchido (escrever o texto num arquivo temporário; o script cuida da codificação).
- `--abrir` em qualquer `link`: também abre no VS Code na hora.

## `/galho` — abrir

1. **Ponto de origem.** É o trecho colado junto do comando. Sem trecho, é o ponto mais recente em discussão; confirmar em uma linha qual é.
2. **Árvore desta conversa já existe?** Pegar o id desta sessão (`galho_link.py sessao`) **antes** de abrir a conversa do galho, que passa a ser a sessão mais recente, e procurá-lo no `arvore.md`.
   - **Não:** transformar o tema em aberto da sessão numa checklist curta (só o que ainda está em jogo, uma linha por ponto; `[x]` no que já foi resolvido na conversa) e identificar de qual ponto sai o galho. Criar a árvore com essa checklist.
   - **Sim:** não refazer a checklist. Marcar `[x]` no que foi resolvido desde a última vez, localizar o ponto de origem (ou acrescentá-lo, se for novo) e pendurar nele o galho.
   - **Esta conversa é ela mesma um galho** (abriu com o texto de abertura de um galho): o novo galho se pendura no galho atual da árvore de origem, com número `N.1`, `N.2`…
3. **Confirmar antes de gravar.** Mostrar ao usuário a checklist como vai ficar (nova, ou a existente com o que mudou) e o ponto de onde sai o galho marcado com "← galho". Perguntar se está ok ou se muda algo, e esperar a resposta. Com ajuste, mostrar de novo só se a mudança for grande; senão, gravar já ajustado. Nada vai para o `arvore.md` antes disso.
4. **Gravar** o galho no `arvore.md`: 🌿, número, título curto, linha "Origem" com o trecho (até ~200 caracteres, cortado com "…").
5. **Abrir a conversa do galho**: escrever o texto de abertura (modelo abaixo) num arquivo temporário e rodar `galho_link.py link --prompt-file <arquivo> --abrir`. Gravar esse link no galho do `arvore.md`.
6. **Responder na conversa 1** com a marca:

   > 🌿 **Galho N aberto:** [título] · do ponto "[ponto da checklist]". A conversa do galho abriu com o texto preenchido: é só conferir e apertar Enter.

   Se o `--abrir` falhar, mostrar o texto de abertura num bloco de código para copiar e colar numa conversa nova. Texto de abertura:

   ```
   /galho continuar
   ↳ Galho N da árvore "[tema]" (sessão [id de 8 caracteres])
   Ponto de origem: [ponto da checklist]
   Trecho: "[trecho]"
   Contexto: [2–4 linhas do que já se sabe e do que falta resolver]
   ```

## `/galho continuar` — início da conversa 2

É o texto colado na conversa nova. Abrir a resposta com:

> ↳ **Galho N** da árvore "[tema]" · origem: "[ponto da checklist]"

Pegar o id desta sessão (`galho_link.py sessao`) e trocar, no `arvore.md`, o link de abertura do galho pelo link da sessão (`?session=`). Conferir que o galho está 🌿 e seguir direto no assunto.

## `/galho fechar`

Roda na conversa do galho.

1. Resumir a conclusão em 1–3 linhas e confirmar com o usuário.
2. No `arvore.md`: 🌿 → ✅ e acrescentar a linha "Conclusão". O ponto de origem só vira `[x]` se o usuário confirmar que ele também ficou resolvido.
3. Gerar o texto de retorno num bloco de código, para o usuário colar na conversa 1, e abrir a conversa 1 com `galho_link.py link --session <id do tronco> --abrir`:

   ```
   ✅ Galho N fechado: [título]
   Conclusão: [1–3 linhas]
   ```

4. Se a árvore ficou sem galho aberto, aplicar a **limpeza** acima e avisar em uma linha.

## `/galho abrir N` e `/galho tronco`

Abrem a conversa do galho N (ou do tronco) com `galho_link.py link --session <id> --abrir`, lendo o id no `arvore.md`.

## O que não fazer

- Não usar o `arvore.md` como lista de tarefas do projeto: ele é só o mapa das conversas. Se do galho sair uma pendência ou decisão, ela vai para onde o projeto guarda isso.
- Não apagar árvore que ainda tenha galho 🌿, nem mexer em árvore de outra conversa além de marcar o galho que esta conversa fecha.
