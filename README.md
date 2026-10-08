<picture>
  <source media="(prefers-color-scheme: dark)" srcset="docs/marca/cabecalho-escuro.svg">
  <img alt="engenharia-de-agentes" src="docs/marca/cabecalho-claro.svg" width="100%">
</picture>

# engenharia-de-agentes

O mesmo agente de IA escrito em três stacks (Python puro com Pydantic, LangChain/LangGraph e Google ADK), mais uma versão multiagente nas três e uma aplicação que usa um time de agentes para gerar um site. Todos rodam offline, sem chave de API, num modo de demonstração.

![Terminal rodando o time multiagente em LangGraph, com o grafo planejador, executor e revisor](docs/prints/engenharia-de-agentes.png)

## Por que existe

Material de estudo de engenharia de agentes. Comparar frameworks lendo documentação não mostra a diferença real; implementar a mesma tarefa, com as mesmas ferramentas e o mesmo laço (pensar, agir, observar), em cada um deles mostra. A tarefa é sempre a mesma: calcular `(12*8)+5` e salvar o resultado nas anotações, usando duas tools (calculadora e anotações).

## Projetos

| pasta | stack | o que mostra |
|---|---|---|
| [`01-pydantic-puro`](01-pydantic-puro/) | Python + Pydantic, sem framework | o laço do agente, o registro de tools e os hooks escritos à mão |
| [`02-langchain-langgraph`](02-langchain-langgraph/) | LangChain + LangGraph | o mesmo agente como grafo de estados |
| [`03-google-adk`](03-google-adk/) | Google ADK | Runner e callbacks nativos (`before_model`, `after_tool`) |
| [`04-multiagente`](04-multiagente/) | as três stacks | planejador, executor e revisor; prompts por agente, comunicação A2A e defesa contra prompt injection ([SEGURANCA.md](04-multiagente/SEGURANCA.md)) |
| [`05-gerador-de-sites`](05-gerador-de-sites/) | Python + Pydantic, multiagente | um time que gera uma página HTML/CSS e itera sobre ela até o revisor aprovar |

Cada pasta é independente: tem o próprio README, dependências, scripts de setup e testes.

Página gerada pelo projeto 05, em modo offline:

![Site gerado pelos agentes](05-gerador-de-sites/preview.png)

## O padrão que se repete nos projetos

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="docs/marca/diagrama-escuro.svg">
  <img alt="Diagrama: o pedido passa por uma barreira contra prompt injection, o agente pensa, usa só ferramentas liberadas num laço com limite de voltas e a saída é validada em Pydantic" src="docs/marca/diagrama-claro.svg" width="100%">
</picture>

## Stack

Python 3.10+, Pydantic v2, pydantic-settings, LangGraph 1.x, Google ADK 2.x, pytest. Provedores reais opcionais: Anthropic (projetos 01, 02, 04 e 05) e Gemini (03).

## Como rodar

Mac/Linux:

```bash
cd 01-pydantic-puro
bash scripts/setup.sh            # cria .venv, instala dependências, cria .env e roda os testes
./.venv/bin/python src/main.py
```

Windows (PowerShell):

```powershell
cd 01-pydantic-puro
powershell -ExecutionPolicy Bypass -File scripts\setup.ps1
powershell -ExecutionPolicy Bypass -File scripts\run.ps1
```

Sem chave no `.env`, tudo roda em modo demonstração: um modelo falso e determinístico simula as decisões do agente, então a arquitetura pode ser exercitada sem custo. Para usar um LLM de verdade:

| projeto | variáveis no `.env` |
|---|---|
| 01, 02, 04, 05 | `LLM_PROVIDER=anthropic` e `ANTHROPIC_API_KEY` |
| 03 | `LLM_PROVIDER=gemini` e `GOOGLE_API_KEY` |

## Testes

Cada projeto tem testes de fumaça que rodam no modo demonstração (`pytest` dentro da pasta). Última execução, Python 3.12:

| projeto | testes |
|---|---|
| 01-pydantic-puro | 4 passando |
| 02-langchain-langgraph | 2 passando |
| 03-google-adk | 3 passando |
| 04-multiagente/pydantic-puro | 5 passando |
| 04-multiagente/langchain-langgraph | 3 passando |
| 04-multiagente/google-adk | 3 passando |
| 05-gerador-de-sites | 4 passando |

Total: 24 testes.

## Pontos de extensão

O código marca onde entram memória/RAG, novas tools, MCP e observabilidade (os hooks e callbacks são o ponto natural para Langfuse ou OpenTelemetry). O projeto 01 traz em `requirements-extra.txt` as dependências dessas extensões, comentadas.

## Para quem vem de C#

Os comentários `# C#: ...` no código fazem a ponte. Resumo:

| Python | C# |
|---|---|
| type hints (`def f(x: str) -> int`) | tipos na assinatura (`int F(string x)`) |
| `class Settings(BaseSettings)` | configuração tipada (`IOptions<T>`) |
| `@dataclass` | `record` |
| `Protocol` | `interface` com duck typing |
| `Callable[[X], None]` | `Action<X>` |
| `T \| None` | `T?` |
| `async def` / `await` | `async Task` / `await` |
| `.venv` + `pip` + `requirements.txt` | NuGet + `dotnet restore` + `.csproj` |

## Status

Base de estudo estável; não há desenvolvimento ativo.

## Licença

MIT.
