"""
╔══════════════════════════════════════════════════════════════╗
║                  AGENTE DE CURADORIA                        ║
║              agents/scraper.py                              ║
╠══════════════════════════════════════════════════════════════╣
║  O QUE PREENCHER NESTE ARQUIVO:                             ║
║  1. Suas URLs de afiliado Shopee (linha ~60)                ║
║  2. Suas URLs de afiliado Mercado Livre (linha ~90)         ║
║  3. Opcionalmente: filtros de preço e comissão              ║
╚══════════════════════════════════════════════════════════════╝
"""

import os
import requests
import random
from typing import List, Dict
from dotenv import load_dotenv
from utils.logger import log

load_dotenv()


class ScraperAgent:
    """
    Busca produtos vencedores nas plataformas afiliadas.

    COMO FUNCIONA:
    - Shopee:  usa a API do programa de afiliados para pegar produtos em alta
    - ML:      usa a API do programa de afiliados para o mesmo fim
    - Filtros: comissão mínima, faixa de preço, volume de vendas

    IMPORTANTE:
    Como iniciante, a forma mais SIMPLES e SEGURA é montar
    sua lista manualmente (modo MANUAL abaixo). Quando quiser
    automatizar de verdade, ative o modo API.
    """

    def __init__(self):
        # ── Modo de operação ─────────────────────────────────────
        # "MANUAL" = você cola os produtos no arquivo produtos.json
        # "API"    = busca automática via APIs (requer configuração extra)
        self.modo = "MANUAL"  # ← DEIXE "MANUAL" POR ENQUANTO

        # Filtros de qualidade (ajuste como quiser)
        self.PRECO_MIN       = 20.0   # R$ mínimo
        self.PRECO_MAX       = 120.0  # R$ máximo (impulso)
        self.COMISSAO_MIN    = 8.0    # % mínima de comissão

    # ─────────────────────────────────────────────────────────────
    # MÉTODO PRINCIPAL — chamado pelo main.py
    # ─────────────────────────────────────────────────────────────
    def buscar_produtos(self, keywords: List[str]) -> List[Dict]:
        if self.modo == "MANUAL":
            return self._carregar_manual()
        else:
            return self._buscar_via_api(keywords)

    # ─────────────────────────────────────────────────────────────
    # MODO MANUAL (recomendado para começar)
    # ─────────────────────────────────────────────────────────────
    def _carregar_manual(self) -> List[Dict]:
        """
        Lê o arquivo produtos.json que VOCÊ preenche manualmente.
        Veja o arquivo produtos_exemplo.json para entender o formato.
        """
        caminho = "./produtos.json"

        if not os.path.exists(caminho):
            log("⚠️  produtos.json não encontrado. Usando produtos de exemplo.", level="WARN")
            return self._produtos_exemplo()

        with open(caminho, "r", encoding="utf-8") as f:
            import json
            dados = json.load(f)

        # Aplica filtros de qualidade
        filtrados = [
            p for p in dados
            if self.PRECO_MIN <= p.get("preco", 0) <= self.PRECO_MAX
            and p.get("comissao", 0) >= self.COMISSAO_MIN
        ]

        log(f"📦 {len(filtrados)}/{len(dados)} produtos passaram nos filtros")
        return filtrados

    # ─────────────────────────────────────────────────────────────
    # MODO API (ative depois, quando estiver confortável)
    # ─────────────────────────────────────────────────────────────
    def _buscar_via_api(self, keywords: List[str]) -> List[Dict]:
        """
        ══════════════════════════════════════════════════
        O QUE PREENCHER AQUI (quando ativar o modo API):

        Para Shopee Afiliados:
        1. Acesse: https://affiliate.shopee.com.br
        2. Vá em Ferramentas → API
        3. Pegue seu APP_ID e SECRET
        4. Cole no .env:
           SHOPEE_APP_ID=seu_app_id_aqui
           SHOPEE_SECRET=seu_secret_aqui

        Para Mercado Livre Afiliados:
        1. Acesse: https://www.mercadolivre.com.br/afiliados
        2. Vá em Integrações → API
        3. Pegue seu CLIENT_ID e ACCESS_TOKEN
        4. Cole no .env:
           ML_CLIENT_ID=seu_client_id_aqui
           ML_ACCESS_TOKEN=seu_token_aqui
        ══════════════════════════════════════════════════
        """
        produtos = []

        # ── Shopee ────────────────────────────────────────────────
        shopee_app_id = os.getenv("SHOPEE_APP_ID")
        shopee_secret = os.getenv("SHOPEE_SECRET")

        if shopee_app_id and shopee_secret:
            log("🛍️  Buscando na Shopee via API...")
            # PREENCHA: Implemente a chamada real quando tiver as credenciais
            # Documentação: https://open.affiliate.shopee.com.br/docs
            pass
        else:
            log("⚠️  Credenciais Shopee não configuradas no .env", level="WARN")

        # ── Mercado Livre ─────────────────────────────────────────
        ml_token = os.getenv("ML_ACCESS_TOKEN")

        if ml_token:
            log("🛒  Buscando no Mercado Livre via API...")
            # PREENCHA: Implemente a chamada real quando tiver as credenciais
            # Documentação: https://developers.mercadolivre.com.br
            pass
        else:
            log("⚠️  Credenciais ML não configuradas no .env", level="WARN")

        # Se a API não retornou nada, usa exemplos
        if not produtos:
            log("ℹ️  Usando produtos de exemplo (configure as APIs para busca real)")
            return self._produtos_exemplo()

        return produtos

    # ─────────────────────────────────────────────────────────────
    # PRODUTOS DE EXEMPLO (para testar sem configurar nada)
    # ─────────────────────────────────────────────────────────────
    def _produtos_exemplo(self) -> List[Dict]:
        """
        Produtos fictícios para testar o pipeline sem configurar APIs.
        Substitua pelo produtos.json com dados reais antes de publicar!
        """
        return [
            {
                "id": "prod_001",
                "titulo": "Organizador Giratório para Temperos",
                "descricao": "Suporte giratório de 360° para até 12 potes de tempero. Organiza sua cozinha de forma prática e elegante.",
                "preco": 39.90,
                "preco_original": 59.90,
                "comissao": 12.0,
                "plataforma": "shopee",
                "link_afiliado": "COLE_SEU_LINK_AFILIADO_SHOPEE_AQUI",
                "imagens": [],        # URLs das imagens do produto
                "video_original": "", # URL do vídeo do vendedor (se houver)
                "avaliacao": 4.8,
                "vendas": 230,
            },
            {
                "id": "prod_002",
                "titulo": "Descascador Multifuncional 5 em 1",
                "descricao": "Descasca batata, cenoura, chuchu e mais. Lâmina inox, ergonômico, fácil de limpar.",
                "preco": 24.90,
                "preco_original": 44.90,
                "comissao": 15.0,
                "plataforma": "mercadolivre",
                "link_afiliado": "COLE_SEU_LINK_AFILIADO_ML_AQUI",
                "imagens": [],
                "video_original": "",
                "avaliacao": 4.7,
                "vendas": 415,
            },
            {
                "id": "prod_003",
                "titulo": "Escorredor de Louça com Bandeja Retrátil",
                "descricao": "Ocupa pouco espaço, bandeja retráctil evita água no balcão. Suporta até 8kg.",
                "preco": 67.90,
                "preco_original": 99.90,
                "comissao": 10.0,
                "plataforma": "shopee",
                "link_afiliado": "COLE_SEU_LINK_AFILIADO_SHOPEE_AQUI",
                "imagens": [],
                "video_original": "",
                "avaliacao": 4.9,
                "vendas": 188,
            },
        ]
