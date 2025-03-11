# Serper Search and Scrape MCP Server (Python)

Um servidor MCP baseado em Python que fornece recursos de busca na web e raspagem de páginas usando a API Serper. Este servidor integra-se com o Claude Desktop para permitir recursos poderosos de busca na web e extração de conteúdo.

## Funcionalidades

### Ferramentas

- `google_search` - Realizar buscas na web via API Serper
  - Resultados de busca ricos incluindo resultados orgânicos, gráfico de conhecimento, "pessoas também perguntam" e buscas relacionadas
  - Suporta segmentação regional e de idioma
  - Parâmetros opcionais para localização, paginação, filtros de tempo e autocorreção
  - Suporta operadores de busca avançados:
    - `site`: Limitar resultados a domínios específicos
    - `filetype`: Limitar a tipos específicos de arquivo (ex: 'pdf', 'doc')
    - `inurl`: Buscar páginas com palavras específicas na URL
    - `intitle`: Buscar páginas com palavras específicas no título
    - `related`: Encontrar sites similares
    - `cache`: Ver versão em cache do Google de uma URL específica
    - `before`: Data antes em formato YYYY-MM-DD
    - `after`: Data depois em formato YYYY-MM-DD
    - `exact`: Correspondência exata de frases
    - `exclude`: Termos para excluir dos resultados de busca
    - `or`: Termos alternativos (operador OR)
  
- `scrape` - Extrair conteúdo de páginas web
  - Obter texto simples e conteúdo markdown opcional
  - Inclui JSON-LD e metadados de cabeçalho
  - Preserva a estrutura do documento

- `_health` - Verificar o status de saúde da API

- `analyze_serp` - Analisar os resultados de busca (SERP) para uma consulta

- `research_keywords` - Pesquisar palavras-chave relacionadas a uma palavra-chave semente

- `analyze_competitors` - Analisar concorrentes para um domínio ou palavra-chave

- `autocomplete` - Obter sugestões de autocompletar para múltiplas consultas
  - Permite enviar várias consultas em uma única requisição
  - Suporta parâmetros de localização e idioma
  - Retorna sugestões de autocompletar para cada consulta

## Requisitos

- Python >= 3.6
- Chave de API Serper (definida como variável de ambiente `SERPER_API_KEY`)

## Desenvolvimento

Para executar o servidor:

```bash
./mcp_serper_server.py
```

### Variáveis de Ambiente

Crie um arquivo `.env` no diretório raiz:

```
SERPER_API_KEY=sua_chave_api_aqui
```

### Testes

Para testar o endpoint de autocompletar:

```bash
./test_autocomplete.py
```

## Instalação

### Claude Desktop

Adicione a configuração do servidor em:
- MacOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
- Windows: `%APPDATA%/Claude/claude_desktop_config.json`

```json
{
  "mcpServers": {
    "serper-search-python": {
      "command": "python3",
      "args": ["/caminho/para/mcp_serper_server.py"],
      "env": {
        "SERPER_API_KEY": "sua_chave_api_aqui"
      }
    }
  }
}
```

### Cursor

1. Abra as configurações do Cursor
2. Abra as configurações de "Features"
3. Na seção "MCP Servers", clique em "Add new MCP Server"
4. Escolha um nome e selecione "command" como "Type"
5. No campo "Command", insira o seguinte:

```
env SERPER_API_KEY=sua_chave_api_aqui python3 /caminho/para/mcp_serper_server.py
```

### Docker

Você também pode executar o servidor usando Docker. Primeiro, crie um Dockerfile:

```Dockerfile
FROM python:3.9-slim

WORKDIR /app

COPY mcp_serper_server.py /app/

ENV PYTHONUNBUFFERED=1

CMD ["python", "mcp_serper_server.py"]
```

Então construa e execute o container:

```bash
docker build -t mcp-server-serper-python .
docker run -e SERPER_API_KEY=sua_chave_api_aqui mcp-server-serper-python
```

Alternativamente, se você tem suas variáveis de ambiente em um arquivo `.env`:

```bash
docker run --env-file .env mcp-server-serper-python
```

Nota: Certifique-se de substituir `sua_chave_api_aqui` com sua chave de API Serper real.