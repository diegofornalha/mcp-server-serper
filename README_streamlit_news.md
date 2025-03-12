# Visualizador de Busca de Notícias - Streamlit 

Este aplicativo Streamlit permite visualizar os resultados de busca de notícias obtidos pela API Serper através do servidor MCP Python.

## Funcionalidades

- Realizar buscas de notícias com diferentes parâmetros
- Visualizar as notícias em um formato de cards
- Filtrar resultados por período de tempo (última hora, dia, semana, mês, ano)
- Configurar região, idioma e número de resultados
- Visualizar imagens associadas às notícias (quando disponíveis)
- Acessar links para as notícias originais

## Requisitos

- Python 3.6+
- Streamlit
- python-dotenv
- Chave da API Serper (definida como variável de ambiente `SERPER_API_KEY`)

## Instalação

1. Instale as dependências necessárias:

```bash
pip install -r requirements_streamlit.txt
```

2. Configure sua chave de API Serper:

Crie um arquivo `.env` no diretório raiz (se ainda não existir) com o seguinte conteúdo:

```
SERPER_API_KEY=sua_chave_api_aqui
```

Ou defina a variável de ambiente:

```bash
export SERPER_API_KEY=sua_chave_api_aqui
```

## Execução

Execute o aplicativo com o comando:

```bash
streamlit run news_search_streamlit.py
```

Isso iniciará o servidor Streamlit e abrirá o aplicativo no seu navegador padrão (geralmente em http://localhost:8501).

## Como usar

1. Digite sua consulta de busca no campo apropriado
2. Selecione a região desejada (Brasil, Estados Unidos, Reino Unido, etc.)
3. Escolha o período de tempo para filtrar os resultados
4. Selecione o número de resultados desejado usando o controle deslizante
5. Clique em "Buscar Notícias"
6. Navegue pelos resultados exibidos nos cards de notícias

## Interface

- **Barra lateral**: Contém os controles para configurar a busca
- **Área principal**: Exibe os resultados da busca em formato de cards
- **Cards de notícias**: Cada notícia é exibida com seu título, fonte, data, snippet e links para a página original
- **Imagens**: Quando disponíveis, as imagens associadas às notícias são exibidas nos cards

## Parâmetros de Tempo

O aplicativo suporta os seguintes parâmetros de tempo para filtrar resultados:

- **Qualquer período**: Sem filtro de tempo
- **Última hora**: Notícias publicadas na última hora
- **Último dia**: Notícias publicadas nas últimas 24 horas
- **Última semana**: Notícias publicadas nos últimos 7 dias
- **Último mês**: Notícias publicadas nos últimos 30 dias
- **Último ano**: Notícias publicadas no último ano

## Integração com o MCP Serper

Este aplicativo é um exemplo de como os resultados do servidor MCP Serper podem ser visualizados em uma interface amigável. Ele utiliza diretamente a API Serper, mas pode ser facilmente adaptado para usar o servidor MCP.

Para integrar com o servidor MCP completo, seria necessário modificar a função `search_news` para fazer a chamada através da interface do MCP em vez de acessar diretamente a API Serper.

## Solução de Problemas

Se você encontrar problemas ao executar o aplicativo, verifique o seguinte:

1. A chave da API Serper está corretamente configurada no arquivo `.env` ou como variável de ambiente
2. Todas as dependências estão instaladas corretamente
3. O servidor Streamlit está em execução e acessível
4. Há conexão com a internet para acessar a API Serper

## Limitações

- O aplicativo depende da disponibilidade da API Serper
- O número máximo de resultados é limitado a 20 para evitar sobrecarga
- A formatação e disponibilidade de dados (como imagens, datas) pode variar dependendo da fonte das notícias 