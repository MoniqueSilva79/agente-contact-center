"""Ferramentas que o agente pode chamar (function calling).

Aqui elas consultam um "sistema" simulado em memória. Em produção, cada função
chamaria a API real (CRM, faturamento, monitoramento de rede, ticketing).
As docstrings e os tipos são lidos pelo Gemini para decidir quando e como chamar
cada função, por isso estão escritos com cuidado.
"""
from datetime import datetime

CLIENTES = {
    "100200": {"nome": "Mariana Alves", "cpf": "123.456.789-00", "cep": "04571-000",
               "plano": "Fibra 600 Mega + Móvel 30GB", "status": "ativo"},
    "100201": {"nome": "Padaria Pão Quente Ltda", "cpf": "12.345.678/0001-90", "cep": "13015-100",
               "plano": "Fibra Empresas 1 Giga + 5 linhas", "status": "ativo"},
}
FATURAS = {
    ("100200", "2026-10"): {"valor": 189.90, "vencimento": "10/11/2026", "situacao": "em aberto"},
    ("100200", "2026-09"): {"valor": 189.90, "vencimento": "10/10/2026", "situacao": "paga"},
    ("100201", "2026-10"): {"valor": 649.00, "vencimento": "15/11/2026", "situacao": "em aberto"},
}
OCORRENCIAS_REDE = {"04571": "Manutenção programada na região até 18h de hoje."}
PROTOCOLOS: list[dict] = []


def _mascarar(documento: str) -> str:
    """Mostra só os 2 últimos dígitos (LGPD)."""
    return "*" * (len(documento) - 2) + documento[-2:]


def identificar_cliente(contrato: str, ultimos_digitos_documento: str) -> dict:
    """Valida a identidade do cliente. Deve ser chamada antes de qualquer outra ferramenta.

    Args:
        contrato: número do contrato informado pelo cliente (6 dígitos).
        ultimos_digitos_documento: os 4 últimos dígitos do CPF ou CNPJ, sem pontuação.
    """
    cliente = CLIENTES.get(contrato.strip())
    if not cliente:
        return {"identificado": False, "motivo": "contrato não encontrado"}
    informado = "".join(c for c in ultimos_digitos_documento if c.isdigit())
    if len(informado) != 4:
        return {"identificado": False, "motivo": "informe exatamente os 4 últimos dígitos do documento"}
    digitos = "".join(c for c in cliente["cpf"] if c.isdigit())
    if not digitos.endswith(informado):
        return {"identificado": False, "motivo": "documento não confere"}
    return {"identificado": True, "nome": cliente["nome"], "plano": cliente["plano"],
            "documento": _mascarar(cliente["cpf"])}


def consultar_fatura(contrato: str, mes_referencia: str) -> dict:
    """Consulta valor, vencimento e situação de uma fatura.

    Args:
        contrato: número do contrato já identificado.
        mes_referencia: mês no formato AAAA-MM, por exemplo 2026-10.
    """
    fatura = FATURAS.get((contrato, mes_referencia))
    return fatura or {"erro": f"fatura de {mes_referencia} não encontrada para o contrato"}


def enviar_segunda_via(contrato: str, mes_referencia: str, canal: str) -> dict:
    """Envia a segunda via da fatura pelo canal escolhido pelo cliente.

    Args:
        contrato: número do contrato já identificado.
        mes_referencia: mês no formato AAAA-MM.
        canal: "email" ou "whatsapp".
    """
    if (contrato, mes_referencia) not in FATURAS:
        return {"enviado": False, "motivo": "fatura não encontrada"}
    if canal not in ("email", "whatsapp"):
        return {"enviado": False, "motivo": "canal inválido, use email ou whatsapp"}
    return {"enviado": True, "canal": canal, "observacao": "código de barras e PIX copia e cola enviados"}


def verificar_rede(contrato: str) -> dict:
    """Verifica se há falha ou manutenção na rede da região do cliente.

    Args:
        contrato: número do contrato já identificado.
    """
    cliente = CLIENTES.get(contrato)
    if not cliente:
        return {"erro": "contrato não encontrado"}
    ocorrencia = OCORRENCIAS_REDE.get(cliente["cep"][:5])
    return {"ocorrencia_na_regiao": bool(ocorrencia), "detalhe": ocorrencia or "nenhuma falha conhecida"}


def abrir_protocolo(contrato: str, motivo: str, prioridade: str) -> dict:
    """Abre um protocolo de atendimento para acompanhamento técnico ou financeiro.

    Args:
        contrato: número do contrato já identificado.
        motivo: descrição curta do problema.
        prioridade: "alta" se o serviço está totalmente parado, senão "normal".
    """
    numero = f"{datetime.now():%Y%m%d}{len(PROTOCOLOS) + 1:04d}"
    PROTOCOLOS.append({"protocolo": numero, "contrato": contrato, "motivo": motivo, "prioridade": prioridade})
    prazo = "4 horas" if prioridade == "alta" else "24 horas"
    return {"protocolo": numero, "prazo_retorno": prazo}


def transferir_para_humano(motivo: str) -> dict:
    """Transfere a conversa para um atendente humano.

    Use quando o cliente pedir, estiver muito insatisfeito, ou o assunto for
    cancelamento, contestação de valor ou algo que as outras ferramentas não resolvem.

    Args:
        motivo: resumo do caso para o atendente não precisar perguntar de novo.
    """
    return {"transferido": True, "fila": "Retenção" if "cancel" in motivo.lower() else "Atendimento N1",
            "tempo_estimado_minutos": 3}


FERRAMENTAS = [identificar_cliente, consultar_fatura, enviar_segunda_via,
               verificar_rede, abrir_protocolo, transferir_para_humano]


if __name__ == "__main__":
    # Autoteste rápido das ferramentas (não precisa de nuvem)
    print(identificar_cliente("100200", "8900"))
    print(identificar_cliente("100200", "1111"))
    print(consultar_fatura("100200", "2026-10"))
    print(enviar_segunda_via("100200", "2026-10", "whatsapp"))
    print(verificar_rede("100200"))
    print(abrir_protocolo("100201", "internet parada na loja", "alta"))
    print(transferir_para_humano("cliente quer cancelar o plano"))
