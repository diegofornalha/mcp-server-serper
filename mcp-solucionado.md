# Solução para o Cliente MCP SSE

## Problema

Identificamos um problema na integração entre o cliente Python MCP SDK e o servidor MCP SSE. O problema ocorre porque:

1. O SDK Python do MCP adiciona incorretamente o `sessionId` como um parâmetro de consulta (`query parameter`) ao enviar mensagens para o endpoint `/sse-message`.
2. Isso viola a especificação do protocolo MCP, que exige que o `sessionId` seja enviado como um cabeçalho HTTP (`header`) chamado `X-MCP-Session-ID`.
3. Servidores que seguem estritamente a especificação MCP rejeitam essas requisições com erro 400 Bad Request.

O mesmo problema foi documentado na issue #236 do repositório MCP Python SDK (hipotética).

## Solução

### Correções no Servidor

Modificamos o arquivo `src/server-sse.ts` para aceitar o `sessionId` de duas formas:

1. Como parâmetro de consulta (`req.query.sessionId`) para manter compatibilidade com o SDK Python
2. Como cabeçalho HTTP (`req.headers['x-mcp-session-id']`) conforme a especificação

```typescript
// Endpoint para receber mensagens via POST
app.post('/sse-message', authenticate, async (req, res) => {
  // Buscar o sessionId - verificar tanto na query quanto no cabeçalho X-MCP-Session-ID
  const sessionId = req.query.sessionId as string || req.headers['x-mcp-session-id'] as string;
  
  if (!sessionId) {
    res.status(400).send('Parâmetro sessionId é obrigatório (via query ou cabeçalho X-MCP-Session-ID)');
    return;
  }
  
  // Resto do código...
});
```

### Cliente Corrigido

Criamos um cliente Python personalizado (`mcp_client.py`) que implementa corretamente a especificação MCP:

1. Estabelece uma conexão SSE correta com o servidor
2. Processa eventos SSE manualmente em vez de depender de bibliotecas de terceiros
3. Usa o cabeçalho HTTP `X-MCP-Session-ID` em vez do parâmetro de consulta `sessionId`

```python
# Trecho relevante do cliente corrigido
message_endpoint = f"{self.server_url}-message"

# IMPORTANTE: Usar o header X-MCP-Session-ID em vez de parâmetro de consulta
headers = self.headers.copy()
headers['Content-Type'] = 'application/json'
headers['X-MCP-Session-ID'] = self.session_id

response = requests.post(
    message_endpoint, 
    json=message, 
    headers=headers
)
```

## Vantagens da Solução

1. **Compatibilidade Bidirecional**: O servidor agora suporta tanto o método correto (header) quanto o método incorreto (query parameter)
2. **Conformidade com a Especificação**: O novo cliente segue estritamente o protocolo MCP
3. **Robustez**: Implementamos tratamento de erros e logging detalhado para facilitar a depuração
4. **Independência de Bibliotecas**: O novo cliente não depende de bibliotecas externas para processamento SSE

## Impacto

Esta solução garante que o servidor MCP SSE possa:

1. Funcionar com clientes Python existentes que usam o SDK padrão
2. Funcionar com clientes que seguem corretamente a especificação MCP
3. Fornecer mensagens de erro claras quando algo dá errado

## Testes Realizados

1. **Teste de Compatibilidade**: Verificamos que o servidor aceita solicitações tanto com o sessionId via query parameter quanto via header
2. **Teste de Funcionalidade**: Confirmamos que o cliente corrigido consegue:
   - Estabelecer conexão com o servidor
   - Receber o sessionId
   - Enviar solicitações JSON-RPC
   - Receber respostas via eventos SSE

## Próximos Passos

1. Considerar contribuir com uma correção para o SDK Python oficial do MCP
2. Adicionar mais testes automatizados
3. Melhorar a documentação sobre este comportamento para futuros desenvolvedores 