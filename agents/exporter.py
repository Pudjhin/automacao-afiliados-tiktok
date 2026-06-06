"""
╔══════════════════════════════════════════════════════════════╗
║                   AGENTE DE EXPORTAÇÃO                      ║
║                  agents/exporter.py                         ║
╠══════════════════════════════════════════════════════════════╣
║  O QUE PREENCHER NESTE ARQUIVO:                             ║
║  1. Seus hashtags favoritos do nicho (linha ~55)            ║
║  2. Seu @ do TikTok (linha ~60) para o rodapé               ║
╚══════════════════════════════════════════════════════════════╝
"""

import os
import json
from typing import Dict
from utils.logger import log


class ExporterAgent:
    """
    Cria a pasta final de cada produto com:
    - video.mp4       → sobe direto no TikTok
    - legenda.txt     → cola na descrição do vídeo
    - link.txt        → link afiliado já formatado
    - produto.json    → dados completos do produto
    """

    def __init__(self):
        self.output_dir = "./output"

        # ══════════════════════════════════════════════════════════
        # PREENCHA: Seus hashtags do nicho Cozinha/Casa
        # Dica: misture hashtags grandes (#cozinha) com médias
        # (#organizacaocozinha) para melhor alcance orgânico.
        # ══════════════════════════════════════════════════════════
        self.hashtags_nicho = [
            "#cozinha", "#organizacaocozinha", "#dicasdecozinha",
            "#casaorganizada", "#utilidadesdomesticas", "#gadgetscozinha",
            "#achados", "#achadosdashopee", "#achadosdomercadolivre",
            "#produtosvirais", "#decoracaocasa", "#cozinhaorganizada",
            "#recicandoacasa", "#househacks", "#kitchenhacks",
        ]

        # ══════════════════════════════════════════════════════════
        # PREENCHA: Seu @ do TikTok (sem o @)
        # Exemplo: "gilmar.oficial" ou "achadinhosdacozinha"
        # ══════════════════════════════════════════════════════════
        self.seu_tiktok = "SEU_USUARIO_TIKTOK_AQUI"

    def exportar(self, produto: Dict, video_path: str, roteiro: str) -> Dict:
        """
        Monta o pacote completo de publicação para um produto.
        Retorna dict com caminhos dos arquivos gerados.
        """
        pasta = f"{self.output_dir}/{produto['id']}"
        os.makedirs(pasta, exist_ok=True)

        # 1. Legenda otimizada para TikTok
        legenda = self._gerar_legenda(produto, roteiro)
        with open(f"{pasta}/legenda.txt", "w", encoding="utf-8") as f:
            f.write(legenda)

        # 2. Link afiliado formatado
        link_info = self._formatar_link(produto)
        with open(f"{pasta}/link.txt", "w", encoding="utf-8") as f:
            f.write(link_info)

        # 3. Dados completos do produto
        with open(f"{pasta}/produto.json", "w", encoding="utf-8") as f:
            json.dump(produto, f, ensure_ascii=False, indent=2)

        # 4. README de instruções de postagem
        instrucoes = self._gerar_instrucoes(produto)
        with open(f"{pasta}/INSTRUCOES_POSTAGEM.txt", "w", encoding="utf-8") as f:
            f.write(instrucoes)

        log(f"   📁  Pacote completo salvo em: {pasta}/")

        return {
            "pasta":    pasta,
            "video":    video_path,
            "legenda":  f"{pasta}/legenda.txt",
            "link":     f"{pasta}/link.txt",
        }

    def _gerar_legenda(self, produto: Dict, roteiro: str) -> str:
        """
        Cria a legenda completa para colar no TikTok.
        Formato ideal: gancho curto + hashtags.
        """
        # Pega as 2 primeiras frases do roteiro como gancho
        frases = roteiro.split(".")
        gancho = ". ".join(frases[:2]).strip()
        if not gancho.endswith("."):
            gancho += "."

        # Seleciona 8-10 hashtags aleatórias (parece mais natural)
        import random
        hashtags_selecionadas = random.sample(self.hashtags_nicho, min(10, len(self.hashtags_nicho)))

        legenda = f"""{gancho}

🔗 Link na bio para comprar!

{" ".join(hashtags_selecionadas)}

@{self.seu_tiktok}"""

        return legenda

    def _formatar_link(self, produto: Dict) -> str:
        """Formata as instruções de link para bio."""
        plataforma = produto.get("plataforma", "shopee").title()

        return f"""LINK AFILIADO — {produto['titulo']}
{'='*50}

Plataforma: {plataforma}
Preço atual: R$ {produto['preco']:.2f}
Comissão:    {produto.get('comissao', '?')}%

LINK DIRETO:
{produto.get('link_afiliado', 'CONFIGURE SEU LINK AFILIADO NO produtos.json')}

{'='*50}
COMO USAR:
1. Coloque este link no seu perfil do TikTok (bio)
2. Ou use um serviço de "link na bio" (Linktree, Beacons, etc.)
   e adicione este produto lá
3. Quando alguém comprar pelo seu link, você ganha a comissão!

DICA: Troque o link na bio ANTES de postar o vídeo.
"""

    def _gerar_instrucoes(self, produto: Dict) -> str:
        return f"""INSTRUÇÕES DE POSTAGEM — {produto['titulo']}
{'='*50}

PASSO A PASSO:

1. ANTES DE POSTAR:
   ✅ Coloque o link afiliado (arquivo link.txt) na sua bio do TikTok
   ✅ Se usar Linktree: adicione o produto lá e coloque o Linktree na bio

2. UPLOAD DO VÍDEO:
   ✅ Abra o TikTok → botão "+"
   ✅ Selecione o arquivo: video.mp4
   ✅ NÃO corte nem edite o vídeo no TikTok (já está pronto)

3. LEGENDA:
   ✅ Abra o arquivo legenda.txt
   ✅ Copie TODO o conteúdo
   ✅ Cole no campo de descrição do TikTok

4. CONFIGURAÇÕES:
   ✅ Permitir comentários (essencial para engajamento)
   ✅ Permitir dueto e stitch
   ✅ Visibilidade: Público

5. MELHOR HORÁRIO PARA POSTAR:
   📅 Dias úteis: 07h-09h | 12h-14h | 19h-21h
   📅 Fim de semana: 10h-12h | 20h-22h
   (horário de Brasília)

6. APÓS POSTAR:
   ✅ Responda os primeiros comentários em até 30 minutos
   ✅ Se alguém perguntar onde compra: responda "link na bio!"
   ✅ NÃO delete o vídeo mesmo se tiver poucas views nas 1as horas

{'='*50}
Produto ID: {produto['id']}
Gerado pelo Agente Afiliado 🤖
"""
