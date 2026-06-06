"""
╔══════════════════════════════════════════════════════════════╗
║                   AGENTE DE CRIAÇÃO                         ║
║                  agents/creator.py                          ║
╠══════════════════════════════════════════════════════════════╣
║  O QUE PREENCHER NESTE ARQUIVO:                             ║
║  1. Nada obrigatório — as chaves vêm do .env               ║
║  2. Opcional: ajuste os prompts de roteiro (linha ~70)      ║
║  3. Opcional: troque a fonte do vídeo (linha ~160)          ║
╚══════════════════════════════════════════════════════════════╝
"""

import os
import random
import textwrap
import requests
from typing import Dict
from dotenv import load_dotenv
from utils.logger import log

load_dotenv()

# ── Importações de mídia (instaladas pelo requirements.txt) ──
try:
    from moviepy.editor import (
        ImageClip, AudioFileClip, TextClip, CompositeVideoClip,
        ColorClip, concatenate_videoclips
    )
    from PIL import Image, ImageDraw, ImageFont
    import numpy as np
    MOVIEPY_OK = True
except ImportError:
    MOVIEPY_OK = False
    log("⚠️  moviepy/PIL não instalado. Rode: pip install -r requirements.txt", level="WARN")

try:
    from anthropic import Anthropic
    ANTHROPIC_OK = True
except ImportError:
    ANTHROPIC_OK = False


class CreatorAgent:

    def __init__(self):
        self.output_dir = "./output"
        self.temp_dir   = "./temp"
        os.makedirs(self.output_dir, exist_ok=True)
        os.makedirs(self.temp_dir,   exist_ok=True)

        # Clientes de API
        self.anthropic_key   = os.getenv("ANTHROPIC_API_KEY")
        self.elevenlabs_key  = os.getenv("ELEVENLABS_API_KEY")
        self.elevenlabs_voice = os.getenv("ELEVENLABS_VOICE_ID", "")

    # ════════════════════════════════════════════════════════════
    # ETAPA 1 — GERAR ROTEIRO COM IA
    # ════════════════════════════════════════════════════════════
    def gerar_roteiro(self, produto: Dict) -> str:
        """
        Usa Claude (Anthropic) para criar um roteiro persuasivo de 15-20s.
        Se não tiver chave Anthropic, usa um roteiro-modelo automático.
        """

        if self.anthropic_key and ANTHROPIC_OK:
            return self._roteiro_via_claude(produto)
        else:
            log("ℹ️  Chave Anthropic não configurada. Usando roteiro-modelo.")
            return self._roteiro_modelo(produto)

    def _roteiro_via_claude(self, produto: Dict) -> str:
        client = Anthropic(api_key=self.anthropic_key)

        # ── PROMPT DO ROTEIRO ────────────────────────────────────
        # Você pode customizar este prompt!
        # Dicas:
        #  - "gancho de dor"     = começa com o problema
        #  - "gancho curiosidade"= começa com pergunta
        #  - "gancho oferta"     = começa com o preço/desconto
        tipo_gancho = random.choice(["dor", "curiosidade", "oferta"])

        ganchos = {
            "dor": f"Começa com a DOR do usuário. Exemplo: 'Cansado de [problema]?'",
            "curiosidade": "Começa com curiosidade. Exemplo: 'Você sabia que esse produto resolve [problema] em segundos?'",
            "oferta": f"Começa com o desconto. Exemplo: 'De R${produto['preco_original']:.0f} por R${produto['preco']:.0f}!'",
        }

        prompt = f"""
Você é um criador de conteúdo viral no TikTok especializado em produtos de cozinha e casa.

PRODUTO:
- Nome: {produto['titulo']}
- Descrição: {produto['descricao']}
- Preço: R$ {produto['preco']:.2f}
- Preço original: R$ {produto.get('preco_original', produto['preco'] * 1.5):.2f}

INSTRUÇÕES:
1. Crie um roteiro de narração para um vídeo de 15-20 segundos
2. Tipo de gancho: {ganchos[tipo_gancho]}
3. Tom: jovem, direto, empolgado mas natural — como um amigo recomendando
4. Use linguagem brasileira informal (pode usar "gente", "cara", "olha só")
5. Termine SEMPRE com call to action: "Link na bio pra comprar!" ou "Comenta EU QUERO!"
6. Máximo 80 palavras no total
7. APENAS o texto falado, sem indicações de cena, sem colchetes, sem asteriscos

SAÍDA: apenas o texto da narração, pronto para ser lido em voz alta.
"""

        resposta = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=300,
            messages=[{"role": "user", "content": prompt}]
        )

        roteiro = resposta.content[0].text.strip()
        log(f"   🤖 Roteiro gerado via Claude ({tipo_gancho})")
        return roteiro

    def _roteiro_modelo(self, produto: Dict) -> str:
        """Roteiro automático sem IA — usado como fallback."""
        desconto = produto.get('preco_original', produto['preco'] * 1.4)
        economia = desconto - produto['preco']

        templates = [
            f"Gente, olha que achado! {produto['titulo']} por só R${produto['preco']:.0f}! "
            f"Era R${desconto:.0f}, você economiza R${economia:.0f}! "
            f"Perfeito pra organizar sua cozinha. Link na bio pra comprar!",

            f"Você ainda não tem esse produto na sua cozinha? "
            f"{produto['titulo']} — resolve {produto['descricao'][:50]}... "
            f"Por R${produto['preco']:.0f} tá baratíssimo! Comenta EU QUERO!",

            f"Esse produto aqui mudou minha cozinha! "
            f"{produto['titulo']} com {produto['avaliacao']} estrelas e mais de {produto['vendas']} vendidos. "
            f"Só R${produto['preco']:.0f}! Link na bio!",
        ]

        return random.choice(templates)

    # ════════════════════════════════════════════════════════════
    # ETAPA 2 — GERAR ÁUDIO COM ELEVENLABS
    # ════════════════════════════════════════════════════════════
    def gerar_audio(self, roteiro: str, produto_id: str) -> str:
        """
        Converte o roteiro em áudio MP3 usando ElevenLabs.
        Se não tiver chave, cria um arquivo de áudio silencioso para teste.
        """
        audio_path = f"{self.temp_dir}/audio_{produto_id}.mp3"

        if self.elevenlabs_key and self.elevenlabs_voice:
            return self._audio_via_elevenlabs(roteiro, audio_path)
        else:
            log("ℹ️  ElevenLabs não configurado. Criando áudio silencioso para teste.")
            return self._audio_silencioso(audio_path, duracao=18)

    def _audio_via_elevenlabs(self, roteiro: str, audio_path: str) -> str:
        """
        ══════════════════════════════════════════════════
        COMO CONFIGURAR O ELEVENLABS:
        1. Acesse: https://elevenlabs.io
        2. Crie uma conta gratuita (10.000 caracteres/mês grátis)
        3. Vá em "Voices" → escolha uma voz em português
        4. Clique na voz → copie o "Voice ID"
        5. Vá em seu perfil → API Keys → copie a chave
        6. Cole no .env:
           ELEVENLABS_API_KEY=sua_chave_aqui
           ELEVENLABS_VOICE_ID=id_da_voz_aqui

        VOZES BRASILEIRAS RECOMENDADAS (pesquise por):
        - "Brazilian Portuguese" na biblioteca de vozes
        - Vozes com tag "conversational" ou "social media"
        ══════════════════════════════════════════════════
        """
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{self.elevenlabs_voice}"

        headers = {
            "xi-api-key": self.elevenlabs_key,
            "Content-Type": "application/json"
        }

        payload = {
            "text": roteiro,
            "model_id": "eleven_multilingual_v2",
            "voice_settings": {
                "stability": 0.4,          # Menos estável = mais expressivo
                "similarity_boost": 0.75,
                "style": 0.5,              # Estilo empolgado
                "use_speaker_boost": True
            }
        }

        response = requests.post(url, json=payload, headers=headers)

        if response.status_code == 200:
            with open(audio_path, "wb") as f:
                f.write(response.content)
            log(f"   🎙️  Áudio ElevenLabs salvo")
            return audio_path
        else:
            log(f"   ⚠️  Erro ElevenLabs: {response.status_code} — usando áudio silencioso", level="WARN")
            return self._audio_silencioso(audio_path)

    def _audio_silencioso(self, audio_path: str, duracao: int = 18) -> str:
        """Cria um MP3 silencioso para testar o pipeline sem áudio real."""
        try:
            # Cria áudio silencioso com pydub se disponível
            from pydub import AudioSegment
            silencio = AudioSegment.silent(duration=duracao * 1000)
            silencio.export(audio_path, format="mp3")
        except ImportError:
            # Fallback: arquivo MP3 vazio mínimo
            with open(audio_path, "wb") as f:
                f.write(b"\xff\xfb\x90\x00" * 1000)
        return audio_path

    # ════════════════════════════════════════════════════════════
    # ETAPA 3 — MONTAR VÍDEO COM MOVIEPY
    # ════════════════════════════════════════════════════════════
    def montar_video(self, produto: Dict, audio_path: str, roteiro: str) -> str:
        """
        Cria o vídeo final no formato TikTok (9:16 vertical).
        Usa imagens do produto + legenda + áudio.
        """
        video_path = f"{self.output_dir}/{produto['id']}/video.mp4"
        os.makedirs(f"{self.output_dir}/{produto['id']}", exist_ok=True)

        if not MOVIEPY_OK:
            log("   ⚠️  moviepy não instalado. Vídeo não gerado.", level="WARN")
            return video_path

        return self._montar_com_moviepy(produto, audio_path, roteiro, video_path)

    def _montar_com_moviepy(self, produto, audio_path, roteiro, video_path):
        """
        Montagem do vídeo:
        - Fundo colorido gradiente no estilo TikTok
        - Imagens do produto (se houver) ou placeholder colorido
        - Legenda automática quebrada em linhas
        - Áudio narrado
        """
        LARGURA  = 1080
        ALTURA   = 1920
        DURACAO  = 18   # segundos

        # ── Carrega áudio e ajusta duração ────────────────────────
        try:
            audio = AudioFileClip(audio_path)
            DURACAO = min(audio.duration + 1, 30)  # máx 30s
        except Exception:
            audio = None

        # ── Fundo com cor vibrante (estilo TikTok cozinha) ────────
        cores_nicho = [
            (255, 87,  34),   # laranja vibrante
            (76,  175, 80),   # verde cozinha
            (33,  150, 243),  # azul moderno
            (255, 193, 7),    # amarelo quente
        ]
        cor = random.choice(cores_nicho)
        fundo = ColorClip(size=(LARGURA, ALTURA), color=cor, duration=DURACAO)

        clips = [fundo]

        # ── Tenta baixar e inserir imagem do produto ───────────────
        if produto.get("imagens"):
            try:
                img_url = produto["imagens"][0]
                img_path = f"{self.temp_dir}/img_{produto['id']}.jpg"
                r = requests.get(img_url, timeout=10)
                if r.status_code == 200:
                    with open(img_path, "wb") as f:
                        f.write(r.content)

                    img_clip = (ImageClip(img_path)
                                .resize(width=900)
                                .set_position("center")
                                .set_duration(DURACAO)
                                .set_start(0))
                    clips.append(img_clip)
            except Exception as e:
                log(f"   ℹ️  Imagem não carregada: {e}")

        # ── Legenda no estilo TikTok (palavra por palavra no centro) ──
        # Quebra o roteiro em blocos de ~6 palavras por linha
        linhas = textwrap.wrap(roteiro, width=30)
        bloco_texto = "\n".join(linhas[:6])  # máx 6 linhas no vídeo

        try:
            legenda = (TextClip(
                            bloco_texto,
                            fontsize=58,
                            color="white",
                            font="DejaVu-Sans-Bold",   # ← fonte padrão Linux
                            stroke_color="black",
                            stroke_width=3,
                            method="caption",
                            size=(LARGURA - 80, None),
                            align="center"
                        )
                        .set_position(("center", ALTURA * 0.65))
                        .set_duration(DURACAO))
            clips.append(legenda)
        except Exception as e:
            log(f"   ℹ️  Legenda simplificada (erro na fonte): {e}")

        # ── Texto do preço no topo ─────────────────────────────────
        try:
            preco_txt = (TextClip(
                            f"R$ {produto['preco']:.2f}",
                            fontsize=80,
                            color="yellow",
                            font="DejaVu-Sans-Bold",
                            stroke_color="black",
                            stroke_width=4,
                        )
                        .set_position(("center", 120))
                        .set_duration(DURACAO))
            clips.append(preco_txt)
        except Exception:
            pass

        # ── Monta e exporta ───────────────────────────────────────
        video = CompositeVideoClip(clips, size=(LARGURA, ALTURA))

        if audio:
            video = video.set_audio(audio)

        video.write_videofile(
            video_path,
            fps=30,
            codec="libx264",
            audio_codec="aac",
            temp_audiofile=f"{self.temp_dir}/temp_audio.m4a",
            remove_temp=True,
            verbose=False,
            logger=None
        )

        log(f"   🎬  Vídeo salvo: {video_path}")
        return video_path
