# 🎧 Agente Virtual de Contact Center com Gemini (Function Calling)

A **Lia** é uma assistente virtual de uma operadora de telecom que conversa em português, **identifica o cliente**, **consulta e envia a segunda via da fatura**, **verifica falhas de rede na região**, **abre protocolo** e **transfere para um atendente humano** quando precisa. Ela não só responde: executa as ações chamando funções do "sistema" da operadora.

## 🎯 Problema que resolve
Grande parte das ligações de um contact center de telecom se resume a poucos assuntos repetitivos: segunda via, "minha internet caiu" e status de protocolo. Um agente com IA generativa resolve esses casos sozinho, a qualquer hora, e deixa os atendentes humanos para cancelamentos, contestações e casos complexos.

## 🏗️ Arquitetura
```
Cliente ──► agente.py (chat) ──► Gemini no Vertex AI
                                     │ decide qual ferramenta chamar
                                     ▼
                          ferramentas.py (function calling)
          identificar_cliente · consultar_fatura · enviar_segunda_via
          verificar_rede · abrir_protocolo · transferir_para_humano
                                     │
                                     ▼
                 "Sistemas" simulados (CRM, faturamento, rede, tickets)
```
O Google Gen AI SDK lê os **tipos e docstrings** das funções Python, envia isso ao Gemini como ferramentas e executa automaticamente a função que o modelo escolher (*automatic function calling*).

## 💬 Exemplo de conversa
```
Você: minha internet tá sem funcionar
Lia:  Sinto muito! Para eu verificar, me informe o número do contrato e os 4 últimos dígitos do seu CPF.
Você: contrato 100200, final 8900
Lia:  Obrigada, Mariana. Identifiquei uma manutenção programada na sua região até as 18h de hoje,
      que pode estar afetando sua conexão. Quer que eu abra um protocolo para acompanhamento?
Você: sim, e manda a segunda via de outubro no whatsapp
Lia:  Pronto! Protocolo 202611140001 aberto, com retorno em até 24 horas. A segunda via de outubro
      (R$ 189,90, vencimento 10/11/2026) foi enviada no seu WhatsApp com código de barras e PIX.
```
*(As respostas variam a cada execução: o texto acima ilustra o comportamento esperado.)*

## 🛡️ Regras de negócio e LGPD
- Nenhum dado é mostrado antes de `identificar_cliente` (contrato + 4 últimos dígitos do documento)
- Documentos aparecem sempre mascarados
- Cancelamento e contestação vão para atendimento humano (fila de Retenção)
- O modelo é instruído a nunca inventar valores, prazos ou protocolos: eles vêm sempre das ferramentas

## 🧰 Tecnologias
Python · Google Gen AI SDK (`google-genai`) · Gemini no Vertex AI · Function calling

## 🚀 Como rodar
```bash
git clone https://github.com/MoniqueSilva79/agente-contact-center.git
cd agente-contact-center
pip install -r requirements.txt

# Testar as ferramentas sem nuvem
python ferramentas.py

# Conversar com o agente
gcloud auth application-default login
export GOOGLE_CLOUD_PROJECT=seu-projeto
export GOOGLE_CLOUD_LOCATION=us-central1
python agente.py
```
Clientes de teste: contrato **100200** (final do CPF **8900**) e contrato **100201** (final do CNPJ **0190**).

## 🗺️ Próximos passos
- [ ] Canal de voz com Speech-to-Text e Text-to-Speech
- [ ] Integração com WhatsApp
- [ ] Base de conhecimento (RAG) para dúvidas sobre planos
- [ ] Painel com taxa de resolução sem humano (contenção)

---
Projeto autoral de **Monique da Silva Cruz**, baseado na experiência com soluções de CCaaS e UCaaS para empresas na América Latina. Exemplos oficiais do Vertex AI usados como referência de estudo: [GoogleCloudPlatform/vertex-ai-samples](https://github.com/GoogleCloudPlatform/vertex-ai-samples).
