# Servidor MCP Serper

Um servidor MCP (Model Context Protocol) que fornece recursos de busca na web e raspagem de páginas através da API Serper.

## Funcionalidades

Este servidor MCP oferece as seguintes ferramentas:

- **google_search**: Realiza buscas na web através da API Serper, fornecendo resultados completos, incluindo resultados orgânicos, "pessoas também perguntam", buscas relacionadas e gráfico de conhecimento.
- **scrape**: Extrai o conteúdo de uma página web, incluindo texto e opcionalmente conteúdo em markdown. Também recupera metadados JSON-LD e metadados do cabeçalho.
- **_health**: Um endpoint para verificar a saúde do servidor e a conectividade com a API Serper.

## Requisitos

- Node.js v18 ou superior
- Uma chave de API Serper (disponível em [serper.dev](https://serper.dev))

## Instalação

### Como pacote npm

```bash
npm install serper-search-scrape-mcp-server
```

### A partir do repositório

```bash
git clone https://github.com/diegofornalha/mcp-server-serper.git
cd mcp-server-serper
npm install
```

## Configuração

Antes de executar o servidor, você precisa configurar a chave de API Serper. Há algumas maneiras de fazer isso:

### 1. Variável de ambiente

```bash
export SERPER_API_KEY="sua_chave_api_aqui"
```

### 2. Arquivo .env

Crie um arquivo `.env` na raiz do projeto:

```
SERPER_API_KEY=sua_chave_api_aqui
```

## Uso

### Linha de comando

```bash
# Se instalado como pacote npm
npx serper-mcp

# Se clonado do repositório
npm start
```

### Com Claude Desktop

Para usar este servidor MCP com o Claude Desktop:

1. Edite o arquivo de configuração do Claude Desktop:
   - **macOS**: `~/Library/Application Support/Claude/claude_desktop_config.json` 
   - **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

2. Adicione a configuração do servidor:

```json
{
  "serper-search": {
    "command": "npx",
    "args": ["serper-mcp"],
    "env": {
      "SERPER_API_KEY": "sua_chave_api_aqui"
    }
  }
}
```

3. Reinicie o Claude Desktop

## Teste com o MCP Inspector

Você pode testar o servidor MCP usando o MCP Inspector:

```bash
npm run inspector
```

Isso iniciará o MCP Inspector na URL http://localhost:5173, onde você poderá testar as ferramentas do servidor.

## Exemplos de uso

### Busca no Google

```json
{
  "q": "inteligência artificial",
  "gl": "br",
  "hl": "pt-br"
}
```

### Raspagem de página web

```json
{
  "url": "https://www.exemplo.com.br",
  "includeMarkdown": true
}
```

## Desenvolvimento

### Compilação

```bash
npm run build
```

### Execução em modo de desenvolvimento

```bash
npm run watch
```

## Licença

Este projeto está licenciado sob a licença MIT - veja o arquivo LICENSE para detalhes.

## Contribuição

Contribuições são bem-vindas! Por favor, sinta-se à vontade para enviar um Pull Request.

## Suporte

Para relatar problemas ou solicitar recursos, abra uma issue no repositório do GitHub. 