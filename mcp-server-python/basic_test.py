#!/usr/bin/env python3

"""
Script básico para testar o servidor MCP sem dependências específicas.
"""

import json
import requests
import sys
import threading
import time

# Configurações
SERVER_URL = "http://localhost:3001"
AUTH_TOKEN = "mcp-serper-token"
HEADERS = {"Authorization": f"Bearer {AUTH_TOKEN}"}
SESSION_ID = None  # Será preenchido após a conexão SSE

# Função para monitorar o SSE e extrair o session_id
def sse_monitor():
    global SESSION_ID
    
    try:
        print("Iniciando conexão SSE...")
        response = requests.get(
            f"{SERVER_URL}/sse",
            headers={"Accept": "text/event-stream", **HEADERS},
            stream=True
        )
        
        for line in response.iter_lines():
            if line:
                decoded = line.decode('utf-8')
                print(f"SSE: {decoded}")
                
                # Procurando pelo evento "connected" que contém o session_id
                if decoded.startswith('data:'):
                    data = json.loads(decoded[5:].strip())
                    if 'sessionId' in data:
                        SESSION_ID = data['sessionId']
                        print(f"Session ID obtido: {SESSION_ID}")
                        break
        
        print("Conexão SSE encerrada")
    except Exception as e:
        print(f"Erro na conexão SSE: {e}")

# Função para testar o servidor
def test_server():
    print("=== Testando Servidor MCP Python ===")
    
    try:
        # 1. Verificando status do servidor
        print("\n1. Verificando status do servidor...")
        response = requests.get(SERVER_URL, headers=HEADERS)
        print(f"Status: {response.status_code}")
        print(f"Resposta: {response.text}")
        
        if response.status_code != 200:
            print("Erro ao conectar ao servidor!")
            return
        
        # 2. Conectando ao SSE e obtendo session_id
        print("\n2. Conectando ao endpoint SSE...")
        sse_thread = threading.Thread(target=sse_monitor)
        sse_thread.daemon = True
        sse_thread.start()
        
        # Aguarda até obter um session_id válido (máximo 10 segundos)
        timeout = time.time() + 10
        while not SESSION_ID and time.time() < timeout:
            time.sleep(0.5)
            
        if not SESSION_ID:
            print("Não foi possível obter um session_id válido!")
            return
            
        print(f"Usando session_id: {SESSION_ID}")
        
        # 3. Testando ferramenta _health
        print("\n3. Testando ferramenta _health...")
        health_payload = {
            "type": "toolInvocation",
            "query": "_health",
            "parameters": {}
        }
        
        headers = HEADERS.copy()
        headers["Content-Type"] = "application/json"
        headers["X-MCP-Session-ID"] = SESSION_ID
        
        response = requests.post(
            f"{SERVER_URL}/messages", 
            headers=headers,
            json=health_payload
        )
        
        print(f"Status: {response.status_code}")
        print(f"Resposta: {response.text}")
        
        # 4. Testando ferramenta google_search
        if len(sys.argv) > 1 and sys.argv[1] == "search":
            print("\n4. Testando ferramenta google_search...")
            search_payload = {
                "type": "toolInvocation",
                "query": "Python Model Context Protocol",
                "parameters": {
                    "gl": "br",
                    "hl": "pt"
                }
            }
            
            response = requests.post(
                f"{SERVER_URL}/messages", 
                headers=headers,
                json=search_payload
            )
            
            print(f"Status: {response.status_code}")
            if response.status_code == 200:
                print("Resposta recebida com sucesso!")
                # Limitando a saída para não ficar muito grande
                print(f"Primeiros 200 caracteres: {response.text[:200]}...")
            else:
                print(f"Resposta: {response.text}")
        
    except Exception as e:
        print(f"Erro durante o teste: {e}")

if __name__ == "__main__":
    test_server() 