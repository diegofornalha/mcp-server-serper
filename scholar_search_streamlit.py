#!/usr/bin/env python3

"""
Aplicativo Streamlit para busca acadêmica (scholar) usando a API Serper.
Permite visualizar resultados acadêmicos com diferentes parâmetros de busca.
"""

import os
import json
import http.client
import streamlit as st
from dotenv import load_dotenv
import html

# Carregar variáveis de ambiente
load_dotenv()

# Configurar a página do Streamlit
st.set_page_config(
    page_title="Busca Acadêmica - Serper API",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilo CSS personalizado
st.markdown("""
<style>
    .result-card {
        background-color: #f9f9f9;
        border-radius: 10px;
        padding: 15px;
        margin-bottom: 20px;
        border-left: 5px solid #4285F4;
        box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    }
    .publication-title {
        color: #1a0dab;
        font-size: 18px;
        font-weight: 600;
        margin-bottom: 10px;
        text-decoration: none;
    }
    .publication-title:hover {
        text-decoration: underline;
    }
    .publication-info {
        color: #006621;
        font-size: 14px;
        margin-bottom: 8px;
    }
    .publication-year {
        color: #545454;
        font-size: 14px;
        margin-bottom: 8px;
    }
    .cited-by {
        color: #545454;
        font-size: 14px;
        font-style: italic;
        margin-bottom: 8px;
    }
    .publication-snippet {
        color: #545454;
        font-size: 14px;
        margin-bottom: 12px;
    }
    .pdf-link {
        background-color: #f8f9fa;
        border: 1px solid #dadce0;
        border-radius: 4px;
        color: #1a73e8;
        display: inline-block;
        font-size: 14px;
        font-weight: 500;
        margin-top: 10px;
        padding: 5px 10px;
        text-decoration: none;
    }
    .pdf-link:hover {
        background-color: #e8f0fe;
        text-decoration: none;
    }
    .credit-counter {
        margin-top: 20px;
        font-size: 14px;
        color: #70757a;
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


# Função para buscar artigos acadêmicos usando a API Serper
def search_scholar(query, location="United States", gl="us", hl="en", num=10, time_period=None):
    """
    Busca artigos acadêmicos usando a API Serper.
    
    Args:
        query: Termo de busca
        location: Localização geográfica
        gl: Código de região do Google
        hl: Código de idioma
        num: Número de resultados
        time_period: Filtro de tempo (qdr:h, qdr:d, qdr:w, qdr:m, qdr:y)
        
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
            "type": "scholar"
        }
        
        # Adicionar filtro de tempo se especificado
        if time_period:
            payload["tbs"] = time_period
        
        # Cabeçalhos da requisição
        headers = {
            'X-API-KEY': SERPER_API_KEY,
            'Content-Type': 'application/json'
        }
        
        # Fazer a requisição POST
        conn.request('POST', '/scholar', json.dumps(payload), headers)
        
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
    st.header("📚 Configurações da Busca")
    
    # Campo de busca
    query = st.text_input("Termo de busca", value="inteligência artificial")
    
    # Seleção de região
    regions = {
        "Brasil": {"gl": "br", "hl": "pt-br", "location": "Brasil"},
        "Estados Unidos": {"gl": "us", "hl": "en", "location": "United States"},
        "Reino Unido": {"gl": "gb", "hl": "en", "location": "United Kingdom"},
        "Espanha": {"gl": "es", "hl": "es", "location": "España"},
        "França": {"gl": "fr", "hl": "fr", "location": "France"},
        "Alemanha": {"gl": "de", "hl": "de", "location": "Deutschland"},
        "Japão": {"gl": "jp", "hl": "ja", "location": "日本"},
        "Austrália": {"gl": "au", "hl": "en", "location": "Australia"},
        "Canadá": {"gl": "ca", "hl": "en", "location": "Canada"},
        "Índia": {"gl": "in", "hl": "en", "location": "India"}
    }
    
    selected_region = st.selectbox("Região", options=list(regions.keys()), index=0)
    region_info = regions[selected_region]
    
    # Filtro de tempo
    time_filters = {
        "Qualquer período": None,
        "Última hora": "qdr:h",
        "Último dia": "qdr:d",
        "Última semana": "qdr:w",
        "Último mês": "qdr:m",
        "Último ano": "qdr:y"
    }
    
    selected_time = st.selectbox("Período", options=list(time_filters.keys()), index=0)
    time_period = time_filters[selected_time]
    
    # Número de resultados
    num_results = st.slider("Número de resultados", min_value=1, max_value=30, value=10, step=1)
    
    # Botão para realizar a busca
    search_button = st.button(
        "🔍 Buscar Artigos", 
        type="primary", 
        use_container_width=True
    )

    # Seção de informações
    st.divider()
    st.markdown("""
    ### Sobre
    Este aplicativo utiliza a API Serper para buscar 
    publicações acadêmicas através do Google Scholar. 
    A busca retorna artigos, livros e outras publicações
    científicas baseadas nos parâmetros configurados.
    
    Desenvolvido como parte do projeto MCP Server Serper.
    """)

# Cabeçalho principal
st.markdown(
    "<div class='header-container'><h1>📚 Busca Acadêmica - Serper API</h1>"
    "<p>Busque e visualize artigos e publicações acadêmicas com a API Serper integrada ao Google Scholar</p></div>", 
    unsafe_allow_html=True
)

# Realizar busca quando o botão for pressionado
if search_button or 'last_results' in st.session_state:
    if search_button or 'last_results' not in st.session_state:
        # Obter parâmetros da região selecionada
        region_params = region_info
        
        # Filtro de tempo
        tbs = time_period
        
        # Mostrar spinner durante a busca
        with st.spinner(f'Buscando publicações acadêmicas sobre "{query}"...'):
            # Realizar a busca acadêmica
            results = search_scholar(
                query=query,
                location=region_params["location"],
                gl=region_params["gl"],
                hl=region_params["hl"],
                num=num_results,
                time_period=tbs
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
        # Extrair artigos acadêmicos
        organic_items = results.get("organic", [])
        
        # Informações sobre a busca
        if organic_items:
            # Exibir número de resultados
            result_info = (
                f"<div class='results-info'><h3>Encontrados {len(organic_items)} "
                f"resultados acadêmicos sobre \"{query}\""
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
            
            # Exibir os artigos acadêmicos
            for item in organic_items:
                # Obter dados do artigo com escape de caracteres HTML
                title = html.escape(item.get("title", "Sem título"))
                link = html.escape(item.get("link", "#"))
                publication_info = html.escape(item.get("publicationInfo", "Informação não disponível"))
                snippet = html.escape(item.get("snippet", ""))
                year = item.get("year", "")
                cited_by = item.get("citedBy", 0)
                pdf_url = html.escape(item.get("pdfUrl", ""))
                
                # Construir HTML de forma segura
                scholar_html = "<div class='result-card'>"
                
                # Título e link
                scholar_html += f'<a href="{link}" target="_blank" class="publication-title">{title}</a>'
                
                # Informações da publicação e ano
                scholar_html += f'<div class="publication-info">{publication_info}'
                if year:
                    scholar_html += f'<div class="publication-year">Publicado em: {year}</div>'
                scholar_html += '</div>'
                
                # Citações
                if cited_by:
                    scholar_html += f'<div class="cited-by">Citado por: {cited_by} publicações</div>'
                
                # Snippet
                if snippet:
                    scholar_html += f'<div class="publication-snippet">{snippet}</div>'
                
                # Links
                scholar_html += f'<a href="{link}" target="_blank" class="pdf-link">Ver publicação →</a>'
                
                # Link para PDF se disponível
                if pdf_url:
                    scholar_html += f'<a href="{pdf_url}" target="_blank" class="pdf-link">📄 Download PDF</a>'
                
                # Fechar div do card
                scholar_html += "</div>"
                
                # Renderizar HTML
                st.markdown(scholar_html, unsafe_allow_html=True)
        else:
            st.info(f"Nenhuma publicação acadêmica encontrada para '{query}' com os parâmetros selecionados.")

# Mensagem inicial quando nenhuma busca foi realizada
else:
    st.info("👈 Configure os parâmetros e clique em 'Buscar Artigos' para começar.")
    
    # Exibir exemplos de termos de busca
    st.markdown("""
    ### Exemplos de termos para busca:
    - inteligência artificial
    - machine learning
    - ciência de dados
    - teoria dos grafos
    - algoritmos genéticos
    - análise de sentimentos
    - processamento de linguagem natural
    """)

# Rodapé
st.sidebar.markdown("---")
st.sidebar.markdown("### Sobre este aplicativo")
st.sidebar.markdown("""
Este aplicativo utiliza a API Serper para realizar buscas no Google Scholar e exibir os resultados em um formato amigável.

Cada busca consome créditos da sua conta na API Serper.
""")

if __name__ == "__main__":
    # O Streamlit executa todo o script em todas as interações,
    # então não é necessário um loop principal explícito
    pass 