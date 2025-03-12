#!/usr/bin/env python3

"""
Aplicativo Streamlit para busca de produtos (shopping) usando a API Serper.
Permite visualizar resultados de produtos com diferentes parâmetros de busca.
"""

import os
import json
import http.client
import streamlit as st
from dotenv import load_dotenv
import html

# Carregar variáveis de ambiente
load_dotenv()

# Configurações da página Streamlit
st.set_page_config(
    page_title="Busca de Produtos - Serper API",
    page_icon="🛍️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos CSS personalizados
st.markdown("""
<style>
    .product-card {
        border: 1px solid #ddd;
        border-radius: 8px;
        padding: 15px;
        margin-bottom: 15px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        background-color: white;
        height: 100%;
        display: flex;
        flex-direction: column;
    }
    .product-title {
        color: #1E88E5;
        text-decoration: none;
        font-weight: bold;
        font-size: 16px;
        margin-bottom: 8px;
        line-height: 1.2;
    }
    .product-source {
        color: #616161;
        font-size: 13px;
        margin-bottom: 5px;
    }
    .product-price {
        color: #4CAF50;
        font-size: 18px;
        font-weight: bold;
        margin-bottom: 8px;
    }
    .product-delivery {
        color: #616161;
        font-size: 12px;
        margin-bottom: 5px;
    }
    .product-rating {
        color: #FF9800;
        font-size: 14px;
        margin-bottom: 5px;
    }
    .product-reviews {
        color: #616161;
        font-size: 12px;
        margin-bottom: 8px;
    }
    .product-link {
        color: #1976D2;
        font-size: 13px;
        text-decoration: none;
        margin-top: auto;
    }
    .product-image {
        max-width: 100%;
        height: auto;
        border-radius: 4px;
        margin-bottom: 10px;
        object-fit: contain;
        max-height: 180px;
    }
    .header-container {
        background-color: #1976D2;
        padding: 20px;
        border-radius: 8px;
        color: white;
        margin-bottom: 20px;
    }
    .results-info {
        background-color: #f1f8fe;
        padding: 10px;
        border-radius: 5px;
        margin-bottom: 20px;
        text-align: center;
    }
    .credits-info {
        background-color: #fff3cd;
        padding: 5px 10px;
        border-radius: 5px;
        margin-top: 5px;
        font-size: 14px;
        display: inline-block;
    }
</style>
""", unsafe_allow_html=True)

# Obter a chave da API Serper do ambiente
SERPER_API_KEY = os.getenv("SERPER_API_KEY")
if not SERPER_API_KEY:
    st.error(
        "⚠️ Chave da API Serper não encontrada. "
        "Configure a variável de ambiente SERPER_API_KEY ou crie um arquivo .env."
    )
    SERPER_API_KEY = ""


# Função para buscar produtos usando a API Serper
def search_shopping(query, location="Brazil", gl="br", hl="pt-br", num=20, tbs=None):
    """
    Busca produtos (shopping) usando a API Serper.
    
    Args:
        query: Termo de busca
        location: Localização geográfica
        gl: Código de região do Google
        hl: Código de idioma
        num: Número de resultados
        tbs: Filtro de tempo (qdr:h, qdr:d, qdr:w, qdr:m, qdr:y)
        
    Returns:
        Resultados da busca ou mensagem de erro
    """
    try:
        # Criar conexão HTTPS
        conn = http.client.HTTPSConnection('google.serper.dev')
        
        # Preparar payload da requisição
        payload = {
            "q": query,
            "location": location,
            "gl": gl,
            "hl": hl,
            "num": num,
            "type": "shopping"
        }
        
        # Adicionar filtro de tempo se especificado
        if tbs:
            payload["tbs"] = tbs
        
        # Cabeçalhos da requisição
        headers = {
            'X-API-KEY': SERPER_API_KEY,
            'Content-Type': 'application/json'
        }
        
        # Fazer a requisição POST
        conn.request('POST', '/shopping', json.dumps(payload), headers)
        
        # Obter resposta
        res = conn.getresponse()
        data = res.read().decode('utf-8')
        
        # Verificar se houve erro na resposta
        if res.status != 200:
            return {"error": f"Erro na API: {res.status} {res.reason}", "raw": data}
        
        # Converter resposta para JSON e retornar
        return json.loads(data)
    
    except Exception as e:
        return {"error": f"Erro na requisição: {str(e)}"}
    
    finally:
        # Fechar conexão
        conn.close()


# Renderiza as estrelas de avaliação
def render_stars(rating):
    """Renderiza as estrelas de avaliação."""
    if not rating:
        return ""
    
    full_stars = int(rating)
    half_star = rating - full_stars >= 0.5
    
    stars = "★" * full_stars
    if half_star:
        stars += "½"
    
    return stars


# Interface da Barra Lateral
with st.sidebar:
    st.header("🛍️ Configurações da Busca")
    
    # Campo de busca
    query = st.text_input("Termo de busca", value="smartphone")
    
    # Seleção de região
    region_options = {
        "Brasil": {"location": "Brazil", "gl": "br", "hl": "pt-br"},
        "Estados Unidos": {"location": "United States", "gl": "us", "hl": "en"},
        "Reino Unido": {"location": "United Kingdom", "gl": "uk", "hl": "en-GB"},
        "França": {"location": "France", "gl": "fr", "hl": "fr"},
        "Alemanha": {"location": "Germany", "gl": "de", "hl": "de"},
        "Espanha": {"location": "Spain", "gl": "es", "hl": "es"},
        "Portugal": {"location": "Portugal", "gl": "pt", "hl": "pt-PT"},
        "Japão": {"location": "Japan", "gl": "jp", "hl": "ja"},
    }
    
    selected_region = st.selectbox("Região", options=list(region_options.keys()), index=0)
    
    # Período de tempo
    time_options = {
        "Qualquer período": None,
        "Última hora": "qdr:h",
        "Último dia": "qdr:d",
        "Última semana": "qdr:w",
        "Último mês": "qdr:m",
        "Último ano": "qdr:y"
    }
    
    selected_time = st.selectbox("Período", options=list(time_options.keys()), index=0)
    
    # Número de resultados
    num_results = st.slider("Número de resultados", min_value=5, max_value=30, value=20, step=5)
    
    # Botão para realizar a busca
    search_button = st.button(
        "🔍 Buscar Produtos", 
        type="primary", 
        use_container_width=True
    )

    # Seção de informações
    st.divider()
    st.markdown("""
    ### Sobre
    Este aplicativo utiliza a API Serper para buscar produtos 
    através do Google Shopping. A busca retorna produtos 
    baseados nos parâmetros configurados.
    
    Desenvolvido como parte do projeto MCP Server Serper.
    """)

# Cabeçalho principal
st.markdown(
    "<div class='header-container'><h1>🛍️ Busca de Produtos - Serper API</h1>"
    "<p>Busque e visualize produtos com a API Serper integrada ao Google Shopping</p></div>", 
    unsafe_allow_html=True
)

# Realizar busca quando o botão for pressionado
if search_button or 'last_results' in st.session_state:
    if search_button or 'last_results' not in st.session_state:
        # Obter parâmetros da região selecionada
        region_params = region_options[selected_region]
        
        # Filtro de tempo
        tbs = time_options[selected_time]
        
        # Mostrar spinner durante a busca
        with st.spinner(f'Buscando produtos relacionados a "{query}"...'):
            # Realizar a busca de produtos
            results = search_shopping(
                query=query,
                location=region_params["location"],
                gl=region_params["gl"],
                hl=region_params["hl"],
                num=num_results,
                tbs=tbs
            )
            
            # Armazenar os resultados na sessão
            st.session_state.last_results = results
            st.session_state.last_query = query
    else:
        # Usar resultados da sessão
        results = st.session_state.last_results
        query = st.session_state.last_query
    
    # Verificar se houve erro
    if "error" in results:
        st.error(f"⚠️ {results['error']}")
        if "raw" in results:
            with st.expander("Detalhes do erro"):
                st.code(results["raw"])
    
    # Exibir resultados
    else:
        # Extrair produtos
        shopping_items = results.get("shopping", [])
        
        # Informações sobre a busca
        if shopping_items:
            # Exibir número de resultados
            result_info = (
                f"<div class='results-info'><h3>Encontrados {len(shopping_items)} "
                f"produtos relacionados a \"{query}\""
            )
            
            # Exibir informações de créditos se disponível
            if "credits" in results:
                result_info += (
                    f" <span class='credits-info'>Créditos utilizados: "
                    f"{results['credits']}</span>"
                )
            
            result_info += "</h3></div>"
            st.markdown(result_info, unsafe_allow_html=True)
            
            # Exibir parâmetros da busca
            with st.expander("Detalhes da requisição"):
                st.json(results.get("searchParameters", {}))
            
            # Criar grade de 3 colunas para exibir os produtos
            cols = st.columns(3)
            
            # Distribuir produtos entre as colunas
            for i, product in enumerate(shopping_items):
                # Alternando entre as colunas
                col = cols[i % 3]
                
                # Obter dados do produto
                title = html.escape(product.get("title", "Sem título"))
                link = html.escape(product.get("link", "#"))
                price = html.escape(product.get("price", "Preço não disponível"))
                source = html.escape(product.get("source", "Fonte desconhecida"))
                image_url = html.escape(product.get("imageUrl", ""))
                rating = product.get("rating", 0)
                rating_count = product.get("ratingCount", 0)
                delivery = html.escape(product.get("delivery", ""))
                offers = product.get("offers", "")
                
                # Gerar estrelas para avaliação
                stars_html = ""
                if rating:
                    full_stars = int(rating)
                    half_star = rating - full_stars >= 0.5
                    stars_html = "★" * full_stars
                    if half_star:
                        stars_html += "½"
                
                # Renderizar o card do produto usando componentes separados
                with col:
                    with st.container():
                        # Construir HTML de forma mais segura
                        product_html = f"""
                        <div class="product-card">
                        """
                        
                        # Imagem (se disponível)
                        if image_url:
                            product_html += f'<img src="{image_url}" class="product-image">'
                        
                        # Título e link
                        product_html += f'<a href="{link}" target="_blank" class="product-title">{title}</a>'
                        
                        # Fonte
                        product_html += f'<div class="product-source">{source}</div>'
                        
                        # Preço
                        product_html += f'<div class="product-price">{price}</div>'
                        
                        # Informações de entrega (se disponível)
                        if delivery:
                            product_html += f'<div class="product-delivery">{delivery}</div>'
                        
                        # Avaliação com estrelas (se disponível)
                        if stars_html:
                            product_html += f'<div class="product-rating">{stars_html}</div>'
                        
                        # Número de avaliações (se disponível)
                        if rating_count:
                            product_html += f'<div class="product-reviews">{rating_count} avaliações</div>'
                        
                        # Ofertas disponíveis (se disponível)
                        if offers:
                            product_html += f'<div class="product-reviews">{offers} ofertas disponíveis</div>'
                        
                        # Link para o produto
                        product_html += f'<a href="{link}" target="_blank" class="product-link">Ver produto →</a>'
                        
                        # Fechar div do card
                        product_html += "</div>"
                        
                        # Renderizar HTML
                        st.markdown(product_html, unsafe_allow_html=True)
        else:
            st.info(f"Nenhum produto encontrado para '{query}' com os parâmetros selecionados.")

# Mensagem inicial quando nenhuma busca foi realizada
else:
    st.info("👈 Configure os parâmetros e clique em 'Buscar Produtos' para começar.")
    
    # Exibir exemplos de termos de busca
    st.markdown("""
    ### Exemplos de termos para busca:
    - smartphone
    - notebook
    - tênis esportivo
    - fone de ouvido bluetooth
    - monitor ultrawide
    - máquina de café
    - smartwatch
    """) 