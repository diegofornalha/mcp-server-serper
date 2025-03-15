"""
Configurações para o servidor MCP Python.
"""

import logging
import os
from typing import Optional

from dotenv import load_dotenv

# Carrega variáveis de ambiente do arquivo .env
load_dotenv()

# Configurações do servidor
HOST: str = os.getenv("HOST", "127.0.0.1")
PORT: int = int(os.getenv("PORT", "3001"))
DEBUG: bool = os.getenv("DEBUG", "False").lower() in ("true", "1", "t")
MCP_TOKEN: Optional[str] = os.getenv("MCP_TOKEN")

# Configurações da API Serper
SERPER_API_KEY: str = os.getenv("SERPER_API_KEY", "")

# Configurações de logging
LOG_LEVEL_MAP = {
    "DEBUG": logging.DEBUG,
    "INFO": logging.INFO,
    "WARNING": logging.WARNING,
    "ERROR": logging.ERROR,
    "CRITICAL": logging.CRITICAL,
}
LOG_LEVEL: int = LOG_LEVEL_MAP.get(
    os.getenv("LOG_LEVEL", "INFO").upper(), logging.INFO
)

# Nome e versão da aplicação
APP_NAME = "MCP Serper Server"
APP_VERSION = "0.1.0"

# URL base para a API Serper
SERPER_API_URL = "https://google.serper.dev"


def validate_config() -> bool:
    """
    Valida as configurações necessárias.

    Returns:
        bool: True se a configuração é válida, False caso contrário
    """
    # Verifica a chave da API Serper
    if not SERPER_API_KEY:
        logging.error(
            "SERPER_API_KEY não definida. "
            "Defina no .env ou variáveis de ambiente."
        )
        return False

    return True 