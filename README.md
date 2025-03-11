# MCP Serper - Serviços de Busca Unificados

Este projeto implementa um servidor MCP (Model Control Protocol) para realizar buscas na web através da API Serper, bem como aplicativos e scripts unificados para testar as funcionalidades de busca.

## Funcionalidades

- Servidor MCP que disponibiliza ferramentas de busca via API Serper
- Aplicativo web unificado para visualizar resultados de diferentes tipos de busca:
  - Web (busca orgânica)
  - Imagens
  - Vídeos
  - Notícias
  - Lugares (Places)
  - Mapas
  - Reviews (Avaliações)
  - Shopping
  - Image Search (Lens)
  - Scholar (Acadêmico)
  - Patents (Patentes)
  - Webpage (Análise de páginas web)
- Script de teste unificado via linha de comando para testar as funcionalidades de busca
- Interface unificada e reutilizável para diferentes tipos de busca

## Requisitos

- Python 3.6 ou superior
- Chave de API Serper (obtenha em [google.serper.dev](https://google.serper.dev))
- Pacotes Python listados em `requirements.txt`

## Instalação

1. Clone o repositório:
```bash
git clone https://github.com/seu-usuario/mcp-server-serper.git
cd mcp-server-serper
```

2. Crie e ative um ambiente virtual (opcional, mas recomendado):
```bash
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# ou
.venv\Scripts\activate     # Windows
```

3. Instale as dependências:
```bash
pip install -r requirements.txt
```

4. Configure sua chave da API Serper:
```bash
# Linux/macOS
export SERPER_API_KEY=sua_chave_da_api_aqui

# Windows (Prompt de Comando)
set SERPER_API_KEY=sua_chave_da_api_aqui

# Windows (PowerShell)
$env:SERPER_API_KEY="sua_chave_da_api_aqui"
```

Alternativamente, crie um arquivo `.env` na raiz do projeto com o seguinte conteúdo:
```
SERPER_API_KEY=sua_chave_da_api_aqui
```

## Uso

### Servidor MCP

Para iniciar o servidor MCP:

```bash
python mcp_serper_server.py
```

O servidor MCP fornece as seguintes ferramentas:
- `mcp__google_search`: Busca web
- `mcp__serper_image_search`: Busca de imagens
- `mcp__serper_video_search`: Busca de vídeos
- `mcp__serper_news_search`: Busca de notícias 
- `mcp__serper_places_search`: Busca de lugares
- `mcp__serper_maps_search`: Busca de mapas
- `mcp__serper_reviews_search`: Busca de avaliações
- `mcp__serper_shopping_search`: Busca de produtos
- `mcp__serper_lens_search`: Busca por imagem (Google Lens)
- `mcp__serper_scholar_search`: Busca acadêmica (Google Scholar)
- `mcp__serper_patents_search`: Busca de patentes
- `mcp__serper_webpage_search`: Análise de páginas web
- `mcp__serper_autocomplete`: Autocompletar consultas

### Aplicativo Web Unificado

O aplicativo web unificado permite visualizar os resultados de diferentes tipos de busca em uma interface amigável:

```bash
# Tornar o script executável
chmod +x serper_search_app.py

# Executar o aplicativo
./serper_search_app.py
```

Isso iniciará um servidor web local na porta 8000 e abrirá automaticamente o navegador. Você pode alternar entre os diferentes tipos de busca usando as abas na parte superior da interface.

### Scripts de Teste

O script de teste unificado permite testar diferentes tipos de busca na API Serper diretamente pela linha de comando:

```bash
# Tornar o script executável
chmod +x test_serper_search.py

# Exemplos de uso:
# Busca web (padrão)
./test_serper_search.py

# Busca de imagens
./test_serper_search.py --type images

# Busca de vídeos
./test_serper_search.py --type videos --query "música brasileira"

# Busca de notícias
./test_serper_search.py -t news -q "inteligência artificial" -n 5

# Busca de mapas
./test_serper_search.py -t maps -q "restaurantes em São Paulo"

# Busca de avaliações
./test_serper_search.py -t reviews -q "melhores smartphones 2024"

# Busca de produtos (shopping)
./test_serper_search.py -t shopping -q "tênis de corrida"

# Busca acadêmica (scholar)
./test_serper_search.py -t scholar -q "machine learning research"

# Busca de patentes
./test_serper_search.py -t patents -q "blockchain patents"

# Exibir ajuda
./test_serper_search.py --help
```

## Arquitetura

O projeto foi reestruturado seguindo os princípios DRY (Don't Repeat Yourself), KISS (Keep It Simple, Stupid) e YAGNI (You Aren't Gonna Need It), com foco na reutilização de código e redução de duplicação.

### Componentes Principais

1. **SerperClient**: Classe base para interagir com a API Serper, encapsulando a lógica de comunicação HTTP.

2. **SerperSearchTools**: Implementa as ferramentas de busca para o servidor MCP, com métodos específicos para cada tipo de busca.

3. **Aplicativo Web Unificado**: Interface web que usa um mesmo código base para lidar com diferentes tipos de busca, apenas alterando os parâmetros e a renderização conforme necessário.

4. **Script de Teste Unificado**: Testa todos os tipos de busca usando uma única classe que implementa a lógica comum.

## Benefícios da Versão Otimizada

- **Menos Código Duplicado**: A lógica de busca é implementada uma única vez e reutilizada para diferentes tipos de busca.
- **Manutenção Simplificada**: Alterações na lógica de busca precisam ser feitas em apenas um lugar.
- **Extensibilidade**: Adicionar novos tipos de busca é mais simples, exigindo modificações mínimas.
- **Consistência**: Interface de usuário e comportamento consistentes entre os diferentes tipos de busca.
- **Melhor Experiência do Usuário**: Interface unificada para todos os tipos de busca.
- **Suporte Completo**: Implementa todos os tipos de busca disponíveis na API Serper.

## Tipos de Busca Suportados

| Tipo de Busca | Descrição | Endpoint MCP |
|---------------|-----------|--------------|
| Web | Busca web orgânica | `mcp__google_search` |
| Imagens | Busca de imagens | `mcp__serper_image_search` |
| Vídeos | Busca de vídeos | `mcp__serper_video_search` |
| Notícias | Busca de notícias | `mcp__serper_news_search` |
| Lugares | Busca de locais e pontos de interesse | `mcp__serper_places_search` |
| Mapas | Busca em mapas | `mcp__serper_maps_search` |
| Reviews | Busca de avaliações | `mcp__serper_reviews_search` |
| Shopping | Busca de produtos para compras | `mcp__serper_shopping_search` |
| Image Search (Lens) | Busca por imagem | `mcp__serper_lens_search` |
| Scholar | Busca acadêmica | `mcp__serper_scholar_search` |
| Patents | Busca de patentes | `mcp__serper_patents_search` |
| Webpage | Análise de páginas web | `mcp__serper_webpage_search` |
| Autocomplete | Sugestões de autocompletar | `mcp__serper_autocomplete` |

## Contribuindo

Contribuições são bem-vindas! Sinta-se à vontade para abrir issues ou pull requests com melhorias, correções de bugs ou novas funcionalidades.

## Licença

Este projeto está licenciado sob a licença MIT - veja o arquivo LICENSE para detalhes.
