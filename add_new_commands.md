# Guia para Adicionar Novos Comandos ao Servidor MCP Python

Este documento fornece um guia passo a passo para adicionar novos comandos ao servidor MCP Python, com exemplos específicos que abrangem desde a implementação até os testes.

## Índice

1. [Estrutura Básica](#estrutura-básica)
2. [Passo a Passo para Adicionar um Novo Comando](#passo-a-passo-para-adicionar-um-novo-comando)
3. [Exemplo: Adicionando Busca de Imagens](#exemplo-adicionando-busca-de-imagens)
4. [Exemplo: Integrando Sequential Thinking](#exemplo-integrando-sequential-thinking)
5. [Boas Práticas](#boas-práticas)
6. [Referências](#referências)

## Estrutura Básica

O servidor MCP Python segue uma estrutura organizada que separa as responsabilidades:

```
mcp_serper_server.py    # Arquivo principal do servidor
test_*.py               # Scripts de teste para endpoints específicos
setup_and_run.sh        # Script de inicialização
README_PYTHON.md        # Documentação
```

## Passo a Passo para Adicionar um Novo Comando

### 1. Implementar o Método no Cliente

Adicione um novo método na classe `SerperClient` para interagir com o endpoint desejado da API:

```python
def novo_endpoint(self, params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Descrição do método.
    
    Args:
        params: Parâmetros para o endpoint
        
    Returns:
        Resposta do endpoint
    """
    try:
        # Preparar payload
        payload = {
            "param_chave": params["param_chave"]
            # Adicione outros parâmetros conforme necessário
        }
        
        # Faz a requisição para o endpoint
        response = self._make_request("POST", "/caminho_do_endpoint", payload)
        return {"resultadoFormatado": response}
    except Exception as e:
        logger.error(f"Error in novo_endpoint: {e}")
        raise Exception(f"Failed to use novo_endpoint: {e}")
```

### 2. Adicionar Método na Classe de Ferramentas

Implemente o método correspondente na classe `SerperSearchTools` para expor a funcionalidade:

```python
def novo_comando(self, params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Executa o novo comando.
    
    Args:
        params: Parâmetros do comando
        
    Returns:
        Resultados do comando
    """
    try:
        return self.serper_client.novo_endpoint(params)
    except Exception as e:
        raise Exception(f"SearchTool: failed to execute novo_comando. {e}")
```

### 3. Definir o Schema do Comando

Adicione a definição do comando na lista `tool_definitions` para expor seus parâmetros:

```python
"novo_comando": {
    "description": "Descrição do que esse comando faz e como pode ser utilizado.",
    "parameters": {
        "param_chave": {
            "type": "string",
            "description": "Descrição detalhada deste parâmetro"
        },
        "param_opcional": {
            "type": "number",
            "description": "Descrição de um parâmetro opcional"
        }
    },
    "required": ["param_chave"]
}
```

### 4. Atualizar o Handler de Mensagens

Adicione o tratamento deste comando no método `handle_message`:

```python
elif tool_name == "novo_comando":
    result = search_tools.novo_comando(arguments)
    return {
        "id": message_id,
        "result": {
            "content": [
                {"type": "text", "text": json.dumps(result, ensure_ascii=False)}
            ]
        }
    }
```

### 5. Criar Script de Teste

Crie um arquivo de teste para validar o novo comando:

```python
#!/usr/bin/env python3

import http.client
import json

def test_novo_comando():
    conn = http.client.HTTPSConnection('endpoint_da_api')
    payload = json.dumps({
        "param_chave": "valor_teste",
        "param_opcional": 10
    })
    headers = {
        'X-API-KEY': 'sua_chave_api',
        'Content-Type': 'application/json'
    }
    
    print("Enviando requisição para o endpoint...")
    conn.request('POST', '/caminho_do_endpoint', payload, headers)
    
    print("Recebendo resposta...")
    res = conn.getresponse()
    
    print(f"Status: {res.status} {res.reason}")
    data = res.read()
    
    print("Resposta:")
    result = json.loads(data.decode('utf-8'))
    print(json.dumps(result, indent=2, ensure_ascii=False))
    
    return result

if __name__ == "__main__":
    test_novo_comando()
```

## Exemplo: Adicionando Busca de Imagens

Vamos demonstrar a adição do comando de busca de imagens (`image_search`):

### 1. Implementar o Método no Cliente

```python
def image_search(self, params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Realiza uma busca de imagens.
    
    Args:
        params: Parâmetros para a busca de imagens
        
    Returns:
        Resultados da busca de imagens
    """
    try:
        # Prepara o payload com os parâmetros necessários
        payload = {
            "q": params["q"]
        }
        
        # Adiciona parâmetros opcionais
        if "location" in params:
            payload["location"] = params["location"]
        if "gl" in params:
            payload["gl"] = params["gl"]
        if "hl" in params:
            payload["hl"] = params["hl"]
        if "num" in params:
            payload["num"] = params["num"]
            
        response = self._make_request("POST", "/images", payload)
        return {"imageResults": response}
    except Exception as e:
        logger.error(f"Error in image_search: {e}")
        raise Exception(f"Failed to search for images with query '{params.get('q')}': {e}")
```

### 2. Adicionar Método na Classe de Ferramentas

```python
def image_search(self, params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Executa uma busca por imagens.
    
    Args:
        params: Parâmetros da busca
        
    Returns:
        Resultados da busca de imagens
    """
    try:
        return self.serper_client.image_search(params)
    except Exception as e:
        raise Exception(f"SearchTool: failed to search images for '{params.get('q')}'. {e}")
```

### 3. Definir o Schema do Comando

```python
"image_search": {
    "description": "Tool to search for images via Serper API and retrieve results including thumbnails and source information.",
    "parameters": {
        "q": {
            "type": "string",
            "description": "Search query string for image search (e.g., 'sunset over mountains', 'cats playing')"
        },
        "gl": {
            "type": "string",
            "description": "Optional region code for image results in ISO 3166-1 alpha-2 format (e.g., 'us', 'gb', 'de')"
        },
        "hl": {
            "type": "string",
            "description": "Optional language code for image results in ISO 639-1 format (e.g., 'en', 'es', 'fr')"
        },
        "num": {
            "type": "number",
            "description": "Number of image results to return (default: 10)"
        },
        "location": {
            "type": "string",
            "description": "Optional location for image results (e.g., 'New York, United States', 'Paris, France')"
        }
    },
    "required": ["q"]
}
```

### 4. Atualizar o Handler de Mensagens

```python
elif tool_name == "image_search":
    result = search_tools.image_search(arguments)
    return {
        "id": message_id,
        "result": {
            "content": [
                {"type": "text", "text": json.dumps(result, ensure_ascii=False)}
            ]
        }
    }
```

### 5. Script de Teste para Busca de Imagens

```python
#!/usr/bin/env python3

import http.client
import json

def test_image_search():
    conn = http.client.HTTPSConnection('google.serper.dev')
    payload = json.dumps({
        "q": "apple inc",
        "location": "Brazil",
        "gl": "br",
        "hl": "pt-br"
    })
    headers = {
        'X-API-KEY': 'sua_chave_api',
        'Content-Type': 'application/json'
    }
    
    print("Enviando requisição para o endpoint de busca de imagens...")
    conn.request('POST', '/images', payload, headers)
    
    print("Recebendo resposta...")
    res = conn.getresponse()
    
    print(f"Status: {res.status} {res.reason}")
    data = res.read()
    
    print("Resposta:")
    result = json.loads(data.decode('utf-8'))
    print(json.dumps(result, indent=2, ensure_ascii=False))
    
    return result

if __name__ == "__main__":
    test_image_search()
```

## Exemplo: Integrando Sequential Thinking

O Sequential Thinking é uma ferramenta que facilita o processo de pensamento estruturado para resolução de problemas. Vamos ver como integrar essa funcionalidade:

### 1. Implementar o Método no Cliente

```python
def sequential_thinking(self, params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Processa um passo de pensamento sequencial.
    
    Args:
        params: Parâmetros para o processamento de pensamento
        
    Returns:
        Resposta do processamento
    """
    try:
        # O payload deve conter os parâmetros necessários para o Sequential Thinking
        payload = {
            "thought": params.get("thought", ""),
            "nextThoughtNeeded": params.get("nextThoughtNeeded", False),
            "thoughtNumber": params.get("thoughtNumber", 1),
            "totalThoughts": params.get("totalThoughts", 1)
        }
        
        # Adicionar parâmetros opcionais
        if "isRevision" in params:
            payload["isRevision"] = params["isRevision"]
        if "revisesThought" in params:
            payload["revisesThought"] = params["revisesThought"]
        if "branchFromThought" in params:
            payload["branchFromThought"] = params["branchFromThought"]
        if "branchId" in params:
            payload["branchId"] = params["branchId"]
        if "needsMoreThoughts" in params:
            payload["needsMoreThoughts"] = params["needsMoreThoughts"]
            
        # Usar uma API externa para o Sequential Thinking, por exemplo:
        # Neste caso, você precisaria configurar a URL apropriada para o serviço
        conn = http.client.HTTPSConnection("servidor-sequential-thinking.com")
        headers = {
            "Content-Type": "application/json"
        }
        
        conn.request("POST", "/api/thinking", json.dumps(payload), headers)
        response = conn.getresponse()
        data = response.read().decode("utf-8")
        
        if response.status != 200:
            raise Exception(f"Sequential Thinking API error: {response.status} {data}")
            
        return json.loads(data)
    except Exception as e:
        logger.error(f"Error in sequential_thinking: {e}")
        raise Exception(f"Failed to process sequential thinking: {e}")
```

### 2. Adicionar Método na Classe de Ferramentas

```python
def sequential_thinking(self, params: Dict[str, Any]) -> Dict[str, Any]:
    """
    Processa um pensamento sequencial estruturado.
    
    Args:
        params: Parâmetros do processamento
        
    Returns:
        Resultados do processamento
    """
    try:
        return self.serper_client.sequential_thinking(params)
    except Exception as e:
        raise Exception(f"SearchTool: failed to process sequential thinking. {e}")
```

### 3. Definir o Schema do Comando

```python
"sequential_thinking": {
    "description": "Facilita um processo de pensamento detalhado e passo a passo para resolução de problemas e análises.",
    "parameters": {
        "thought": {
            "type": "string",
            "description": "O pensamento atual"
        },
        "nextThoughtNeeded": {
            "type": "boolean",
            "description": "Se é necessário outro passo de pensamento"
        },
        "thoughtNumber": {
            "type": "integer",
            "description": "Número do pensamento atual"
        },
        "totalThoughts": {
            "type": "integer",
            "description": "Número total estimado de pensamentos necessários"
        },
        "isRevision": {
            "type": "boolean",
            "description": "Se este é uma revisão de pensamento anterior"
        },
        "revisesThought": {
            "type": "integer",
            "description": "Qual pensamento está sendo reconsiderado"
        },
        "branchFromThought": {
            "type": "integer",
            "description": "Número do pensamento de ramificação"
        },
        "branchId": {
            "type": "string",
            "description": "Identificador de ramificação"
        },
        "needsMoreThoughts": {
            "type": "boolean",
            "description": "Se mais pensamentos são necessários"
        }
    },
    "required": ["thought", "nextThoughtNeeded", "thoughtNumber", "totalThoughts"]
}
```

### 4. Atualizar o Handler de Mensagens

```python
elif tool_name == "sequential_thinking":
    result = search_tools.sequential_thinking(arguments)
    return {
        "id": message_id,
        "result": {
            "content": [
                {"type": "text", "text": json.dumps(result, ensure_ascii=False)}
            ]
        }
    }
```

### 5. Script de Teste para Sequential Thinking

```python
#!/usr/bin/env python3

import http.client
import json

def test_sequential_thinking():
    # Como o Sequential Thinking geralmente é um serviço externo,
    # precisamos configurar a conexão para o servidor correto
    conn = http.client.HTTPSConnection("servidor-sequential-thinking.com")
    
    payload = json.dumps({
        "thought": "Estou analisando o problema de otimização de rotas de entrega.",
        "nextThoughtNeeded": True,
        "thoughtNumber": 1,
        "totalThoughts": 5
    })
    
    headers = {
        'Content-Type': 'application/json'
    }
    
    print("Enviando requisição para o endpoint de Sequential Thinking...")
    conn.request('POST', '/api/thinking', payload, headers)
    
    print("Recebendo resposta...")
    res = conn.getresponse()
    
    print(f"Status: {res.status} {res.reason}")
    data = res.read()
    
    print("Resposta:")
    result = json.loads(data.decode('utf-8'))
    print(json.dumps(result, indent=2, ensure_ascii=False))
    
    return result

if __name__ == "__main__":
    test_sequential_thinking()
```

## Boas Práticas

1. **Princípio DRY (Don't Repeat Yourself)**: Reutilize código quando possível e evite duplicação.
2. **KISS (Keep It Simple, Stupid)**: Mantenha a implementação simples e direta.
3. **YAGNI (You Ain't Gonna Need It)**: Implemente apenas o que é necessário, sem adicionar complexidade desnecessária.
4. **Tratamento de Erros**: Sempre implemente tratamento adequado de erros com mensagens claras.
5. **Documentação**: Documente adequadamente os métodos, parâmetros e retornos.
6. **Testes**: Crie scripts de teste para cada novo comando.

## Referências

- [Documentação da API Serper](https://serper.dev/docs)
- [Modelo MCP (Model Context Protocol)](https://github.com/anthropics/anthropic-model-context-protocol)
- [Sequential Thinking MCP Server](https://smithery.ai/server/@smithery-ai/server-sequential-thinking)
- [Web Research MCP Server](https://smithery.ai/server/@mzxrai/mcp-webresearch) 