#!/usr/bin/env python3

"""
Script simples para testar o servidor MCP.
"""

import asyncio
import logging
import sys

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Importa o cliente do diretório examples
sys.path.append("examples")
from client_example import MCPClient


async def test_health():
    """Testa a ferramenta _health."""
    client = MCPClient("http://localhost:3001", "mcp-serper-token")
    try:
        logger.info("Conectando ao servidor MCP...")
        await client.connect()
        
        logger.info("Enviando requisição _health...")
        await client.send_tool_request("_health", {"random_string": "test"})
        
        logger.info("Aguardando resposta (5s)...")
        await asyncio.sleep(5)
        
    except Exception as e:
        logger.error(f"Erro ao testar: {e}")
    finally:
        # Não chamamos client.close() pois o método não existe
        logger.info("Teste concluído.")


async def test_google_search():
    """Testa a ferramenta google_search."""
    client = MCPClient("http://localhost:3001", "mcp-serper-token")
    try:
        logger.info("Conectando ao servidor MCP...")
        await client.connect()
        
        logger.info("Enviando requisição google_search...")
        await client.send_tool_request(
            "google_search", 
            {
                "q": "Python Model Context Protocol", 
                "gl": "br", 
                "hl": "pt"
            }
        )
        
        logger.info("Aguardando resposta (10s)...")
        await asyncio.sleep(10)
        
    except Exception as e:
        logger.error(f"Erro ao testar: {e}")
    finally:
        logger.info("Teste concluído.")


async def main():
    """Função principal para executar os testes."""
    if len(sys.argv) > 1 and sys.argv[1] == "search":
        await test_google_search()
    else:
        await test_health()


if __name__ == "__main__":
    asyncio.run(main()) 