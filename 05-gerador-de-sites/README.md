# 05 — Gerador de Sites 🏗️ (agentes não são só chatbot!)

Este projeto pega o **time multi-agente** do [projeto 04](../04-multiagente/) e o
aponta para uma tarefa **concreta e visual**: **gerar um site**. É a prova de que
agente serve pra *construir coisas*, não só conversar.

- **Planejador** decide as seções da página.
- **Executor** escreve os arquivos `index.html` + `style.css` de verdade (no sandbox).
- **Revisor** confere; se faltar seção (ex.: contato), **manda refazer** — e o
  executor corrige no próximo round.

No fim você abre um **site real** no navegador. Tudo **offline** no modo demo.

## ▶️ Rodar

```powershell
powershell -ExecutionPolicy Bypass -File scripts\setup.ps1   # instala + testa
powershell -ExecutionPolicy Bypass -File scripts\run.ps1     # gera o site
```
Mac/Linux: `bash scripts/setup.sh` e `./.venv/bin/python src/main.py`.

Depois **abra `workspace/site/index.html` no navegador**. 🎉

## 🔁 O que acontece quando você roda

```
PLANEJADOR → plano: [hero, sobre, cardapio, contato]
EXECUTOR  (round 1) → gera site só com hero + sobre
REVISOR   (round 1) → REPROVA: "falta cardapio e contato"
EXECUTOR  (round 2) → regenera o site completo
REVISOR   (round 2) → APROVA ✓   → site pronto em workspace/site/
```

Esse vai-e-volta é o coração da coisa: o agente **itera até ficar bom**, sozinho.

## 🗂️ O que mudou em relação ao projeto 04

Quase nada na arquitetura — foi só **trocar os prompts + a tool de saída**:

- [`src/prompts/`](src/prompts/) — prompts reescritos para planejar/gerar/revisar um site.
- [`src/site_templates.py`](src/site_templates.py) — o HTML/CSS que o demo gera
  (em modo real, é o LLM que escreve isso).
- [`src/agents/executor.py`](src/agents/executor.py) — agora escreve **vários
  arquivos** (`site/index.html`, `site/style.css`) em vez de um texto.
- [`src/tools/arquivos.py`](src/tools/arquivos.py) — a mesma tool com **sandbox**
  (só grava dentro de `workspace/`), agora criando subpastas.

> Toda a base de **A2A** e **segurança** (fronteira de confiança anti
> prompt-injection) veio de graça do projeto 04. O exemplo até injeta um ataque
> nos dados do "formulário" — e o site gerado **nunca** contém "INVADIDO".

## 🚀 Faça seu próprio

Quer gerar outro tipo de site (portfólio, restaurante, evento)? Edite o `BRIEFING`
e os `DADOS` no [`src/main.py`](src/main.py) e ajuste os prompts/templates. Com uma
chave da Anthropic no `.env` (`LLM_PROVIDER=anthropic`), o **Claude** escreve o HTML
de verdade a partir do seu briefing — e o revisor continua garantindo a qualidade.
