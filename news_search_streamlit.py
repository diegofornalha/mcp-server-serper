#!/usr/bin/env python3

"""
Aplicativo Streamlit para busca de notícias usando a API Serper.
Permite visualizar resultados de notícias com diferentes parâmetros de busca.
"""

import os
import json
import http.client
import streamlit as st
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# Configurações da página Streamlit
st.set_page_config(
    page_title="Busca de Notícias - Serper API",
    page_icon="📰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos CSS personalizados
st.markdown("""
<style>
    .news-card {
        border: 1px solid #ddd;
        border-radius: 8px;
        padding: 15px;
        margin-bottom: 15px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        background-color: white;
    }
    .news-title {
        color: #1E88E5;
        text-decoration: none;
        font-weight: bold;
        font-size: 18px;
        margin-bottom: 8px;
    }
    .news-source {
        color: #616161;
        font-size: 14px;
        margin-bottom: 8px;
    }
    .news-date {
        color: #616161;
        font-size: 13px;
        margin-bottom: 8px;
    }
    .news-snippet {
        color: #212121;
        font-size: 14px;
        margin-bottom: 10px;
    }
    .news-link {
        color: #1976D2;
        font-size: 13px;
        text-decoration: none;
    }
    .news-image {
        max-width: 100%;
        height: auto;
        border-radius: 4px;
        margin-bottom: 10px;
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

# Função para buscar notícias usando a API Serper
def search_news(query, location="Brazil", gl="br", hl="pt-br", num=10, tbs=None):
    """
    Busca notícias usando a API Serper.
    
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
            "num": num
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
        conn.request('POST', '/news', json.dumps(payload), headers)
        
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

# Interface da Barra Lateral
with st.sidebar:
    st.header("📰 Configurações da Busca")
    
    # Campo de busca
    query = st.text_input("Termo de busca", value="inteligência artificial")
    
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
    num_results = st.slider("Número de resultados", min_value=1, max_value=20, value=10, step=1)
    
    # Botão para realizar a busca
    search_button = st.button(
        "🔍 Buscar Notícias", 
        type="primary", 
        use_container_width=True
    )

    # Seção de informações
    st.divider()
    st.markdown("""
    ### Sobre
    Este aplicativo utiliza a API Serper para buscar notícias 
    através do Google. A busca retorna notícias recentes 
    baseadas nos parâmetros configurados.
    
    Desenvolvido como parte do projeto MCP Server Serper.
    """)

# Cabeçalho principal
st.markdown(
    "<div class='header-container'><h1>📰 Busca de Notícias - Serper API</h1>"
    "<p>Busque e visualize as notícias mais recentes com a API Serper</p></div>", 
    unsafe_allow_html=True
)

# Realizar busca quando o botão for pressionado
if search_button or 'last_results' in st.session_state:
    if search_button or not 'last_results' in st.session_state:
        # Obter parâmetros da região selecionada
        region_params = region_options[selected_region]
        
        # Filtro de tempo
        tbs = time_options[selected_time]
        
        # Mostrar spinner durante a busca
        with st.spinner(f'Buscando notícias sobre "{query}"...'):
            # Realizar a busca de notícias
            results = search_news(
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
        # Extrair notícias
        news_items = results.get("news", [])
        
        # Informações sobre a busca
        if news_items:
            st.markdown(
                f"<div class='results-info'><h3>Encontradas {len(news_items)} "
                f"notícias sobre \"{query}\"</h3></div>", 
                unsafe_allow_html=True
            )
            
            # Exibir parâmetros da busca
            with st.expander("Detalhes da requisição"):
                st.json(results.get("searchParameters", {}))
            
            # Criar grade de 2 colunas para exibir as notícias
            col1, col2 = st.columns(2)
            
            # Distribuir notícias entre as colunas
            for i, news in enumerate(news_items):
                # Alternando entre as colunas
                col = col1 if i % 2 == 0 else col2
                
                # Obter dados da notícia
                title = news.get("title", "Sem título")
                link = news.get("link", "#")
                date = news.get("date", "Data não disponível")
                source = news.get("source", "Fonte desconhecida")
                snippet = news.get("snippet", "")
                image_url = news.get("imageUrl", "")
                
                # Renderizar o card da notícia
                with col:
                    with st.container():
                        st.markdown(f"""
                        <div class="news-card">
                            <a href="{link}" target="_blank" class="news-title">{title}</a>
                            <div class="news-source">{source}</div>
                            <div class="news-date">{date}</div>
                            {"<img src='" + image_url + "' class='news-image'>" if image_url else ""}
                            <div class="news-snippet">{snippet}</div>
                            <a href="{link}" target="_blank" class="news-link">Ler notícia completa →</a>
                        </div>
                        """, unsafe_allow_html=True)
        else:
            st.info(f"Nenhuma notícia encontrada para '{query}' com os parâmetros selecionados.")

# Mensagem inicial quando nenhuma busca foi realizada
else:
    st.info("👈 Configure os parâmetros e clique em 'Buscar Notícias' para começar.")
    
    # Exibir exemplos de termos de busca
    st.markdown("""
    ### Exemplos de termos para busca:
    - inteligência artificial
    - ciência de dados
    - tecnologia quântica
    - multiagentes em IA
    - metaverso
    - criptomoedas
    """) 