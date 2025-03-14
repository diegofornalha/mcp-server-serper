#!/usr/bin/env python3

"""
Aplicativo Streamlit para visualizar resultados de busca de imagens da API Serper.
"""

import os
import json
import http.client
import streamlit as st
from PIL import Image
from io import BytesIO
import requests
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
    st.warning("⚠️ Chave da API Serper não encontrada. Configure a variável de ambiente SERPER_API_KEY ou crie um arquivo .env.")
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

def load_image_from_url(url):
    """
    Carrega uma imagem a partir de uma URL
    
    Args:
        url: URL da imagem
        
    Returns:
        Objeto de imagem ou None se falhar
    """
    try:
        response = requests.get(url, timeout=5)
        image = Image.open(BytesIO(response.content))
        return image
    except Exception:
        return None

def main():
    """Função principal do aplicativo Streamlit."""
    
    # Configurações da página
    st.set_page_config(
        page_title="Busca de Imagens - Serper API",
        page_icon="🖼️",
        layout="wide"
    )
    
    # Título e cabeçalho
    st.title("🖼️ Visualizador de Busca de Imagens")
    st.markdown(
        """
        Pesquise imagens usando a API Serper e visualize os resultados.
        Este aplicativo demonstra a integração com a [API Serper](https://serper.dev/) para busca de imagens.
        """
    )
    
    # Barra lateral para configurações de busca
    with st.sidebar:
        st.header("Configurações da Busca")
        
        # Campo de busca
        query = st.text_input("Termo de busca", value="")
        
        # Configurações regionais
        col1, col2 = st.columns(2)
        with col1:
            gl = st.selectbox(
                "Região",
                options=["br", "us", "uk", "ca", "au", "in", "de", "fr", "es", "it", "jp"],
                format_func=lambda x: {"br": "Brasil", "us": "EUA", "uk": "Reino Unido", 
                                       "ca": "Canadá", "au": "Austrália", "in": "Índia",
                                       "de": "Alemanha", "fr": "França", "es": "Espanha",
                                       "it": "Itália", "jp": "Japão"}[x],
                index=0
            )
        
        with col2:
            hl = st.selectbox(
                "Idioma",
                options=["pt-br", "en", "es", "fr", "de", "it", "ja"],
                format_func=lambda x: {"pt-br": "Português", "en": "Inglês", "es": "Espanhol", 
                                       "fr": "Francês", "de": "Alemão", "it": "Italiano", 
                                       "ja": "Japonês"}[x],
                index=0
            )
        
        # Localização
        location = st.text_input("Localização", value="Brazil")
        
        # Número de resultados
        num_results = st.slider("Número de resultados", min_value=5, max_value=50, value=10, step=5)
        
        # Botão de busca
        search_button = st.button("🔍 Buscar Imagens", type="primary")
        
        st.divider()
        
        # Informações adicionais
        st.markdown("""
        ### Sobre
        
        Este aplicativo usa a API Serper para buscar imagens no Google.
        
        **Desenvolvido com:**
        - Streamlit
        - Serper API
        - Python
        
        [Ver documentação da API](https://serper.dev/docs)
        """)
    
    # Tela principal - Resultados da busca
    if search_button and query:
        with st.spinner(f"Buscando imagens para: '{query}'..."):
            results = search_images(query, location, gl, hl, num_results)
        
        if "error" in results:
            st.error(f"Erro ao realizar a busca: {results['error']}")
            if "raw" in results:
                with st.expander("Detalhes do erro"):
                    st.code(results["raw"])
        elif not results.get("images"):
            st.warning(f"Nenhuma imagem encontrada para '{query}'")
        else:
            # Exibir parâmetros da busca
            with st.expander("Parâmetros da Busca"):
                st.json(results.get("searchParameters", {}))
            
            # Exibir resultados
            st.subheader(f"Resultados para: '{query}'")
            st.write(f"Encontradas {len(results.get('images', []))} imagens")
            
            # Criar grid para as imagens - 3 por linha
            cols = st.columns(3)
            
            # Exibir cada imagem em um card
            for i, image in enumerate(results.get("images", [])):
                with cols[i % 3]:
                    st.markdown(f"**{html.escape(image.get('title', 'Sem título'))}**")
                    
                    # Exibir a imagem
                    st.image(
                        image.get('thumbnailUrl', ''), 
                        use_column_width=True,
                        caption=f"Fonte: {image.get('source', 'Desconhecida')}"
                    )
                    
                    # Informações adicionais
                    st.markdown(f"**Dimensões:** {image.get('imageWidth', '?')}x{image.get('imageHeight', '?')}")
                    
                    # Links
                    col1, col2 = st.columns(2)
                    with col1:
                        st.markdown(f"[Ver página]({image.get('link', '#')})")
                    with col2:
                        st.markdown(f"[Ver imagem]({image.get('imageUrl', '#')})")
                    
                    st.divider()
    elif not query and search_button:
        st.warning("Por favor, insira um termo de busca.")
    else:
        # Mensagem inicial quando nenhuma busca foi realizada
        st.info("👈 Configure os parâmetros de busca na barra lateral e clique em 'Buscar Imagens' para visualizar os resultados.")
        
        # Imagem exemplo
        st.image("https://serper.dev/images/hero.png", caption="API Serper - Busca de imagens")
        
        # Instruções de uso
        st.markdown("""
        ## Como usar
        
        1. Digite sua consulta de busca no campo apropriado
        2. Ajuste os parâmetros de região e idioma, se necessário
        3. Selecione o número de resultados desejado usando o controle deslizante
        4. Clique em "Buscar Imagens"
        5. Navegue pelos resultados exibidos na grade de imagens
        
        ## Recursos
        
        - **Visualização em grade**: Veja múltiplas imagens em um layout organizado
        - **Detalhes da imagem**: Veja título, fonte e dimensões de cada imagem
        - **Links diretos**: Acesse facilmente a página original ou a imagem em tamanho completo
        - **Personalização da busca**: Configure a região, idioma e quantidade de resultados
        """)

if __name__ == "__main__":
    main() 