#!/usr/bin/env python3

"""
Script para depurar a conexão SSE com o servidor MCP Python.
Foca apenas na conexão SSE para entender o problema.
"""

import requests
import time
import json

# Configurações
SERVER_URL = "http://localhost:3001"
AUTH_TOKEN = "mcp-serper-token"

# Configura os cabeçalhos para SSE
headers = {
    "Accept": "text/event-stream",
    "Cache-Control": "no-cache",
    "Authorization": f"Bearer {AUTH_TOKEN}"
}

# Função de depuração para monitorar bytes
def print_bytes(data):
    if isinstance(data, bytes):
        print(f"Bytes: {data}")
        try:
            decoded = data.decode('utf-8')
            print(f"Decodificado: {decoded}")
        except Exception as e:
            print(f"Erro ao decodificar: {e}")
    else:
        print(f"Recebido (não bytes): {data}")

print("=== Depuração de Conexão SSE ===")
print(f"Conectando ao endpoint SSE: {SERVER_URL}/sse")
print(f"Usando cabeçalhos: {headers}")

try:
    # Estabelece conexão SSE
    print("\nIniciando conexão SSE...")
    response = requests.get(f"{SERVER_URL}/sse", headers=headers, stream=True)
    
    # Verifica o código de status
    print(f"Status da conexão: {response.status_code}")
    print(f"Cabeçalhos da resposta: {dict(response.headers)}")
    
    if response.status_code != 200:
        print(f"Erro na conexão: {response.text}")
        exit(1)
    
    # Processa os eventos SSE
    print("\nMonitorando eventos SSE...")
    print("Pressione Ctrl+C para interromper")
    
    # Define um timeout para não bloquear indefinidamente
    timeout = time.time() + 30  # 30 segundos
    line_count = 0
    
    for line in response.iter_lines():
        line_count += 1
        
        if line:
            try:
                decoded = line.decode('utf-8')
                print(f"[{line_count}] Linha recebida: {decoded}")
                
                # Processa eventos SSE
                if decoded.startswith('event:'):
                    event_type = decoded[6:].strip()
                    print(f"Evento: {event_type}")
                elif decoded.startswith('data:'):
                    data = decoded[5:].strip()
                    print(f"Dados: {data}")
                    
                    # Tenta decodificar JSON
                    try:
                        json_data = json.loads(data)
                        print(f"JSON decodificado: {json_data}")
                        
                        # Verifica se tem session_id
                        if 'sessionId' in json_data:
                            print(f"Session ID encontrado: {json_data['sessionId']}")
                    except json.JSONDecodeError:
                        print("Dados não são JSON válido")
            except UnicodeDecodeError:
                print(f"[{line_count}] Erro ao decodificar linha: {line}")
                print_bytes(line)
        else:
            print(f"[{line_count}] Linha vazia recebida")
        
        # Verifica timeout
        if time.time() > timeout:
            print("\nTimeout atingido (30 segundos)")
            break
    
    print(f"\nTotal de linhas recebidas: {line_count}")
    print("Conexão encerrada")

except KeyboardInterrupt:
    print("\nOperação interrompida pelo usuário")
except Exception as e:
    print(f"\nErro durante a conexão SSE: {e}")
    import traceback
    traceback.print_exc() 