"""Agente EXECUTOR (gerador de sites) — escreve os arquivos do site (com sandbox)."""

from __future__ import annotations

from core.llm import LLMClient, extrair_json
from prompts import executor as prompt_executor
from tools.arquivos import escrever_arquivo


class ExecutorAgent:
    papel = "executor"

    # Allow-list: a unica tool liberada e escrever arquivo (no sandbox workspace/).
    TOOLS_PERMITIDAS = {"escrever_arquivo"}

    def __init__(self, llm: LLMClient) -> None:
        self.llm = llm

    def executar(
        self, objetivo: str, plano: list[str], feedback: str = "", dados_usuario: str = ""
    ) -> dict:
        prompt = prompt_executor.montar(objetivo, plano, feedback, dados_usuario)
        resposta = self.llm.gerar(prompt, papel=self.papel)
        dados = extrair_json(resposta)

        # Acao concreta: escreve CADA arquivo gerado, via a tool com sandbox.
        arquivos = dados.get("arquivos", {})
        resultados = list(dados.get("resultados", []))
        for nome, conteudo in arquivos.items():
            if "escrever_arquivo" in self.TOOLS_PERMITIDAS:
                resultados.append(escrever_arquivo(str(nome), str(conteudo)))

        return {"resultados": resultados, "saida": str(dados.get("saida", "")), "arquivos": list(arquivos)}
