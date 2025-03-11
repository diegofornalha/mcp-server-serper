# Visualizador Web de Busca de Imagens

Este é um aplicativo web simples que permite visualizar os resultados de busca de imagens obtidos através da API Serper.

## Funcionalidades

- Interface web amigável para realizar buscas de imagens
- Configuração de parâmetros como localização, região e idioma
- Visualização de imagens em uma grade responsiva
- Exibição de informações detalhadas sobre cada imagem
- Links para acessar a imagem original e a página onde ela está hospedada
- Execução como servidor web local Python (não requer frameworks complexos)

## Requisitos

- Python 3.6 ou superior
- Chave de API Serper (configurada como variável de ambiente)
- Conexão com a internet

## Instalação

Não é necessário instalar pacotes adicionais para executar este aplicativo. O único requisito opcional é o pacote `python-dotenv` para carregar a chave da API de um arquivo `.env`:

```bash
# Opcional: instalar dotenv para carregar variáveis de ambiente de um arquivo .env
pip install python-dotenv
```

### Configuração da Chave da API

Configure sua chave da API Serper como uma variável de ambiente:

```bash
# Linux/macOS
export SERPER_API_KEY=sua_chave_da_api_aqui

# Windows (Prompt de Comando)
set SERPER_API_KEY=sua_chave_da_api_aqui

# Windows (PowerShell)
$env:SERPER_API_KEY="sua_chave_da_api_aqui"
```

Alternativamente, crie um arquivo `.env` na mesma pasta do aplicativo com o seguinte conteúdo:

```
SERPER_API_KEY=sua_chave_da_api_aqui
```

## Execução

Para executar o aplicativo, simplesmente execute o script Python:

```bash
# Tornar o script executável (somente Unix/Linux/macOS)
chmod +x image_search_app.py

# Executar diretamente 
./image_search_app.py

# Ou, alternativamente
python3 image_search_app.py
```

Por padrão, o servidor será iniciado na porta 8000 e abrirá automaticamente o navegador padrão.

## Como Usar

1. Quando o aplicativo iniciar, você verá uma interface com um formulário para digitar sua consulta de busca
2. Digite o termo de busca desejado no campo "Consulta de busca"
3. Opcionalmente, ajuste os parâmetros:
   - Localização: define a localização geográfica para a busca (ex: "Brazil", "United States")
   - Código da região: código da região para os resultados (ex: "br", "us")
   - Código de idioma: código do idioma para os resultados (ex: "pt-br", "en")
   - Número de resultados: quantidade de imagens a serem retornadas (máximo 50)
4. Clique no botão "Buscar Imagens"
5. Os resultados serão exibidos em uma grade de imagens
6. Para cada imagem, você verá:
   - A miniatura da imagem
   - O título da imagem
   - A fonte (site de origem)
   - As dimensões da imagem
   - Links para visualizar a página original e a imagem em tamanho completo

## Interface

O aplicativo possui uma interface simples e responsiva:

- **Cabeçalho**: Título e descrição do aplicativo
- **Formulário de busca**: Campos para inserir a consulta e parâmetros
- **Seção de resultados**: Exibe os resultados da busca ou mensagens informativas
- **Grade de imagens**: Exibe as imagens encontradas em um layout adaptável a diferentes tamanhos de tela
- **Rodapé**: Informações sobre o aplicativo

## Personalização

Você pode personalizar o aplicativo modificando o código-fonte. Alguns aspectos que podem ser personalizados:

- Porta do servidor (altere o valor padrão em `run_server()`)
- Estilos CSS (editando a seção de estilos no método `generate_html_page()`)
- Layout da grade de imagens (modificando as classes CSS relacionadas à `.images-grid`)
- Parâmetros padrão de busca (alterando os valores padrão na função `search_images()`)

## Integração com o MCP Server

Este aplicativo pode ser facilmente integrado ao MCP Server, modificando a função `search_images()` para utilizar a API do servidor MCP em vez de fazer chamadas diretas à API Serper.

## Limitações

- O aplicativo não inclui paginação para resultados extensos
- Não há cache de resultados entre sessões
- A chave da API é exposta ao código JavaScript do cliente

## Solução de Problemas

- **Erro na API**: Verifique se sua chave da API Serper está correta e válida
- **Porta já em uso**: Se a porta 8000 estiver em uso, modifique o valor em `run_server()`
- **Erro ao abrir o navegador**: Se o navegador não abrir automaticamente, acesse manualmente o endereço `http://localhost:8000` 