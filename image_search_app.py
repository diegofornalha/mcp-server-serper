#!/usr/bin/env python3

"""
Aplicativo web simples para visualizar resultados de busca de imagens da API Serper.
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

def search_images(query, location="Brazil", gl="br", hl="pt-br", num=10):
    """
    Realiza uma busca de imagens usando a API Serper.
    
    Args:
        query: Consulta de busca
        location: Localização para resultados
        gl: Código da região
        hl: Código de idioma
        num: Número de resultados
        
    Returns:
        Resultados da busca de imagens
    """
    try:
        conn = http.client.HTTPSConnection('google.serper.dev')
        payload = json.dumps({
            "q": query,
            "location": location,
            "gl": gl,
            "hl": hl,
            "num": num
        })
        headers = {
            'X-API-KEY': SERPER_API_KEY,
            'Content-Type': 'application/json'
        }
        
        # Enviar requisição
        conn.request('POST', '/images', payload, headers)
        
        # Receber resposta
        res = conn.getresponse()
        data = res.read()
        
        if res.status != 200:
            return {"error": f"Erro na API: {res.status} {res.reason}", "raw": data.decode('utf-8')}
            
        return json.loads(data.decode('utf-8'))
    except Exception as e:
        return {"error": f"Erro na requisição: {str(e)}"}
    finally:
        conn.close()

def generate_html_results(results, query):
    """
    Gera HTML para exibir os resultados da busca de imagens.
    
    Args:
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
    
    # Se não tem imagens, mostra uma mensagem
    if not results.get("images"):
        return f"""
        <div class="no-results">
            <h2>Nenhuma imagem encontrada para "{html.escape(query)}"</h2>
        </div>
        """
    
    # Gera o HTML para exibir as imagens em uma grade
    images_html = ""
    for image in results.get("images", []):
        images_html += f"""
        <div class="image-card">
            <div class="image-container">
                <img src="{html.escape(image.get('thumbnailUrl', ''))}" alt="{html.escape(image.get('title', 'Sem título'))}" loading="lazy">
            </div>
            <div class="image-info">
                <h3>{html.escape(image.get('title', 'Sem título'))}</h3>
                <p><strong>Fonte:</strong> {html.escape(image.get('source', 'Desconhecida'))}</p>
                <p><strong>Dimensões:</strong> {image.get('imageWidth', '?')}x{image.get('imageHeight', '?')}</p>
                <div class="image-links">
                    <a href="{html.escape(image.get('link', '#'))}" target="_blank">Ver original</a>
                    <a href="{html.escape(image.get('imageUrl', '#'))}" target="_blank">Ver imagem</a>
                </div>
            </div>
        </div>
        """
    
    return f"""
    <div class="results-header">
        <h2>Resultados para: "{html.escape(query)}"</h2>
        <p>Encontradas {len(results.get("images", []))} imagens</p>
    </div>
    <div class="parameters">
        <h3>Parâmetros da Busca</h3>
        <pre>{html.escape(json.dumps(results.get("searchParameters", {}), indent=2, ensure_ascii=False))}</pre>
    </div>
    <div class="images-grid">
        {images_html}
    </div>
    """

def generate_html_page(content, title="Visualizador de Busca de Imagens"):
    """
    Gera uma página HTML completa para o aplicativo.
    
    Args:
        content: Conteúdo HTML para o corpo da página
        title: Título da página
        
    Returns:
        HTML completo da página
    """
    return f"""
    <!DOCTYPE html>
    <html lang="pt-br">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{html.escape(title)}</title>
        <style>
            * {{
                box-sizing: border-box;
                margin: 0;
                padding: 0;
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
            }}
            
            body {{
                background-color: #f7f7f7;
                color: #333;
                line-height: 1.6;
            }}
            
            .container {{
                max-width: 1200px;
                margin: 0 auto;
                padding: 20px;
            }}
            
            header {{
                background-color: #4285f4;
                color: white;
                padding: 20px;
                margin-bottom: 20px;
                border-radius: 8px;
                box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
            }}
            
            header h1 {{
                margin-bottom: 10px;
            }}
            
            form {{
                background-color: white;
                padding: 20px;
                border-radius: 8px;
                box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
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
                background-color: #4285f4;
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
                background-color: #3367d6;
            }}
            
            .results-section {{
                background-color: white;
                padding: 20px;
                border-radius: 8px;
                box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
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
            
            .images-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
                gap: 20px;
            }}
            
            .image-card {{
                background-color: white;
                border-radius: 8px;
                overflow: hidden;
                box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
                transition: transform 0.3s, box-shadow 0.3s;
            }}
            
            .image-card:hover {{
                transform: translateY(-5px);
                box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
            }}
            
            .image-container {{
                height: 200px;
                overflow: hidden;
                display: flex;
                align-items: center;
                justify-content: center;
                background-color: #f0f0f0;
            }}
            
            .image-container img {{
                width: 100%;
                height: 100%;
                object-fit: cover;
            }}
            
            .image-info {{
                padding: 15px;
            }}
            
            .image-info h3 {{
                margin-bottom: 10px;
                font-size: 16px;
                line-height: 1.4;
                height: 45px;
                overflow: hidden;
                text-overflow: ellipsis;
                display: -webkit-box;
                -webkit-line-clamp: 2;
                -webkit-box-orient: vertical;
            }}
            
            .image-links {{
                margin-top: 10px;
                display: flex;
                gap: 10px;
            }}
            
            .image-links a {{
                display: inline-block;
                padding: 8px 12px;
                background-color: #f0f0f0;
                color: #333;
                text-decoration: none;
                border-radius: 4px;
                font-size: 14px;
                transition: background-color 0.3s;
            }}
            
            .image-links a:hover {{
                background-color: #e0e0e0;
            }}
            
            footer {{
                margin-top: 30px;
                text-align: center;
                padding: 20px;
                color: #666;
                font-size: 14px;
            }}
            
            @media (max-width: 768px) {{
                .images-grid {{
                    grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));
                }}
            }}
            
            @media (max-width: 480px) {{
                .images-grid {{
                    grid-template-columns: 1fr;
                }}
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <header>
                <h1>🔍 Visualizador de Busca de Imagens</h1>
                <p>Este aplicativo permite visualizar os resultados de busca de imagens da API Serper</p>
            </header>
            
            <form action="/" method="get">
                <div class="form-group">
                    <label for="query">Consulta de busca:</label>
                    <input type="text" id="query" name="query" value="{html.escape(title if title != 'Visualizador de Busca de Imagens' else 'agentes de inteligência artificial')}" required>
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
                
                <button type="submit">Buscar Imagens</button>
            </form>
            
            <div class="results-section">
                {content}
            </div>
            
            <footer>
                <p>Desenvolvido com Python e API Serper | Visualizador de Busca de Imagens v1.0</p>
            </footer>
        </div>
    </body>
    </html>
    """

class ImageSearchHandler(BaseHTTPRequestHandler):
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
                results = search_images(query, location, gl, hl, num)
                
                # Gerar HTML com resultados
                content = generate_html_results(results, query)
                html_page = generate_html_page(content, query)
            else:
                # Página inicial sem resultados
                content = """
                <div class="welcome">
                    <h2>Bem-vindo ao Visualizador de Busca de Imagens</h2>
                    <p>Digite uma consulta e clique em "Buscar Imagens" para visualizar os resultados.</p>
                    <p>Este aplicativo utiliza a API Serper para realizar buscas de imagens.</p>
                </div>
                """
                html_page = generate_html_page(content)
            
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
        port: Porta para o servidor
    """
    server_address = ('', port)
    httpd = HTTPServer(server_address, ImageSearchHandler)
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