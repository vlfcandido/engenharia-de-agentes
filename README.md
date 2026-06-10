# 🤖 agentic-base — 3 projetos-base pra estudar Engenharia de Agentes

Bem-vindo! Este repositório tem **três projetos iniciais** com a **mesma
arquitetura** e o **mesmo exemplo**, cada um numa stack diferente. A ideia é você
clonar, rodar com **um comando**, e já ter uma base limpa pra seguir o curso
**[Agentic Engineering Masterclass (INEMA)](https://inematds.github.io/agentic/)**
e começar a codar seus próprios agentes.

> Feito pra rodar no **Windows**, sem dor de cabeça. Tem script de Mac/Linux junto.
> E **roda sem precisar de chave de API** (modo demo) — você vê funcionando de graça.

---

## 📦 Os 3 projetos

Todos resolvem **a mesma tarefa** ("calcule `(12*8)+5` e salve nas anotações"),
usando **as mesmas 2 ferramentas** (calculadora + anotações) e o **mesmo loop**
(pensar → agir → observar). Muda só a *stack*. Assim você compara as abordagens:

| Pasta | Stack | Quando estudar | O que ensina |
|-------|-------|----------------|--------------|
| [`01-pydantic-puro`](01-pydantic-puro/) | **Python puro + Pydantic** (sem framework) | **Comece por aqui** | Como um agente funciona *por baixo dos panos*: o loop, as tools e os hooks escritos à mão |
| [`02-langchain-langgraph`](02-langchain-langgraph/) | **LangChain + LangGraph** | Depois do 01 | O mesmo agente como um **grafo de estados**; o ecossistema mais usado do mercado |
| [`03-google-adk`](03-google-adk/) | **Google ADK** (Agent Development Kit) | Depois do 01 | Framework do Google com **callbacks nativos** (`before_model`, `after_tool`...) e Runner |

Cada pasta tem o **seu próprio README, setup e dependências**. São independentes:
você instala e roda um sem afetar os outros.

---

## 🚀 Começo rápido (Windows)

Pré-requisito: ter o **Git** instalado. O resto (Python) o script instala se faltar.

```powershell
# 1. Baixe o repositório (o link sai quando o Vini te passar o repo)
git clone <URL-DO-REPO> agentic-base
cd agentic-base

# 2. Entre em UM projeto (comece pelo 01)
cd 01-pydantic-puro

# 3. Instale tudo com um comando só
powershell -ExecutionPolicy Bypass -File scripts\setup.ps1

# 4. Rode o exemplo
powershell -ExecutionPolicy Bypass -File scripts\run.ps1
```

Pronto — você vai ver o agente pensando, usando as tools e respondendo. 🎉

> **No Mac/Linux?** Use `bash scripts/setup.sh` e depois `./.venv/bin/python src/main.py`.

> **Por que o `-ExecutionPolicy Bypass`?** Por padrão o Windows bloqueia rodar
> scripts `.ps1`. Esse parâmetro libera só aquela execução, sem mudar nada no PC.

---

## 🔧 A "base do setup" explicada (mesmo automatizada, vale entender)

O `setup.ps1` faz 5 coisas. Entender isso é metade do caminho pra trabalhar com Python:

1. **Confere o Python** (3.10+). Se não tiver, instala via `winget`.
2. **Cria um ambiente virtual** (`.venv`): uma pastinha isolada com as bibliotecas
   *daquele* projeto, pra um projeto não bagunçar o outro.
   - 🟦 *Vindo do C#:* pense no `.venv` como os pacotes que o **NuGet restaura por
     solução** — cada projeto tem os seus, isolados. Ativar o venv ≈ usar aquele
     conjunto de DLLs.
3. **Instala as dependências** do `requirements.txt` dentro do `.venv`
   (`pip install -r requirements.txt`). O `requirements.txt` ≈ o `.csproj` com
   os `<PackageReference>`; o `pip` ≈ o `dotnet restore`.
4. **Cria o `.env`** a partir do `.env.example` — é onde ficam suas chaves de API.
   Sem chave, o projeto roda em **MODO DEMO**.
5. **Roda os testes** (`pytest`) pra provar que está tudo de pé.

Pra rodar de novo depois, é só `scripts\run.ps1` (ele usa o Python do `.venv`).

---

## 🟦 Vindo do C#? Mini-dicionário

Seu background é C# — ótimo, Python tem os mesmos conceitos com outra roupa. O
código está cheio de comentários `# C#: ...` nos pontos importantes. Resumão:

| Python | Equivalente em C# |
|--------|-------------------|
| *type hints* — `def f(x: str) -> int:` | Tipos normais — `int F(string x)` |
| `class Settings(BaseSettings)` (Pydantic) | Classe/`record` de config tipada (`IOptions<T>`) |
| `@dataclass` | `record` (classe só de dados, com construtor/igualdade prontos) |
| `Protocol` | `interface` (com *duck typing*: basta ter os métodos) |
| `Callable[[X], None]` | `delegate` / `Action<X>` |
| `dict[str, Any]` | `Dictionary<string, object>` |
| `list[T]` | `List<T>` |
| `Optional[T]` / `T \| None` | `T?` (nullable) |
| `async def` / `await` | `async Task` / `await` (igualzinho) |
| `.venv` + `pip` + `requirements.txt` | NuGet + `dotnet restore` + `.csproj` |
| `import módulo` | `using Namespace` |
| `raise` / `try/except` | `throw` / `try/catch` |

> 💡 Dica: Python não obriga tipos, mas **este projeto usa type hints em tudo de
> propósito** — fica parecido com C# e o seu editor (VS Code/PyCharm) te dá
> autocomplete e avisa erros, como você está acostumado.

---

## 🔌 Modo DEMO vs. provedor real

Por padrão tudo roda em **MODO DEMO**: um "cérebro" falso, offline, que simula as
decisões do agente. Serve pra você ver a arquitetura rodando **sem gastar 1 centavo**.

Quando quiser usar um LLM de verdade, edite o `.env` do projeto e ponha a chave:

| Projeto | Variável no `.env` | Onde pegar a chave |
|---------|--------------------|--------------------|
| 01 / 02 | `ANTHROPIC_API_KEY` + `LLM_PROVIDER=anthropic` | <https://console.anthropic.com> |
| 03 | `GOOGLE_API_KEY` + `LLM_PROVIDER=gemini` | <https://aistudio.google.com/apikey> (free) |

---

## 🌱 Como crescer (seguindo o curso)

Esta é só a **base**. Conforme você avança nas trilhas do curso, vai plugando coisas
nos **pontos de extensão** que já estão marcados no código:

- **Mais ferramentas (tools/skills)** → Trilha 2.4 — copie um arquivo de tool e registre.
- **Memória / RAG** (FAISS, Chroma) → Trilha 2.3.
- **MCP** (conectar ferramentas externas) → Trilha 2.6 / 3.5.
- **Multi-agente** (CrewAI, AutoGen, A2A) → Trilhas 3 e 4.
- **Observabilidade** (Langfuse, OpenTelemetry → Grafana) → plugue nos **hooks/callbacks**.

O projeto `01` traz um `requirements-extra.txt` com tudo isso já listado (comentado)
pra você descomentar e instalar quando precisar.

---

## 📤 Como levar isso pro SEU repositório

Quando quiser usar uma dessas bases num projeto seu de verdade:

```powershell
# copie a pasta do projeto que você quer (ex.: 01) pra um lugar novo
# apague o histórico do nosso repo e comece o seu:
cd 01-pydantic-puro
rmdir /s /q .git           # (se existir)
git init
git add .
git commit -m "Base do meu agente"
# crie o repo no GitHub e:  git remote add origin <seu-repo> && git push -u origin main
```

> O `.gitignore` já ignora `.venv`, `.env` (suas chaves!) e arquivos temporários —
> então você nunca sobe segredo sem querer.

---

## ⚡ Bônus: usando `uv` no lugar do venv+pip

`uv` é um gerenciador moderno e **muito mais rápido**. Os scripts usam venv+pip
(igual ao curso) pra não confundir, mas se você curtir velocidade:

```powershell
# instala o uv uma vez
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# dentro de um projeto, no lugar do setup:
uv venv
uv pip install -r requirements.txt
uv run python src\main.py     # roda sem nem precisar "ativar" o venv
```

Bons estudos! Qualquer dúvida, o Vini te ajuda. 🚀
