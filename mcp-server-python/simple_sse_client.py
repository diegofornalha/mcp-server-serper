#!/usr/bin/env python3

"""
Cliente simples usando sseclient-py e requests para testar a conexão SSE.
"""

import json
import requests
import sseclient
import time
import threading
import sys

# Configurações
SERVER_URL = "http://localhost:3001"
AUTH_TOKEN = "mcp-serper-token"

# Função principal para testar a conexão SSE
def test_sse_connection():
    print("=== Teste de Conexão SSE ===")
    
    try:
        # Configura os cabeçalhos
        headers = {
            "Accept": "text/event-stream",
            "Cache-Control": "no-cache",
            "Authorization": f"Bearer {AUTH_TOKEN}"
        }
        
        print(f"Conectando ao servidor SSE: {SERVER_URL}/sse")
        print(f"Cabeçalhos: {headers}")
        
        # Estabelece a conexão
        response = requests.get(f"{SERVER_URL}/sse", headers=headers, stream=True)
        
        print(f"Status da conexão: {response.status_code}")
        print(f"Cabeçalhos da resposta: {dict(response.headers)}")
        
        if response.status_code != 200:
            print(f"Erro na conexão: {response.text}")
            return
        
        # Cria um cliente SSE
        client = sseclient.SSEClient(response)
        
        # Configura um timer para encerrar após 30 segundos
        stop_event = threading.Event()
        
        def timeout_handler():
            print("\nTimeout de 30 segundos atingido.")
            stop_event.set()
            
        timer = threading.Timer(30, timeout_handler)
        timer.daemon = True
        timer.start()
        
        # Processa os eventos SSE
        print("\nAgora escutando eventos SSE (timeout: 30s)...\n")
        event_count = 0
        
        for event in client.events():
            if stop_event.is_set():
                break
                
            event_count += 1
            print(f"[Evento {event_count}] Tipo: {event.event}")
            print(f"[Evento {event_count}] Dados: {event.data}")
            
            # Tenta decodificar como JSON
            try:
                json_data = json.loads(event.data)
                print(f"[Evento {event_count}] JSON: {json.dumps(json_data, indent=2)}")
                
                # Verifica sessionId
                if 'sessionId' in json_data:
                    session_id = json_data['sessionId']
                    print(f"\n>>> Session ID encontrado: {session_id}")
                    
                    # Testa uma chamada com este session_id
                    test_health_call(session_id)
            except json.JSONDecodeError:
                print(f"[Evento {event_count}] Dados não são JSON válido")
                
            print()  # Linha em branco entre eventos
    
    except KeyboardInterrupt:
        print("\nOperação interrompida pelo usuário")
    except Exception as e:
        print(f"Erro durante a conexão SSE: {e}")
        import traceback
        traceback.print_exc()
    finally:
        if 'timer' in locals():
            timer.cancel()
        print("\nTeste encerrado")

# Função para testar chamada _health com session_id
def test_health_call(session_id):
    print(f"\n=== Testando Chamada _health com Session ID: {session_id} ===")
    
    try:
        # Configura os cabeçalhos
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {AUTH_TOKEN}",
            "X-MCP-Session-ID": session_id
        }
        
        # Prepara a requisição
        payload = {
            "type": "toolInvocation",
            "query": "_health",
            "parameters": {}
        }
        
        # Envia a requisição
        response = requests.post(
            f"{SERVER_URL}/messages",
            headers=headers,
            json=payload
        )
        
        print(f"Status da chamada _health: {response.status_code}")
        print(f"Resposta: {response.text}")
    except Exception as e:
        print(f"Erro ao testar _health: {e}")

if __name__ == "__main__":
    test_sse_connection() 