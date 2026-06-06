# TikTok/Shorts Automation Agent

Um pipeline completo construído em Python para automatizar de ponta a ponta a criação de vídeos verticais para programas de afiliados. 

Este projeto foi desenvolvido para resolver o problema de gargalo na criação de conteúdo digital, orquestrando inteligência artificial para geração de roteiros, narração neural e edição de vídeo programática, com entrega automatizada diretamente via mensageria.

## Arquitetura e Funcionalidades

O sistema funciona lendo uma base de dados de produtos (`produtos.json`) e executando o seguinte fluxo:

1. **Geração de Roteiros (IA):** Integração via API REST com o **Claude (Anthropic)** para elaborar roteiros persuasivos com foco em conversão e retenção nos primeiros segundos.
2. **Síntese de Voz (TTS):** Conexão com a API da **ElevenLabs** para transformar os roteiros gerados em áudios com vozes neurais de alta fidelidade e realismo.
3. **Edição Programática:** Utilização da biblioteca `moviepy` para processar e renderizar vídeos no formato vertical (1080x1920), sincronizando a duração do vídeo com o áudio gerado.
4. **Notificação e Entrega:** Integração com a API do **Telegram** para enviar o pacote finalizado (Vídeo + Legenda + Links) diretamente para o dispositivo do usuário.

## Stack Tecnológico

- **Linguagem Principal:** Python 3
- **Processamento de Mídia:** MoviePy, Pillow, NumPy
- **Integração de APIs e Web:** `requests`, manipulação de rotas RESTful
- **Gerenciamento de Ambiente:** `python-dotenv` para segurança de credenciais (API Keys)

## Aprendizados e Resolução de Problemas

Durante o desenvolvimento deste projeto, enfrentei desafios reais de engenharia, como:
- Separação de responsabilidades no código (arquitetura modular em pastas como `agents` e `utils`).
- Tratamento de variáveis de ambiente para isolar chaves de acesso e proteger a privacidade das contas.
- Manipulação assíncrona de arquivos pesados de mídia via código.

## Sobre o Desenvolvedor

Desenvolvido por Brenno, estudante de Ciência da Computação na Universidade Federal do ABC (UFABC). 

Este projeto é resultado da aplicação prática de lógica de programação, consumo de APIs e automação de fluxos de trabalho para resolver problemas reais do mercado de criadores de conteúdo e marketing digital.

---
*Nota: Este repositório contém a lógica central e a integração das ferramentas. Por questões de segurança, chaves de API, Tokens do Telegram e dados de clientes foram removidos ou substituídos por templates em `.env.exemplo`.*
