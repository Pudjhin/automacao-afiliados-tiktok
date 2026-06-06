"""utils/logger.py — Sistema de log colorido no terminal"""
import datetime

CORES = {
    "INFO":  "\033[96m",   # Ciano
    "WARN":  "\033[93m",   # Amarelo
    "ERROR": "\033[91m",   # Vermelho
    "OK":    "\033[92m",   # Verde
    "RESET": "\033[0m",
}

def log(mensagem: str, level: str = "INFO"):
    hora = datetime.datetime.now().strftime("%H:%M:%S")
    cor  = CORES.get(level, CORES["INFO"])
    print(f"{cor}[{hora}] {mensagem}{CORES['RESET']}")
