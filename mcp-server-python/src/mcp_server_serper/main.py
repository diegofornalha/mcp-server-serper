"""
Ponto de entrada principal para o servidor MCP Python.
"""

import logging
import os
import signal
import sys
from .server import MCPServerApp

logger = logging.getLogger(__name__)


def handle_sigterm(*args):
    """Manipula o sinal SIGTERM para encerramento gracioso."""
    logger.info("Recebido sinal de encerramento. Encerrando...")
    sys.exit(0)


def run():
    """
    Função principal para iniciar o servidor MCP.
    """
    # Configura manipuladores de sinais
    signal.signal(signal.SIGINT, handle_sigterm)
    signal.signal(signal.SIGTERM, handle_sigterm)
    
    try:
        # Configura logging
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        )
        
        # Verifica variáveis de ambiente necessárias
        if not os.getenv("SERPER_API_KEY"):
            logger.error("Variável de ambiente SERPER_API_KEY não definida")
            sys.exit(1)
        
        # Inicia o servidor
        server = MCPServerApp()
        server.run()
    except KeyboardInterrupt:
        logger.info("Servidor interrompido pelo usuário.")
    except Exception as e:
        logger.exception(f"Erro ao iniciar o servidor: {e}")
        sys.exit(1)


if __name__ == "__main__":
    run() 