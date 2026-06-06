"""
╔══════════════════════════════════════════════════════════════╗
║         AGENTE AFILIADO - COZINHA/CASA  (main.py)           ║
║  Orquestrador principal. Rode este arquivo para iniciar.    ║
╚══════════════════════════════════════════════════════════════╝

COMO USAR:
  1. Preencha o arquivo .env com suas chaves
  2. Rode: python main.py
  3. Os vídeos prontos ficam na pasta /output
"""

import os
import time
import json
import PIL.Image
PIL.Image.ANTIALIAS = PIL.Image.LANCZOS
from dotenv import load_dotenv
load_dotenv()
from agents.scraper import ScraperAgent
from agents.creator import CreatorAgent
from agents.exporter import ExporterAgent
from utils.logger import log
from telegram_bot import enviar_pacote_shopee

def main():
    log("🚀 Iniciando Agente Afiliado...")

    # ─── Inicializa os 3 agentes ───────────────────────────────────
    scraper  = ScraperAgent()
    creator  = CreatorAgent()
    exporter = ExporterAgent()

    # ─── Palavras-chave do nicho Cozinha/Casa ─────────────────────
    keywords = [
        "organizador cozinha",
        "utensílios cozinha",
        "gadgets casa",
        "porta temperos",
        "escorredor louça",
        "panela antiaderente",
        "descascador legumes",
        "espátula silicone",
    ]

    log(f"🔍 Buscando produtos para {len(keywords)} palavras-chave...")
    produtos = scraper.buscar_produtos(keywords)

    if not produtos:
        log("⚠️  Nenhum produto encontrado. Verifique o scraper.py.", level="WARN")
        return

    log(f"✅ {len(produtos)} produtos encontrados. Gerando vídeos...")

    resultados = []
    for i, produto in enumerate(produtos):
        log(f"\n📦 [{i+1}/{len(produtos)}] Processando: {produto['titulo']}")

        try:
            # 1. Gera roteiro
            roteiro = creator.gerar_roteiro(produto)
            log(f"   ✍️  Roteiro gerado ({len(roteiro)} chars)")

            # 2. Gera áudio
            audio_path = creator.gerar_audio(roteiro, produto['id'])
            log(f"   🎙️  Áudio salvo: {audio_path}")

            # 3. Monta vídeo
            video_path = creator.montar_video(produto, audio_path, roteiro)
            log(f"   🎬  Vídeo montado: {video_path}")

            # 4. Exporta pacote (vídeo + legenda + link)
            pacote = exporter.exportar(produto, video_path, roteiro)
            log(f"   📤  Pacote exportado: {pacote['pasta']}")

            log(f" Enviando pacote para o Telegram...")
            enviar_pacote_shopee(pacote['pasta'])

            resultados.append({"produto": produto['titulo'], "status": "OK", "pasta": pacote['pasta']})

        except Exception as e:
            log(f"   ❌ Erro: {e}", level="ERROR")
            resultados.append({"produto": produto['titulo'], "status": "ERRO", "motivo": str(e)})

        # Pausa entre produtos para não sobrecarregar APIs
        time.sleep(3)

    # ─── Resumo Final ─────────────────────────────────────────────
    log("\n" + "═"*50)
    log("📊 RESUMO FINAL:")
    ok    = sum(1 for r in resultados if r['status'] == 'OK')
    erro  = len(resultados) - ok
    log(f"   ✅ Sucessos: {ok}")
    log(f"   ❌ Erros:    {erro}")
    log(f"\n📁 Vídeos prontos em: ./output/")
    log("   Abra cada pasta e você encontrará:")
    log("   • video.mp4  → Suba no TikTok")
    log("   • legenda.txt → Cole na descrição do TikTok")
    log("   • link.txt   → Link afiliado do produto")
    log("═"*50)

    # Salva log de resultados
    with open("./output/resultados.json", "w", encoding="utf-8") as f:
        json.dump(resultados, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    main()
