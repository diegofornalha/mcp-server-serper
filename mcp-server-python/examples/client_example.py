#!/usr/bin/env python3
"""
Exemplo de cliente MCP em Python para se conectar ao servidor MCP Serper.
"""

import asyncio
import json
import logging
import os
import sys
import uuid
from typing import Dict, Any, List, Optional

import httpx
import sseclient

# Configura logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


class MCPClient:
    """Cliente MCP para se conectar ao servidor MCP Serper via SSE."""

    def __init__(self, server_url: str, auth_token: Optional[str] = None):
        """
        Inicializa o cliente MCP.

        Args:
            server_url: URL do servidor MCP, ex: http://localhost:3001
            auth_token: Token de autenticação (opcional)
        """
        self.server_url = server_url.rstrip("/")
        self.sse_url = f"{self.server_url}/sse"
        self.messages_url = f"{self.server_url}/messages"
        self.auth_token = auth_token
        self.session_id = str(uuid.uuid4())
        self.headers = {}
        
        if auth_token:
            self.headers["Authorization"] = f"Bearer {auth_token}"

        # Armazena as ferramentas disponíveis no servidor
        self.tools: List[Dict[str, Any]] = []

    async def connect(self):
        """Conecta ao servidor MCP via SSE e processa eventos."""
        logger.info(f"Conectando ao servidor MCP em {self.sse_url}")
        
        # Adiciona session_id como cabeçalho, não como parâmetro de consulta
        headers = {**self.headers, "X-MCP-Session-ID": self.session_id}
        
        # Cria uma sessão HTTP para a conexão SSE
        with httpx.Client(timeout=None) as client:
            response = client.get(self.sse_url, headers=headers, stream=True)
            
            if response.status_code != 200:
                logger.error(
                    f"Falha ao conectar: {response.status_code} {response.text}"
                )
                return
            
            client = sseclient.SSEClient(response)
            
            for event in client.events():
                if event.event == "open":
                    logger.info("Conexão SSE estabelecida")
                    await self._process_open_event(event.data)
                elif event.event == "message":
                    await self._process_message_event(event.data)
                elif event.event == "error":
                    logger.error(f"Erro SSE: {event.data}")
                    break
    
    async def _process_open_event(self, data: str):
        """Processa o evento open do SSE que contém as ferramentas."""
        try:
            open_data = json.loads(data)
            self.tools = open_data.get("tools", [])
            logger.info(f"Ferramentas disponíveis: {len(self.tools)}")
            
            for tool in self.tools:
                logger.info(f"  - {tool.get('name')}: {tool.get('description')}")
            
            logger.info("Cliente MCP iniciado. Digite suas consultas ou 'quit' para sair.")
        except json.JSONDecodeError as e:
            logger.error(f"Erro ao processar evento open: {e}")
    
    async def _process_message_event(self, data: str):
        """Processa mensagens recebidas do servidor."""
        try:
            message = json.loads(data)
            message_type = message.get("type")
            
            if message_type == "toolResult":
                tool_name = message.get("name", "desconhecido")
                result = message.get("result", {})
                logger.info(f"Resultado da ferramenta '{tool_name}':")
                print(json.dumps(result, indent=2, ensure_ascii=False))
            elif message_type == "error":
                logger.error(f"Erro: {message.get('error')}")
            else:
                logger.info(f"Mensagem recebida: {message}")
        except json.JSONDecodeError as e:
            logger.error(f"Erro ao processar mensagem: {e}")
    
    async def send_message(self, query: str):
        """
        Envia uma mensagem ao servidor MCP.

        Args:
            query: Consulta a ser enviada
        """
        if query.lower() == "quit":
            logger.info("Encerrando cliente...")
            return False
        
        message = {
            "type": "toolInvocation",
            "query": query,
            "parameters": {},
        }
        
        # Adiciona session_id como cabeçalho, não como parâmetro de consulta
        headers = {**self.headers, "X-MCP-Session-ID": self.session_id}
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    self.messages_url,
                    json=message,
                    headers=headers,
                )
                
                if response.status_code != 200:
                    logger.error(
                        f"Erro ao enviar mensagem: {response.status_code} "
                        f"{response.text}"
                    )
        except Exception as e:
            logger.error(f"Erro ao enviar mensagem: {e}")
        
        return True
    
    async def run_interactive(self):
        """Executa o cliente em modo interativo."""
        # Inicia a conexão SSE em uma tarefa separada
        sse_task = asyncio.create_task(self.connect())
        
        # Pequena pausa para garantir que a conexão SSE seja estabelecida
        await asyncio.sleep(1)
        
        try:
            while True:
                query = input("\n> ")
                continue_running = await self.send_message(query)
                
                if not continue_running:
                    break
        except KeyboardInterrupt:
            logger.info("Cliente interrompido pelo usuário.")
        finally:
            sse_task.cancel()


async def main():
    """Função principal do exemplo de cliente."""
    if len(sys.argv) < 2:
        print(f"Uso: {sys.argv[0]} URL_SERVIDOR [TOKEN]")
        print(f"Exemplo: {sys.argv[0]} http://localhost:3001 meu-token")
        sys.exit(1)
    
    server_url = sys.argv[1]
    auth_token = None
    
    if len(sys.argv) > 2:
        auth_token = sys.argv[2]
    elif os.getenv("MCP_TOKEN"):
        auth_token = os.getenv("MCP_TOKEN")
    
    client = MCPClient(server_url, auth_token)
    await client.run_interactive()


if __name__ == "__main__":
    asyncio.run(main()) 