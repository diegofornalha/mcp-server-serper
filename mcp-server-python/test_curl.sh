#!/bin/bash

# Verificar status do servidor
echo "Verificando status do servidor em http://localhost:3001..."
curl -s http://localhost:3001 | python -m json.tool

# Conectar via SSE para obter session_id
echo -e "\nConectando via SSE para obter session_id..."
SESSION_RESPONSE=$(curl -N -s http://localhost:3001/sse -H "Accept: text/event-stream" -H "Authorization: Bearer mcp-serper-token" &)
PID=$!

# Aguardar um pouco para receber o session_id
sleep 2

# Testar ferramenta _health
echo -e "\nTestando ferramenta _health..."
curl -s -X POST http://localhost:3001/messages \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer mcp-serper-token" \
  -H "X-MCP-Session-ID: teste-session-id" \
  -d '{
    "type": "toolInvocation",
    "id": "teste-id-1",
    "name": "_health",
    "arguments": {
      "random_string": "test"
    }
  }' | python -m json.tool

# Testar ferramenta google_search
echo -e "\nTestando ferramenta google_search..."
curl -s -X POST http://localhost:3001/messages \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer mcp-serper-token" \
  -H "X-MCP-Session-ID: teste-session-id" \
  -d '{
    "type": "toolInvocation",
    "id": "teste-id-2",
    "name": "google_search",
    "arguments": {
      "q": "Python Model Context Protocol",
      "gl": "br",
      "hl": "pt"
    }
  }' | python -m json.tool

# Encerrar o processo SSE
echo -e "\nEncerrando conexão SSE..."
kill $PID 2>/dev/null

echo -e "\nTeste concluído!" 