#!/usr/bin/env python

"""
Cliente MCP SSE simplificado para conexão com servidor MCP.
"""

import sys
import json
import requests
import logging
import threading
import time
from sseclient import SSEClient

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class SimpleMCPClient:
    def __init__(self, server_url, auth_token=None):
        self.server_url = server_url
        self.session_id = None
        self.headers = {
            'Content-Type': 'application/json'
        }
        
        if auth_token:
            self.headers['Authorization'] = f'Bearer {auth_token}'
        
        # Para armazenar a conexão SSE
        self.sse_client = None
        self.message_thread = None
        self.running = False
    
    def start(self):
        """Inicia a conexão SSE com o servidor MCP."""
        try:
            # Iniciar conexão SSE
            logger.info(f"Conectando ao servidor MCP em {self.server_url}")
            
            # Usar o requests para fazer a requisição com os headers
            response = requests.get(self.server_url, headers=self.headers, stream=True)
            
            if response.status_code != 200:
                logger.error(
                    f"Erro na conexão: {response.status_code} - {response.text}"
                )
                return False
            
            self.sse_client = SSEClient(response)
            
            # Primeiro evento deve ser a conexão
            for event in self.sse_client:
                if event.event == 'connected':
                    data = json.loads(event.data)
                    self.session_id = data.get('sessionId')
                    logger.info(
                        f"Conectado ao servidor MCP. SessionID: {self.session_id}"
                    )
                    break
            
            if not self.session_id:
                logger.error("Falha ao obter sessionId do servidor")
                return False
            
            # Iniciar thread para escutar eventos
            self.running = True
            self.message_thread = threading.Thread(target=self._listen_events)
            self.message_thread.daemon = True
            self.message_thread.start()
            
            # Solicitar lista de ferramentas
            self.list_tools()
            
            return True
            
        except Exception as e:
            logger.error(f"Erro ao conectar ao servidor: {e}")
            return False
    
    def _listen_events(self):
        """Escuta eventos do servidor SSE."""
        try:
            for event in self.sse_client:
                if not self.running:
                    break
                
                if event.event == 'message':
                    try:
                        data = json.loads(event.data)
                        logger.info(
                            f"Recebida mensagem: {json.dumps(data, indent=2)}"
                        )
                        
                        # Processar resultado
                        if "result" in data:
                            if "tools" in data["result"]:
                                print("\nFerramentas disponíveis:")
                                for tool in data["result"]["tools"]:
                                    print(
                                        f"  - {tool['name']}: {tool['description']}"
                                    )
                                print()
                            elif "content" in data["result"]:
                                for content in data["result"]["content"]:
                                    if content["type"] == "text":
                                        try:
                                            # Tentar analisar como JSON
                                            result_data = json.loads(
                                                content["text"]
                                            )
                                            print(
                                                f"\nResultado: "
                                                f"{json.dumps(result_data, indent=2, ensure_ascii=False)}"
                                            )
                                        except Exception as json_err:
                                            # Se não for JSON, mostrar como texto
                                            print(
                                                f"\nResultado: {content['text']}"
                                            )
                        
                        # Processar erro
                        if "error" in data:
                            print(f"\nErro: {data['error']['message']}")
                            
                    except Exception as e:
                        logger.error(f"Erro ao processar evento: {e}")
                
        except Exception as e:
            if self.running:
                logger.error(f"Erro no loop de eventos: {e}")
    
    def send_message(self, method, params, request_id=None):
        """Envia uma mensagem para o servidor MCP."""
        if not self.session_id:
            logger.error("Nenhuma conexão ativa com o servidor")
            return False
        
        if request_id is None:
            request_id = int(time.time() * 1000)
        
        message = {
            "jsonrpc": "2.0",
            "id": request_id,
            "method": method,
            "params": params
        }
        
        message_endpoint = f"{self.server_url}-message"
        
        # Adicionar o session_id como header X-MCP-Session-ID
        headers = self.headers.copy()
        headers['X-MCP-Session-ID'] = self.session_id
        
        try:
            logger.info(f"Enviando mensagem: {json.dumps(message)}")
            response = requests.post(
                message_endpoint, json=message, headers=headers
            )
            
            if response.status_code != 202:
                logger.error(
                    f"Erro na mensagem: {response.status_code} - {response.text}"
                )
                return False
            
            return True
        except Exception as e:
            logger.error(f"Erro ao enviar mensagem: {e}")
            return False
    
    def list_tools(self):
        """Lista as ferramentas disponíveis no servidor MCP."""
        return self.send_message("listTools", {})
    
    def call_tool(self, tool_name, arguments):
        """Chama uma ferramenta no servidor MCP."""
        return self.send_message("callTool", {
            "name": tool_name,
            "arguments": arguments
        })
    
    def close(self):
        """Encerra a conexão com o servidor."""
        self.running = False
        if self.sse_client:
            self.sse_client.close()
        
        if self.message_thread and self.message_thread.is_alive():
            self.message_thread.join(timeout=1.0)
            
        logger.info("Conexão encerrada")


def main():
    if len(sys.argv) < 2:
        print(f"Uso: {sys.argv[0]} <server_url> [auth_token]")
        sys.exit(1)
    
    server_url = sys.argv[1]
    auth_token = sys.argv[2] if len(sys.argv) > 2 else "mcp-serper-token"
    
    client = SimpleMCPClient(server_url, auth_token)
    
    if not client.start():
        logger.error("Falha ao iniciar o cliente MCP")
        sys.exit(1)
    
    print("Cliente MCP iniciado. Digite suas consultas ou 'quit' para sair.")
    print("Exemplos de comandos:")
    print("  google_search [país] [idioma] [consulta]")
    print("  scrape [url]")
    print("  _health")
    
    try:
        while True:
            cmd = input("\n> ").strip()
            if not cmd:
                continue
                
            if cmd.lower() == 'quit':
                break
            
            parts = cmd.split(maxsplit=3)
            if len(parts) < 1:
                print("Comando inválido.")
                continue
            
            tool_name = parts[0]
            
            if tool_name == "google_search":
                if len(parts) < 4:
                    print("Uso: google_search <gl> <hl> <consulta>")
                    print("Exemplo: google_search br pt inteligência artificial")
                    continue
                gl, hl, query = parts[1], parts[2], parts[3]
                client.call_tool("google_search", {
                    "q": query,
                    "gl": gl,
                    "hl": hl
                })
            
            elif tool_name == "scrape":
                if len(parts) < 2:
                    print("Uso: scrape <url>")
                    print("Exemplo: scrape https://modelcontextprotocol.io")
                    continue
                url = parts[1]
                client.call_tool("scrape", {
                    "url": url,
                    "includeMarkdown": False
                })
            
            elif tool_name == "_health":
                client.call_tool("_health", {
                    "random_string": "test"
                })
                
            else:
                print(f"Ferramenta desconhecida: {tool_name}")
    
    except KeyboardInterrupt:
        print("\nEncerrando...")
    finally:
        client.close()


if __name__ == "__main__":
    main() 