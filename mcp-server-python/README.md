# MCP Server Serper

Servidor MCP (Model Context Protocol) em Python para buscas na web via API Serper.

## Sobre

Este projeto implementa um servidor seguindo o protocolo MCP (Model Context Protocol) com suporte para:

- Transporte Server-Sent Events (SSE)
- Busca na web via API Serper
- Extração de conteúdo de páginas web
- Verificação de saúde do serviço

## Pré-requisitos

- Python 3.8 ou superior
- Conta na API Serper (https://serper.dev)

## Instalação

1. Clone o repositório:
```bash
git clone https://github.com/seu-usuario/mcp-server-serper.git
cd mcp-server-serper
```

2. Instale o projeto:
```bash
pip install -e .
```

## Configuração

Crie um arquivo `.env` na raiz do projeto com as seguintes variáveis:

```
SERPER_API_KEY=sua_chave_api_serper
MCP_TOKEN=seu_token_autenticacao  # opcional
HOST=127.0.0.1  # opcional, padrão: 127.0.0.1
PORT=3001  # opcional, padrão: 3001
```

## Uso

### Iniciar o servidor

```bash
mcp-server-serper
```

Ou diretamente via Python:

```bash
python -m mcp_server_serper.main
```

### Conectar-se ao servidor

O servidor expõe os seguintes endpoints:

- `GET /`: Página inicial com informações básicas
- `GET /sse`: Endpoint SSE para conexão com clientes MCP
- `POST /messages`: Endpoint para receber mensagens dos clientes

### Ferramentas disponíveis

- `google_search`: Realiza buscas na web via API Serper
- `scrape`: Extrai conteúdo de páginas web
- `_health`: Verifica a saúde do serviço

## Desenvolvimento

1. Instale as dependências de desenvolvimento:
```bash
pip install -e ".[dev]"
```

2. Execute os testes:
```bash
pytest
```

3. Verifique a qualidade do código:
```bash
black .
isort .
mypy src
flake8
```

## Licença

Este projeto está licenciado sob a licença MIT - veja o arquivo LICENSE para detalhes. 