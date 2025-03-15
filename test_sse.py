#!/usr/bin/env python

"""
Teste simples de conexão com o servidor MCP SSE.
"""

import sys
import json
import requests
import time

if len(sys.argv) < 2:
    print(f"Uso: {sys.argv[0]} <server_url> [auth_token]")
    sys.exit(1)

server_url = sys.argv[1]
auth_token = sys.argv[2] if len(sys.argv) > 2 else "mcp-serper-token"

headers = {
    'Accept': 'text/event-stream',
    'Cache-Control': 'no-cache',
}

if auth_token:
    headers['Authorization'] = f'Bearer {auth_token}'

print(f"Conectando ao servidor SSE em {server_url}")
print(f"Headers: {headers}")

try:
    # Estabelecer conexão SSE
    response = requests.get(server_url, headers=headers, stream=True)
    
    if response.status_code != 200:
        print(f"Erro na conexão: {response.status_code} - {response.text}")
        sys.exit(1)
        
    print(f"Conexão estabelecida: {response.status_code}")
    
    # Ler eventos
    buffer = ""
    for chunk in response.iter_content(chunk_size=1):
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
                    print(f"Evento: {event_type}")
                    print(f"Dados: {data}")
                    
                    if event_type == 'connected':
                        # Extrair session_id
                        data_obj = json.loads(data)
                        session_id = data_obj.get('sessionId')
                        print(f"Conectado! Session ID: {session_id}")
                        
                        # Enviar listTools
                        message_endpoint = f"{server_url}-message"
                        message = {
                            "jsonrpc": "2.0",
                            "id": int(time.time() * 1000),
                            "method": "listTools",
                            "params": {}
                        }
                        
                        # Usar APENAS o header X-MCP-Session-ID, sem query parameter
                        message_headers = headers.copy()
                        message_headers['Content-Type'] = 'application/json'
                        message_headers['X-MCP-Session-ID'] = session_id
                        
                        print(f"Enviando listTools para {message_endpoint}")
                        print(f"Message headers: {message_headers}")
                        
                        try:
                            list_response = requests.post(
                                message_endpoint, 
                                json=message, 
                                headers=message_headers
                            )
                            print(f"Resposta: {list_response.status_code} - {list_response.text}")
                            
                            if list_response.status_code == 202:
                                print("Requisição aceita pelo servidor!")
                                
                                # Aguardar a resposta via SSE
                                print("Aguardando resposta do servidor via SSE...")
                        except Exception as e:
                            print(f"Erro ao enviar listTools: {e}")

except KeyboardInterrupt:
    print("\nEncerrando...")
except Exception as e:
    print(f"Erro: {e}") 