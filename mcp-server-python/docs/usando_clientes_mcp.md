# Guia de Uso dos Clientes MCP e Ferramentas

Este documento explica como utilizar os diferentes clientes MCP (Model Context Protocol) disponíveis e as ferramentas que eles oferecem, incluindo o sequentialthinking.

## Índice

1. [O que é o MCP (Model Context Protocol)](#o-que-é-o-mcp-model-context-protocol)
2. [Clientes MCP Disponíveis](#clientes-mcp-disponíveis)
   - [Cliente Python SSE](#cliente-python-sse)
   - [Cliente Python STDIO](#cliente-python-stdio)
3. [Ferramentas MCP](#ferramentas-mcp)
   - [google_search](#google_search)
   - [scrape](#scrape)
   - [_health](#_health)
4. [SequentialThinking](#sequentialthinking)
   - [O que é](#o-que-é-sequentialthinking)
   - [Como utilizar](#como-utilizar-sequentialthinking)
5. [Exemplos Práticos](#exemplos-práticos)

## O que é o MCP (Model Context Protocol)

O Model Context Protocol (MCP) é um protocolo projetado para facilitar a comunicação entre modelos de linguagem (LLMs) e ferramentas externas. Ele permite que os modelos acessem dados em tempo real, realizem ações no mundo real e obtenham informações contextuais para melhorar suas respostas.

Com o MCP, é possível:
- Realizar buscas na web em tempo real
- Extrair conteúdo de páginas web
- Acessar dados dinâmicos
- Executar ferramentas especializadas

## Clientes MCP Disponíveis

### Cliente Python SSE

O cliente SSE (Server-Sent Events) permite comunicação contínua com o servidor MCP, recebendo atualizações em tempo real.

#### Instalação

```bash
# No diretório principal do projeto
cd mcp-server-python
pip install -e .
```

#### Uso Básico

```python
import asyncio
from mcp_server_serper.client_example import MCPClient

async def main():
    # Inicializar o cliente
    client = MCPClient("http://localhost:3001", "mcp-serper-token")
    
    # Conectar ao servidor
    await client.connect()
    
    # Enviar uma consulta
    await client.send_message("Busque sobre inteligência artificial")
    
    # Para manter o cliente rodando e processando eventos
    while True:
        await asyncio.sleep(1)

if __name__ == "__main__":
    asyncio.run(main())
```

#### Linha de Comando

Você também pode usar o cliente de exemplo diretamente:

```bash
cd mcp-server-python/examples
python client_example.py http://localhost:3001 mcp-serper-token
```

### Cliente Python STDIO

O cliente STDIO comunica-se com o servidor usando stdin/stdout, útil quando o servidor MCP é iniciado como um subprocesso.

#### Uso

```bash
cd mcp-stdio
python client.py
```

Este cliente inicia automaticamente o servidor MCP como um subprocess e estabelece uma comunicação bidirecional através dos streams de entrada/saída padrão.

## Ferramentas MCP

As ferramentas a seguir estão disponíveis no servidor MCP:

### google_search

Realiza buscas na web via API Serper.

**Parâmetros:**
- `q` (obrigatório): Consulta de busca
- `gl` (obrigatório): Código de região (ex: 'us', 'br')
- `hl` (obrigatório): Código de idioma (ex: 'en', 'pt')
- `num` (opcional): Número de resultados
- Outros parâmetros opcionais: `page`, `tbs`, `site`, `filetype`

**Exemplo:**
```
> google_search br pt inteligência artificial
```

### scrape

Extrai conteúdo de uma página web.

**Parâmetros:**
- `url` (obrigatório): URL da página a ser extraída
- `includeMarkdown` (opcional): Se deve incluir formato Markdown

**Exemplo:**
```
> scrape https://modelcontextprotocol.io
```

### _health

Verifica o estado de saúde do servidor MCP.

**Parâmetros:**
- `random_string`: Parâmetro fictício (não é usado)

**Exemplo:**
```
> _health
```

## SequentialThinking

### O que é SequentialThinking

SequentialThinking é uma ferramenta MCP avançada que permite ao modelo de linguagem realizar um "pensamento em etapas", dividindo problemas complexos em passos menores e mais gerenciáveis.

É especialmente útil para:
- Problemas que exigem raciocínio estruturado
- Análise que pode precisar de revisão ou correção de rumo
- Situações onde a informação completa não está disponível inicialmente
- Problemas que requerem solução em múltiplas etapas

### Como Utilizar SequentialThinking

A ferramenta `mcp__sequentialthinking` possui os seguintes parâmetros:

- `thought`: O passo atual de pensamento
- `nextThoughtNeeded`: Se será necessário outro passo (true/false)
- `thoughtNumber`: Número atual na sequência
- `totalThoughts`: Estimativa de quantidade total de passos
- `isRevision`: Se este pensamento revisa um anterior
- `revisesThought`: Qual pensamento está sendo reconsiderado
- `branchFromThought`: Ponto de ramificação
- `branchId`: Identificador da ramificação
- `needsMoreThoughts`: Se mais pensamentos são necessários


### Exemplo 1: Busca na Web com Cliente SSE

```python
import asyncio
from mcp_server_serper.client_example import MCPClient

async def main():
    client = MCPClient("http://localhost:3001", "mcp-serper-token")
    await client.connect()
    
    # Busca na web
    await client.send_message("Busque as últimas notícias sobre IA")
    
    # Aguarda receber a resposta
    await asyncio.sleep(5)

if __name__ == "__main__":
    asyncio.run(main())
```

### Exemplo 3: Extração de Conteúdo Web

```
> scrape https://www.gov.br/pt-br/servicos/obter-a-carteira-de-identidade
```

Esta consulta extrairá o conteúdo da página web sobre como obter a carteira de identidade no Brasil.

---
