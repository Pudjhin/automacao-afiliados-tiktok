import requests
import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

def enviar_pacote_shopee(pasta_produto):
    url_video = f"https://api.telegram.org/bot{TOKEN}/sendVideo"
    url_texto = f"https://api.telegram.org/bot{TOKEN}/sendMessage"
    
    caminho_video = f"{pasta_produto}/video.mp4"
    caminho_legenda = f"{pasta_produto}/legenda.txt"
    
    try:
        with open(caminho_legenda, 'r', encoding='utf-8') as arquivo_texto:
            texto_legenda = arquivo_texto.read()
    except FileNotFoundError:
        print("Erro: Arquivo legenda.txt não encontrado.")
        return

    try:
        with open(caminho_video, 'rb') as arquivo_video:
            arquivos = {"video": arquivo_video}
            payload_video = {"chat_id": CHAT_ID} # Sem caption agora
            
            print(f"Enviando vídeo da pasta {pasta_produto}...")
            requests.post(url_video, data=payload_video, files=arquivos)
            
    except FileNotFoundError:
        print("Erro: Arquivo video.mp4 não encontrado.")
        return

    print("Enviando legenda...")
    payload_texto = {
        "chat_id": CHAT_ID,
        "text": texto_legenda
    }
    requests.post(url_texto, data=payload_texto)
    
    print("Pacote completo entregue com sucesso no Telegram!")