#!/usr/bin/env python

"""
Cliente MCP para conexão com servidor compatível com o Model Context Protocol.

Este cliente implementa a especificação MCP e usa o header X-MCP-Session-ID
para autenticação de sessão em conformidade com a especificação.
"""

import sys
import json
import requests
import logging
import threading
import time

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class MCPClient:
    def __init__(self, server_url, auth_token=None):
        """
        Inicializa o cliente MCP.
        
        Args:
            server_url: URL do servidor MCP SSE
            auth_token: Token de autenticação Bearer opcional
        """
        self.server_url = server_url
        self.session_id = None
        self.headers = {
            'Accept': 'text/event-stream',
            'Cache-Control': 'no-cache',
        }
        
        if auth_token:
            self.headers['Authorization'] = f'Bearer {auth_token}'
        
        # Para armazenar a conexão e threads
        self.sse_response = None
        self.event_thread = None
        self.running = False
    
    def start(self):
        """Inicia a conexão SSE com o servidor MCP."""
        try:
            # Iniciar conexão SSE
            logger.info(f"Conectando ao servidor MCP em {self.server_url}")
            
            self.sse_response = requests.get(
                self.server_url, 
                headers=self.headers, 
                stream=True
            )
            
            if self.sse_response.status_code != 200:
                logger.error(
                    f"Erro na conexão: {self.sse_response.status_code} - "
                    f"{self.sse_response.text}"
                )
                return False
            
            logger.info(f"Conexão estabelecida: {self.sse_response.status_code}")
            
            # Iniciar thread para escutar eventos
            self.running = True
            self.event_thread = threading.Thread(target=self._process_events)
            self.event_thread.daemon = True
            self.event_thread.start()
            
            # Aguardar obtenção do sessionId
            timeout = 10  # segundos
            start_time = time.time()
            while not self.session_id and time.time() - start_time < timeout:
                time.sleep(0.1)
            
            if not self.session_id:
                logger.error("Timeout ao esperar pelo sessionId")
                self.close()
                return False
                
            # Solicitar lista de ferramentas
            self.list_tools()
            
            return True
            
        except Exception as e:
            logger.error(f"Erro ao conectar ao servidor: {e}")
            return False
    
    def _process_events(self):
        """Processa eventos SSE do servidor."""
        buffer = ""
        try:
            for chunk in self.sse_response.iter_content(chunk_size=1):
                if not self.running:
                    break
                    
                if chunk:
                    chunk_str = chunk.decode('utf-8')
                    buffer += chunk_str
                    
                    if buffer.endswith('\n\n'):
                        # Evento completo
                        lines = buffer.strip().split('\n')
                        buffer = ""
                        
                        event_type = None
                        data = None
                        
                        for line in lines:
                            if line.startswith('event:'):
                                event_type = line[6:].strip()
                            elif line.startswith('data:'):
                                data = line[5:].strip()
                        
                        if event_type and data:
                            self._handle_event(event_type, data)
        except Exception as e:
            if self.running:
                logger.error(f"Erro ao processar eventos SSE: {e}")
    
    def _handle_event(self, event_type, data):
        """Manipula evento SSE."""
        logger.info(f"Evento: {event_type}")
        
        try:
            if event_type == 'connected':
                # Extrair session_id
                data_obj = json.loads(data)
                self.session_id = data_obj.get('sessionId')
                logger.info(f"Conectado ao servidor. SessionID: {self.session_id}")
            
            elif event_type == 'message':
                data_obj = json.loads(data)
                logger.info(f"Mensagem recebida: {json.dumps(data_obj, indent=2)}")
                
                # Processar resultado
                if "result" in data_obj:
                    if "tools" in data_obj["result"]:
                        print("\nFerramentas disponíveis:")
                        for tool in data_obj["result"]["tools"]:
                            print(f"  - {tool['name']}: {tool['description']}")
                        print()
                    elif "content" in data_obj["result"]:
                        for content in data_obj["result"]["content"]:
                            if content["type"] == "text":
                                try:
                                    # Tentar analisar como JSON
                                    result_data = json.loads(content["text"])
                                    print("\nResultado:")
                                    print(json.dumps(
                                        result_data, 
                                        indent=2, 
                                        ensure_ascii=False
                                    ))
                                except Exception:
                                    # Se não for JSON, mostrar como texto
                                    print(f"\nResultado: {content['text']}")
                
                # Processar erro
                if "error" in data_obj:
                    print(f"\nErro: {data_obj['error']['message']}")
                    
        except Exception as e:
            logger.error(f"Erro ao manipular evento: {e}")
    
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
        
        # IMPORTANTE: Usar o header X-MCP-Session-ID em vez de parâmetro de consulta
        headers = self.headers.copy()
        headers['Content-Type'] = 'application/json'
        headers['X-MCP-Session-ID'] = self.session_id
        
        try:
            logger.info(f"Enviando mensagem: {json.dumps(message)}")
            response = requests.post(
                message_endpoint, 
                json=message, 
                headers=headers
            )
            
            if response.status_code != 202:
                logger.error(
                    f"Erro ao enviar mensagem: {response.status_code} - "
                    f"{response.text}"
                )
                return False
            
            logger.info("Mensagem enviada com sucesso (202 Accepted)")
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
        
        if self.sse_response:
            self.sse_response.close()
        
        if self.event_thread and self.event_thread.is_alive():
            self.event_thread.join(timeout=1.0)
            
        logger.info("Conexão encerrada")


def main():
    if len(sys.argv) < 2:
        print(f"Uso: {sys.argv[0]} <server_url> [auth_token]")
        sys.exit(1)
    
    server_url = sys.argv[1]
    auth_token = sys.argv[2] if len(sys.argv) > 2 else "mcp-serper-token"
    
    client = MCPClient(server_url, auth_token)
    
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