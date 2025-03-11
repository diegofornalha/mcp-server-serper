# Visualizador de Busca de Imagens - Streamlit 

Este aplicativo Streamlit permite visualizar os resultados de busca de imagens obtidos pela API Serper através do servidor MCP Python.

## Funcionalidades

- Realizar buscas de imagens com diferentes parâmetros
- Visualizar as imagens em um formato de grade
- Acessar links para as imagens e páginas originais
- Configurar número de resultados, região e idioma

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
streamlit run image_search_app.py
```

Isso iniciará o servidor Streamlit e abrirá o aplicativo no seu navegador padrão (geralmente em http://localhost:8501).

## Como usar

1. Digite sua consulta de busca no campo apropriado
2. Ajuste os parâmetros de região e idioma, se necessário
3. Selecione o número de resultados desejado usando o controle deslizante
4. Clique em "Buscar Imagens"
5. Navegue pelos resultados exibidos na grade de imagens

## Interface

- **Barra lateral**: Contém os controles para configurar a busca
- **Área principal**: Exibe os resultados da busca em formato de grade
- **Informações da imagem**: Cada imagem é exibida com seu título, fonte, dimensões e links para a página e imagem originais

## Integração com o MCP Serper

Este aplicativo é um exemplo de como os resultados do servidor MCP Serper podem ser visualizados em uma interface amigável. Ele utiliza diretamente a API Serper, mas pode ser facilmente adaptado para usar o servidor MCP.

Para integrar com o servidor MCP completo, seria necessário modificar a função `search_images` para fazer a chamada através da interface do MCP em vez de acessar diretamente a API Serper. 