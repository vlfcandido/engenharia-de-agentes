"""Agente EXECUTOR — realiza o plano e persiste a saida (com tool sandboxed)."""

from __future__ import annotations

from core.llm import LLMClient, extrair_json
from prompts import executor as prompt_executor
from tools.arquivos import escrever_arquivo


class ExecutorAgent:
    papel = "executor"

    # Allow-list: as unicas tools que este agente pode usar (menor privilegio).
    TOOLS_PERMITIDAS = {"escrever_arquivo"}

    def __init__(self, llm: LLMClient) -> None:
        self.llm = llm

    def executar(
        self, objetivo: str, plano: list[str], feedback: str = "", dados_usuario: str = ""
    ) -> dict:
        prompt = prompt_executor.montar(objetivo, plano, feedback, dados_usuario)
        resposta = self.llm.gerar(prompt, papel=self.papel)
        dados = extrair_json(resposta)
        saida = str(dados.get("saida", ""))

        # Acao concreta: persiste a saida usando a tool com sandbox.
        # (a allow-list garante que so tools liberadas rodem)
        if "escrever_arquivo" in self.TOOLS_PERMITIDAS and saida:
            retorno = escrever_arquivo("saida.txt", saida)
            dados.setdefault("resultados", []).append(retorno)

        return {"resultados": dados.get("resultados", []), "saida": saida}
