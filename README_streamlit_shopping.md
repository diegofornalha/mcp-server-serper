# Visualizador de Busca de Produtos (Shopping) - Streamlit 

Este aplicativo Streamlit permite visualizar os resultados de busca de produtos (shopping) obtidos pela API Serper através do servidor MCP Python.

## Funcionalidades

- Realizar buscas de produtos com diferentes parâmetros
- Visualizar os produtos em um formato de cards
- Filtrar resultados por período de tempo (última hora, dia, semana, mês, ano)
- Configurar região, idioma e número de resultados
- Visualizar imagens dos produtos
- Ver preços, avaliações e informações de entrega
- Acessar links para os produtos originais
- Verificar a quantidade de créditos utilizados na consulta

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
streamlit run shopping_search_streamlit.py
```

Isso iniciará o servidor Streamlit e abrirá o aplicativo no seu navegador padrão (geralmente em http://localhost:8501).

## Como usar

1. Digite sua consulta de busca no campo apropriado
2. Selecione a região desejada (Brasil, Estados Unidos, Reino Unido, etc.)
3. Escolha o período de tempo para filtrar os resultados
4. Selecione o número de resultados desejado usando o controle deslizante
5. Clique em "Buscar Produtos"
6. Navegue pelos resultados exibidos nos cards de produtos

## Interface

- **Barra lateral**: Contém os controles para configurar a busca
- **Área principal**: Exibe os resultados da busca em formato de cards em uma grade de 3 colunas
- **Cards de produtos**: Cada produto é exibido com sua imagem, título, fonte, preço, avaliações e links para a página original
- **Contador de créditos**: Exibe a quantidade de créditos da API utilizados na consulta

## Dados dos Produtos

O aplicativo exibe as seguintes informações para cada produto (quando disponíveis):

- **Título**: Nome do produto
- **Imagem**: Imagem do produto
- **Preço**: Valor do produto
- **Fonte**: Loja ou marketplace onde o produto está disponível
- **Avaliação**: Classificação por estrelas
- **Número de avaliações**: Quantidade de avaliações do produto
- **Informações de entrega**: Dados sobre frete ou entrega
- **Ofertas disponíveis**: Quantidade de ofertas existentes

## Consumo de Créditos

Este aplicativo mostra a quantidade de créditos utilizados em cada consulta realizada na API Serper. Essa informação é exibida junto ao contador de resultados e é importante para monitorar o uso da API, especialmente em planos com limites de consulta.

## Integração com o MCP Serper

Este aplicativo é um exemplo de como os resultados do servidor MCP Serper podem ser visualizados em uma interface amigável. Ele utiliza diretamente a API Serper, mas pode ser facilmente adaptado para usar o servidor MCP.

Para integrar com o servidor MCP completo, seria necessário modificar a função `search_shopping` para fazer a chamada através da interface do MCP em vez de acessar diretamente a API Serper.

## Solução de Problemas

Se você encontrar problemas ao executar o aplicativo, verifique o seguinte:

1. A chave da API Serper está corretamente configurada no arquivo `.env` ou como variável de ambiente
2. Todas as dependências estão instaladas corretamente
3. O servidor Streamlit está em execução e acessível
4. Há conexão com a internet para acessar a API Serper

## Limitações

- O aplicativo depende da disponibilidade da API Serper
- O número máximo de resultados é limitado a 30 para evitar sobrecarga
- A formatação e disponibilidade de dados (como imagens, preços, avaliações) pode variar dependendo da fonte dos produtos
- Os créditos utilizados em cada consulta são contabilizados no seu plano da API Serper 