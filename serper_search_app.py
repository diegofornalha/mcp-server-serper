#!/usr/bin/env python3

"""
Aplicativo web unificado para visualizar resultados de busca da API Serper.
Suporta múltiplos tipos de busca (web, imagens, vídeos, etc.) em uma única interface.
"""

import os
import json
import http.client
import webbrowser
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse
import html

# Tentar importar dotenv, mas não é obrigatório
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

# Obter a chave da API do ambiente
SERPER_API_KEY = os.getenv("SERPER_API_KEY")
if not SERPER_API_KEY:
    print("AVISO: A chave da API Serper não foi encontrada. Certifique-se de configurar a variável de ambiente SERPER_API_KEY ou criar um arquivo .env.")
    SERPER_API_KEY = "5b5305befa6a1187c56d7ba06e2971aca87e6a0e"  # Chave padrão para testes

class SerperClient:
    """Cliente para interagir com a API Serper."""
    
    def __init__(self, api_key):
        """Inicializa o cliente com a chave da API."""
        self.api_key = api_key
        self.base_url = "google.serper.dev"
    
    def _make_request(self, endpoint, payload):
        """
        Faz uma requisição para a API Serper.
        
        Args:
            endpoint: Endpoint da API (ex: /search, /images, /videos)
            payload: Dados para enviar na requisição
            
        Returns:
            Dados da resposta ou dicionário de erro
        """
        try:
            conn = http.client.HTTPSConnection(self.base_url)
            headers = {
                'X-API-KEY': self.api_key,
                'Content-Type': 'application/json'
            }
            
            # Converter payload para JSON
            json_payload = json.dumps(payload)
            
            # Fazer a requisição
            conn.request('POST', endpoint, json_payload, headers)
            
            # Obter resposta
            res = conn.getresponse()
            data = res.read()
            
            # Verificar se a resposta foi bem-sucedida
            if res.status != 200:
                return {"error": f"Erro na API: {res.status} {res.reason}", "raw": data.decode('utf-8')}
            
            # Decodificar e retornar os dados JSON
            return json.loads(data.decode('utf-8'))
        except Exception as e:
            return {"error": f"Erro na requisição: {str(e)}"}
        finally:
            conn.close()
    
    def search(self, search_type, **kwargs):
        """
        Realiza uma busca genérica na API Serper.
        
        Args:
            search_type: Tipo de busca (search, images, videos, etc.)
            **kwargs: Parâmetros da busca (query, location, gl, hl, num, etc.)
            
        Returns:
            Resultados da busca
        """
        # Mapear endpoints com base no tipo de busca
        endpoints = {
            "web": "/search",
            "images": "/images",
            "videos": "/videos",
            "news": "/news",
            "places": "/places"
        }
        
        # Obter o endpoint correto
        endpoint = endpoints.get(search_type, "/search")
        
        # Preparar o payload
        payload = {
            "q": kwargs.get("query"),
            "location": kwargs.get("location", "United States"),
            "gl": kwargs.get("gl", "us"),
            "hl": kwargs.get("hl", "en"),
            "num": kwargs.get("num", 10)
        }
        
        # Remover parâmetros None
        payload = {k: v for k, v in payload.items() if v is not None}
        
        # Fazer a requisição
        return self._make_request(endpoint, payload)

# Criar uma instância do cliente
serper_client = SerperClient(SERPER_API_KEY)

def generate_card_html(search_type, item):
    """
    Gera HTML para um card de resultado, com base no tipo de busca.
    
    Args:
        search_type: Tipo de busca (web, images, videos, etc.)
        item: Item do resultado
        
    Returns:
        HTML do card
    """
    if search_type == "images":
        return generate_image_card_html(item)
    elif search_type == "videos":
        return generate_video_card_html(item)
    else:
        return generate_default_card_html(item)

def generate_image_card_html(image):
    """Gera HTML para um card de imagem."""
    return f"""
    <div class="card image-card">
        <div class="image-container">
            <a href="{html.escape(image.get('link', '#'))}" target="_blank">
                <img src="{html.escape(image.get('imageUrl', ''))}" alt="{html.escape(image.get('title', 'Sem título'))}" loading="lazy">
            </a>
        </div>
        <div class="card-info">
            <h3><a href="{html.escape(image.get('link', '#'))}" target="_blank">{html.escape(image.get('title', 'Sem título'))}</a></h3>
            <p class="source">{html.escape(image.get('source', 'Fonte desconhecida'))}</p>
        </div>
    </div>
    """

def generate_video_card_html(video):
    """Gera HTML para um card de vídeo."""
    # Obter a thumbnail ou usar uma imagem padrão
    thumbnail = video.get('thumbnailUrl', '')
    if not thumbnail:
        # Usar ID do vídeo do YouTube (se disponível) para construir URL de thumbnail
        link = video.get('link', '')
        if 'youtube.com' in link and 'v=' in link:
            video_id = link.split('v=')[1].split('&')[0]
            thumbnail = f"https://img.youtube.com/vi/{video_id}/0.jpg"
        elif 'youtu.be' in link:
            video_id = link.split('/')[-1].split('?')[0]
            thumbnail = f"https://img.youtube.com/vi/{video_id}/0.jpg"
    
    # Formatar a duração do vídeo
    duration = video.get('duration', 'Desconhecida')
    
    return f"""
    <div class="card video-card">
        <div class="video-thumbnail">
            <a href="{html.escape(video.get('link', '#'))}" target="_blank">
                <img src="{html.escape(thumbnail)}" alt="{html.escape(video.get('title', 'Sem título'))}" loading="lazy">
                <div class="duration">{html.escape(duration)}</div>
            </a>
        </div>
        <div class="card-info">
            <h3><a href="{html.escape(video.get('link', '#'))}" target="_blank">{html.escape(video.get('title', 'Sem título'))}</a></h3>
            <p class="source">{html.escape(video.get('channelTitle', 'Canal desconhecido'))}</p>
            <p class="metadata">
                {f"<span>{html.escape(str(video.get('views', '')))}</span>" if video.get('views') else ""}
                {f"<span>{html.escape(video.get('publishedDate', ''))}</span>" if video.get('publishedDate') else ""}
            </p>
        </div>
    </div>
    """

def generate_default_card_html(item):
    """Gera HTML para um card genérico."""
    return f"""
    <div class="card default-card">
        <div class="card-info">
            <h3><a href="{html.escape(item.get('link', '#'))}" target="_blank">{html.escape(item.get('title', 'Sem título'))}</a></h3>
            <p class="description">{html.escape(item.get('snippet', ''))}</p>
            <p class="source">{html.escape(item.get('source', ''))}</p>
        </div>
    </div>
    """

def generate_html_results(search_type, results, query):
    """
    Gera HTML para exibir os resultados da busca.
    
    Args:
        search_type: Tipo de busca (web, images, videos, etc.)
        results: Resultados da busca
        query: Consulta realizada
        
    Returns:
        HTML formatado com os resultados
    """
    # Se ocorreu um erro, mostra a mensagem de erro
    if "error" in results:
        return f"""
        <div class="error">
            <h2>Erro ao realizar a busca</h2>
            <p>{html.escape(results["error"])}</p>
            {f"<pre>{html.escape(results.get('raw', ''))}</pre>" if "raw" in results else ""}
        </div>
        """
    
    # Obter a lista de itens baseado no tipo de busca
    items_key_map = {
        "web": "organic",
        "images": "images",
        "videos": "videos",
        "news": "news",
        "places": "places"
    }
    
    items_key = items_key_map.get(search_type, "organic")
    items = results.get(items_key, [])
    
    # Se não tem itens, mostra uma mensagem
    if not items:
        return f"""
        <div class="no-results">
            <h2>Nenhum resultado encontrado para "{html.escape(query)}"</h2>
        </div>
        """
    
    # Gera o HTML para exibir os itens em uma grade
    items_html = ""
    for item in items:
        items_html += generate_card_html(search_type, item)
    
    return f"""
    <div class="results-header">
        <h2>Resultados para: "{html.escape(query)}"</h2>
        <p>Encontrados {len(items)} {search_type}</p>
    </div>
    <div class="parameters">
        <h3>Parâmetros da Busca</h3>
        <pre>{html.escape(json.dumps(results.get("searchParameters", {}), indent=2, ensure_ascii=False))}</pre>
    </div>
    <div class="items-grid {search_type}-grid">
        {items_html}
    </div>
    """

def generate_html_page(content, title="Visualizador de Busca Serper", search_type="web"):
    """
    Gera uma página HTML completa para o aplicativo.
    
    Args:
        content: Conteúdo HTML para o corpo da página
        title: Título da página
        search_type: Tipo de busca selecionado
        
    Returns:
        HTML completo da página
    """
    # Ícones para os tipos de busca
    search_icons = {
        "web": "🔍",
        "images": "🖼️",
        "videos": "🎬",
        "news": "📰",
        "places": "📍"
    }
    
    # Cores para os tipos de busca
    search_colors = {
        "web": "#4285F4",  # Google Blue
        "images": "#34A853",  # Google Green
        "videos": "#EA4335",  # Google Red (YouTube color)
        "news": "#FBBC05",  # Google Yellow
        "places": "#4285F4"   # Google Blue
    }
    
    # Obter o ícone e a cor do tipo de busca atual
    icon = search_icons.get(search_type, "🔍")
    primary_color = search_colors.get(search_type, "#4285F4")
    
    return f"""
    <!DOCTYPE html>
    <html lang="pt-br">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{html.escape(title)} - Visualizador Serper</title>
        <style>
            :root {{
                --primary-color: {primary_color};
                --primary-dark: {primary_color}dd;
                --primary-light: {primary_color}22;
                --text-color: #333;
                --bg-color: #f7f7f7;
                --card-bg: white;
                --shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
                --shadow-hover: 0 5px 15px rgba(0, 0, 0, 0.1);
                --radius: 8px;
            }}
            
            * {{
                box-sizing: border-box;
                margin: 0;
                padding: 0;
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
            }}
            
            body {{
                background-color: var(--bg-color);
                color: var(--text-color);
                line-height: 1.6;
            }}
            
            .container {{
                max-width: 1200px;
                margin: 0 auto;
                padding: 20px;
            }}
            
            header {{
                background-color: var(--primary-color);
                color: white;
                padding: 20px;
                margin-bottom: 20px;
                border-radius: var(--radius);
                box-shadow: var(--shadow);
            }}
            
            header h1 {{
                margin-bottom: 10px;
                display: flex;
                align-items: center;
                gap: 10px;
            }}
            
            .search-type-selector {{
                display: flex;
                flex-wrap: wrap;
                gap: 10px;
                margin-top: 15px;
            }}
            
            .search-type-button {{
                background-color: rgba(255, 255, 255, 0.2);
                color: white;
                border: none;
                padding: 8px 15px;
                border-radius: var(--radius);
                cursor: pointer;
                font-size: 14px;
                font-weight: 600;
                display: flex;
                align-items: center;
                gap: 6px;
                transition: background-color 0.3s;
            }}
            
            .search-type-button:hover {{
                background-color: rgba(255, 255, 255, 0.3);
            }}
            
            .search-type-button.active {{
                background-color: white;
                color: var(--primary-color);
            }}
            
            form {{
                background-color: var(--card-bg);
                padding: 20px;
                border-radius: var(--radius);
                box-shadow: var(--shadow);
                margin-bottom: 20px;
            }}
            
            .form-group {{
                margin-bottom: 15px;
            }}
            
            label {{
                display: block;
                margin-bottom: 5px;
                font-weight: 600;
            }}
            
            input, select {{
                width: 100%;
                padding: 10px;
                border: 1px solid #ddd;
                border-radius: 4px;
                font-size: 16px;
            }}
            
            button {{
                background-color: var(--primary-color);
                color: white;
                border: none;
                padding: 12px 20px;
                border-radius: 4px;
                cursor: pointer;
                font-size: 16px;
                font-weight: 600;
                transition: background-color 0.3s;
            }}
            
            button:hover {{
                background-color: var(--primary-dark);
            }}
            
            .results-section {{
                background-color: var(--card-bg);
                padding: 20px;
                border-radius: var(--radius);
                box-shadow: var(--shadow);
            }}
            
            .error {{
                background-color: #ffebee;
                color: #c62828;
                padding: 15px;
                border-radius: 4px;
                margin-bottom: 20px;
            }}
            
            .no-results {{
                background-color: #fff8e1;
                color: #ff8f00;
                padding: 15px;
                border-radius: 4px;
                margin-bottom: 20px;
            }}
            
            .results-header {{
                margin-bottom: 20px;
            }}
            
            .parameters {{
                background-color: #f5f5f5;
                padding: 15px;
                border-radius: 4px;
                margin-bottom: 20px;
                overflow-x: auto;
            }}
            
            .parameters pre {{
                white-space: pre-wrap;
            }}
            
            .items-grid {{
                display: grid;
                gap: 20px;
            }}
            
            .web-grid {{
                grid-template-columns: 1fr;
            }}
            
            .images-grid, .videos-grid {{
                grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
            }}
            
            .card {{
                background-color: var(--card-bg);
                border-radius: var(--radius);
                overflow: hidden;
                box-shadow: var(--shadow);
                transition: transform 0.3s, box-shadow 0.3s;
            }}
            
            .card:hover {{
                transform: translateY(-5px);
                box-shadow: var(--shadow-hover);
            }}
            
            .card-info {{
                padding: 15px;
            }}
            
            .card-info h3 {{
                margin-bottom: 8px;
                font-size: 16px;
                line-height: 1.4;
                max-height: 45px;
                overflow: hidden;
                text-overflow: ellipsis;
                display: -webkit-box;
                -webkit-line-clamp: 2;
                -webkit-box-orient: vertical;
            }}
            
            .card-info h3 a {{
                color: var(--text-color);
                text-decoration: none;
            }}
            
            .card-info h3 a:hover {{
                color: var(--primary-color);
            }}
            
            .source, .description {{
                color: #666;
                font-size: 14px;
                margin-bottom: 5px;
            }}
            
            .description {{
                max-height: 60px;
                overflow: hidden;
                text-overflow: ellipsis;
                display: -webkit-box;
                -webkit-line-clamp: 3;
                -webkit-box-orient: vertical;
            }}
            
            .metadata {{
                display: flex;
                flex-wrap: wrap;
                gap: 10px;
                font-size: 12px;
                color: #666;
            }}
            
            /* Estilos específicos para imagens */
            .image-container {{
                height: 180px;
                overflow: hidden;
                background-color: #f1f1f1;
            }}
            
            .image-container img {{
                width: 100%;
                height: 100%;
                object-fit: cover;
                transition: transform 0.3s;
            }}
            
            .image-card:hover .image-container img {{
                transform: scale(1.05);
            }}
            
            /* Estilos específicos para vídeos */
            .video-thumbnail {{
                position: relative;
                height: 180px;
                overflow: hidden;
                background-color: #000;
            }}
            
            .video-thumbnail img {{
                width: 100%;
                height: 100%;
                object-fit: cover;
            }}
            
            .duration {{
                position: absolute;
                bottom: 8px;
                right: 8px;
                background-color: rgba(0, 0, 0, 0.8);
                color: white;
                padding: 2px 6px;
                border-radius: 3px;
                font-size: 12px;
                font-weight: 600;
            }}
            
            footer {{
                margin-top: 30px;
                text-align: center;
                padding: 20px;
                color: #666;
                font-size: 14px;
            }}
            
            @media (max-width: 768px) {{
                .search-type-selector {{
                    justify-content: center;
                }}
                
                .images-grid, .videos-grid {{
                    grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
                }}
            }}
            
            @media (max-width: 480px) {{
                .images-grid, .videos-grid {{
                    grid-template-columns: 1fr;
                }}
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <header>
                <h1>{icon} Visualizador de Busca Serper</h1>
                <p>Este aplicativo permite visualizar os resultados de busca da API Serper</p>
                
                <div class="search-type-selector">
                    <a href="/?type=web" class="search-type-button {search_type == 'web' and 'active' or ''}">🔍 Web</a>
                    <a href="/?type=images" class="search-type-button {search_type == 'images' and 'active' or ''}">🖼️ Imagens</a>
                    <a href="/?type=videos" class="search-type-button {search_type == 'videos' and 'active' or ''}">🎬 Vídeos</a>
                    <a href="/?type=news" class="search-type-button {search_type == 'news' and 'active' or ''}">📰 Notícias</a>
                    <a href="/?type=places" class="search-type-button {search_type == 'places' and 'active' or ''}">📍 Locais</a>
                </div>
            </header>
            
            <form action="/" method="get">
                <input type="hidden" name="type" value="{html.escape(search_type)}">
                
                <div class="form-group">
                    <label for="query">Consulta de busca:</label>
                    <input type="text" id="query" name="query" value="{html.escape(title if title != 'Visualizador de Busca Serper' else 'agentes de inteligência artificial')}" required>
                </div>
                
                <div class="form-grid" style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px;">
                    <div class="form-group">
                        <label for="location">Localização:</label>
                        <input type="text" id="location" name="location" value="Brazil">
                    </div>
                    
                    <div class="form-group">
                        <label for="gl">Código da região:</label>
                        <input type="text" id="gl" name="gl" value="br">
                    </div>
                    
                    <div class="form-group">
                        <label for="hl">Código de idioma:</label>
                        <input type="text" id="hl" name="hl" value="pt-br">
                    </div>
                    
                    <div class="form-group">
                        <label for="num">Número de resultados:</label>
                        <input type="number" id="num" name="num" value="10" min="1" max="50">
                    </div>
                </div>
                
                <button type="submit">Buscar {search_type == 'images' and 'Imagens' or search_type == 'videos' and 'Vídeos' or search_type == 'news' and 'Notícias' or search_type == 'places' and 'Locais' or 'Conteúdo'}</button>
            </form>
            
            <div class="results-section">
                {content}
            </div>
            
            <footer>
                <p>Desenvolvido com Python e API Serper | Visualizador Unificado de Busca v1.0</p>
            </footer>
        </div>
    </body>
    </html>
    """

class SerperSearchHandler(BaseHTTPRequestHandler):
    """Manipulador de requisições HTTP para o servidor web."""
    
    def do_GET(self):
        """Processa requisições GET."""
        # Definir headers
        self.send_response(200)
        self.send_header('Content-type', 'text/html; charset=utf-8')
        self.end_headers()
        
        # Página inicial
        if self.path == '/' or self.path.startswith('/?'):
            # Extrair parâmetros da URL
            query_params = parse_qs(urlparse(self.path).query)
            
            # Obter o tipo de busca (padrão: web)
            search_type = query_params.get('type', ['web'])[0]
            if search_type not in ['web', 'images', 'videos', 'news', 'places']:
                search_type = 'web'
            
            # Se há uma consulta, realiza a busca
            if 'query' in query_params:
                query = query_params['query'][0]
                location = query_params.get('location', ['Brazil'])[0]
                gl = query_params.get('gl', ['br'])[0]
                hl = query_params.get('hl', ['pt-br'])[0]
                
                try:
                    num = int(query_params.get('num', ['10'])[0])
                    num = max(1, min(50, num))  # Limitar entre 1 e 50
                except ValueError:
                    num = 10
                
                # Realizar busca
                results = serper_client.search(
                    search_type=search_type,
                    query=query,
                    location=location,
                    gl=gl,
                    hl=hl,
                    num=num
                )
                
                # Gerar HTML com resultados
                content = generate_html_results(search_type, results, query)
                html_page = generate_html_page(content, query, search_type)
            else:
                # Página inicial sem resultados
                content = f"""
                <div class="welcome">
                    <h2>Bem-vindo ao Visualizador de Busca Serper</h2>
                    <p>Digite uma consulta e clique em "Buscar" para visualizar os resultados.</p>
                    <p>Este aplicativo utiliza a API Serper para realizar buscas na web, imagens, vídeos e mais.</p>
                    <p>Você está no modo de busca <strong>{search_type}</strong>.</p>
                </div>
                """
                html_page = generate_html_page(content, search_type=search_type)
            
            # Enviar resposta
            self.wfile.write(html_page.encode('utf-8'))
        else:
            # Página não encontrada
            content = """
            <div class="error">
                <h2>Página não encontrada</h2>
                <p>A página solicitada não existe. <a href="/">Voltar para a página inicial</a>.</p>
            </div>
            """
            html_page = generate_html_page(content, "Página não encontrada")
            self.wfile.write(html_page.encode('utf-8'))

def run_server(port=8000):
    """
    Inicia o servidor HTTP.
    
    Args:
        port: Porta para o servidor (padrão: 8000)
    """
    server_address = ('', port)
    httpd = HTTPServer(server_address, SerperSearchHandler)
    print(f"Servidor iniciado em http://localhost:{port}")
    print("Pressione Ctrl+C para encerrar.")
    
    # Abrir navegador automaticamente
    webbrowser.open(f"http://localhost:{port}")
    
    # Iniciar servidor
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nServidor encerrado.")
        httpd.server_close()

if __name__ == "__main__":
    run_server() 