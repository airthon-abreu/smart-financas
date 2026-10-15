import sys
from pathlib import Path

def obter_diretorio_base() -> Path:
    if getattr(sys, 'frozen', False):
        return Path(sys.executable).resolve().parent
    return Path(__file__).resolve().parent.parent

DIRETORIO_BASE = obter_diretorio_base()
CAMINHO_BANCO = DIRETORIO_BASE / 'financas.db'
PASTA_UPLOADS = DIRETORIO_BASE / 'uploads'
PASTA_FRONTEND = DIRETORIO_BASE / 'frontend'