"""Agente virtual de contact center com Gemini (Vertex AI) e function calling.

O agente conversa em português, identifica o cliente, consulta fatura, envia
segunda via, verifica falhas de rede, abre protocolo e transfere para humano.

Uso:
    python agente.py
"""
import os

from google import genai
from google.genai import types

from ferramentas import FERRAMENTAS, PROTOCOLOS

INSTRUCOES = """Você é a Lia, assistente virtual de uma operadora de telecom brasileira.
Regras:
1. Seja cordial, objetiva e escreva em português do Brasil, com frases curtas.
2. Antes de falar de fatura, rede ou protocolo, peça o número do contrato e os 4 últimos
   dígitos do CPF/CNPJ e chame identificar_cliente. Sem identificação, não revele dados.
3. Nunca mostre documentos completos (LGPD). Use só o que as ferramentas devolverem.
4. Se o cliente relatar internet ou linha sem funcionar, chame verificar_rede antes de abrir protocolo.
5. Cancelamento, contestação de valor ou cliente irritado: chame transferir_para_humano.
6. Nunca invente valores, prazos ou números de protocolo.
Hoje é novembro de 2026."""


def criar_chat():
    cliente = genai.Client(
        vertexai=True,
        project=os.environ["GOOGLE_CLOUD_PROJECT"],
        location=os.environ.get("GOOGLE_CLOUD_LOCATION", "us-central1"),
    )
    return cliente.chats.create(
        model=os.environ.get("MODELO", "gemini-2.5-flash"),
        config=types.GenerateContentConfig(
            system_instruction=INSTRUCOES,
            tools=FERRAMENTAS,      # o SDK executa as funções automaticamente (automatic function calling)
            temperature=0.3,
        ),
    )


def main():
    chat = criar_chat()
    print("Lia: Olá! Sou a Lia, assistente virtual. Como posso ajudar? (digite 'sair' para encerrar)")
    while True:
        try:
            pergunta = input("\nVocê: ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if pergunta.lower() in {"sair", "tchau", "encerrar"}:
            break
        if not pergunta:
            continue
        resposta = chat.send_message(pergunta)
        print(f"\nLia: {resposta.text}")

    if PROTOCOLOS:
        print("\nProtocolos abertos nesta conversa:")
        for p in PROTOCOLOS:
            print(f"  {p['protocolo']} – {p['motivo']} (prioridade {p['prioridade']})")
    print("Atendimento encerrado.")


if __name__ == "__main__":
    main()
