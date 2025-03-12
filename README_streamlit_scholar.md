# Visualizador de Busca Acadêmica - Streamlit 

Este aplicativo Streamlit permite visualizar os resultados de busca acadêmica (Google Scholar) obtidos pela API Serper através do servidor MCP Python.

## Funcionalidades

- Realizar buscas de publicações acadêmicas com diferentes parâmetros
- Visualizar artigos científicos, livros e outras publicações em um formato de cards
- Filtrar resultados por período de tempo (última hora, dia, semana, mês, ano)
- Configurar região, idioma e número de resultados
- Ver informações detalhadas como autores, ano de publicação e número de citações
- Acessar links para os documentos originais e PDFs (quando disponíveis)
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
streamlit run scholar_search_streamlit.py
```

Isso iniciará o servidor Streamlit e abrirá o aplicativo no seu navegador padrão (geralmente em http://localhost:8501).

## Como usar

1. Digite sua consulta de busca no campo apropriado
2. Selecione a região desejada (Brasil, Estados Unidos, Reino Unido, etc.)
3. Escolha o período de tempo para filtrar os resultados
4. Selecione o número de resultados desejado usando o controle deslizante
5. Clique em "Buscar Artigos"
6. Navegue pelos resultados exibidos nos cards de publicações acadêmicas

## Interface

- **Barra lateral**: Contém os controles para configurar a busca
- **Área principal**: Exibe os resultados da busca em formato de cards
- **Cards acadêmicos**: Cada publicação é exibida com seu título, autores, ano, snippet e links para o documento original e PDF (quando disponível)
- **Contador de citações**: Exibe o número de citações de cada publicação
- **Contador de créditos**: Exibe a quantidade de créditos da API utilizados na consulta

## Dados das Publicações

O aplicativo exibe as seguintes informações para cada publicação (quando disponíveis):

- **Título**: Nome do artigo, livro ou publicação
- **Informações de publicação**: Autores, fonte, editora
- **Ano**: Ano de publicação
- **Número de citações**: Quantidade de vezes que a publicação foi citada
- **Snippet**: Breve trecho do conteúdo
- **Link para a publicação**: URL para acessar o documento original
- **Link para PDF**: URL para download do PDF (quando disponível)

## Consumo de Créditos

Este aplicativo mostra a quantidade de créditos utilizados em cada consulta realizada na API Serper. Essa informação é exibida junto ao contador de resultados e é importante para monitorar o uso da API, especialmente em planos com limites de consulta.

## Integração com o MCP Serper

Este aplicativo é um exemplo de como os resultados do servidor MCP Serper podem ser visualizados em uma interface amigável. Ele utiliza diretamente a API Serper, mas pode ser facilmente adaptado para usar o servidor MCP.

Para integrar com o servidor MCP completo, seria necessário modificar a função `search_scholar` para fazer a chamada através da interface do MCP em vez de acessar diretamente a API Serper.

## Características Específicas de Busca Acadêmica

A busca acadêmica através do Google Scholar oferece algumas características específicas:

- **Contagem de citações**: Permite identificar publicações mais relevantes/influentes
- **Acesso a PDFs**: Links diretos para documentos completos quando disponíveis
- **Refinamento por período**: Filtragem por data para encontrar pesquisas recentes
- **Informações bibliográficas**: Dados formatados para referências acadêmicas

## Solução de Problemas

Se você encontrar problemas ao executar o aplicativo, verifique o seguinte:

1. A chave da API Serper está corretamente configurada no arquivo `.env` ou como variável de ambiente
2. Todas as dependências estão instaladas corretamente
3. O servidor Streamlit está em execução e acessível
4. Há conexão com a internet para acessar a API Serper

## Renderização HTML Segura

Este aplicativo implementa técnicas seguras de renderização HTML para evitar problemas comuns:

1. Escape de caracteres especiais em todos os dados provenientes da API
2. Construção progressiva de HTML em vez de strings complexas
3. Separação da lógica condicional da construção do HTML

Essas técnicas garantem uma exibição consistente e evitam problemas de renderização onde código HTML poderia ser exibido como texto em vez de elementos formatados.

## Limitações

- O aplicativo depende da disponibilidade da API Serper
- O número máximo de resultados é limitado a 30 para evitar sobrecarga
- A formatação e disponibilidade de dados pode variar dependendo da fonte original
- Os créditos utilizados em cada consulta são contabilizados no seu plano da API Serper 