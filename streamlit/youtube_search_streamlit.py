#!/usr/bin/env python3

"""
Aplicativo Streamlit para busca de vídeos do YouTube usando a API Serper.
Permite visualizar resultados de vídeos com diferentes parâmetros de busca.
"""

import os
import json
import http.client
import streamlit as st
import html
import requests
import re
import urllib.parse
from typing import List
import base64
from pathlib import Path

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

# Configurações da página Streamlit
st.set_page_config(
    page_title="Agente de IA - Videos",
    page_icon="🎬",
    layout="wide",
    initial_sidebar_state="collapsed",  # Começa com a barra lateral fechada como no app HTTP
    menu_items={
        'About': "Agente de IA Videos usando a API Serper"
    }
)

# Definir o tema para claro de forma mais robusta
st.markdown("""
<script>
    // Forçar tema claro
    localStorage.setItem('theme', '"light"');
    
    // Aplicar tema claro imediatamente
    document.documentElement.dataset.theme = "light";
    
    // Observar mudanças no DOM e garantir que o tema permaneça claro
    const observer = new MutationObserver(function() {
        document.documentElement.dataset.theme = "light";
        
        // Encontrar e modificar elementos específicos do Streamlit
        const themeElements = document.querySelectorAll('[data-baseweb="select"] span, .sidebar .sidebar-content');
        themeElements.forEach(el => {
            el.dataset.theme = "light";
        });
    });
    
    observer.observe(document.body, { childList: true, subtree: true });
    
    // Garantir que o tema não mude após o carregamento completo
    window.addEventListener('load', function() {
        document.documentElement.dataset.theme = "light";
    });
</script>
""", unsafe_allow_html=True)

# Adicionar CSS para forçar o tema claro
st.markdown("""
<style>
    /* Forçar tema claro */
    html[data-theme="dark"] {
        filter: none !important;
        background-color: #f0f2f6 !important;
        color: #262730 !important;
    }
    
    /* Cores de tema claro para elementos principais */
    .main {
        background-color: #f0f2f6 !important;
        color: #262730 !important;
    }
    
    /* Texto preto para labels e texto principal */
    label, .stMarkdown p, .stAlert p, .stMarkdown li {
        color: black !important;
        font-weight: 500 !important;
    }
    
    /* Labels dos controles específicos em preto */
    .stTextInput label, .stSlider label, .stSelectbox label {
        color: black !important;
        font-weight: 500 !important;
    }
    
    /* Cor de texto para o painel info */
    .stAlert.stInfo {
        color: black !important;
    }
    
    .stAlert.stInfo > div:first-child {
        background-color: #d7e9f7 !important;
        color: black !important;
    }
    
    /* Texto dentro do alerta info em preto */
    .stAlert.stInfo p, .stAlert.stInfo h2, .stAlert.stInfo h3 {
        color: black !important;
    }
    
    /* Estilização específica para a barra de busca e campos de entrada */
    .stTextInput > div > div {
        background-color: white !important;
        color: #262730 !important;
        border-radius: 4px !important;
    }
    
    .stTextInput input {
        background-color: white !important;
        color: #262730 !important;
        border: 1px solid #cccccc !important;
        border-radius: 4px !important;
    }
    
    /* Estilização para caixas de seleção, sliders e outros controles */
    .stSlider, .stSelectbox {
        background-color: transparent !important;
    }
    
    .stSlider > div, .stSelectbox > div {
        background-color: transparent !important;
    }
    
    /* Ajustar cores do slider para vermelho */
    .stSlider [data-baseweb="slider"] {
        margin-top: 1rem !important;
    }
    
    .stSlider [data-baseweb="slider"] div[role="slider"] {
        background-color: #FF0000 !important;
        border-color: #FF0000 !important;
    }
    
    .stSlider [data-baseweb="slider"] div[data-testid="stThumbValue"] {
        color: #FF0000 !important;
        font-weight: bold !important;
    }
    
    .stSlider [data-baseweb="slider"] div[role="progressbar"] {
        background-color: #FF0000 !important;
    }
    
    /* Estilização para o placeholder nos campos de entrada */
    input::placeholder {
        color: #8e8e8e !important;
        opacity: 0.8 !important;
    }
    
    /* Tema claro para todos os widgets e controles Streamlit */
    div.stNumberInput, div.stTextInput, div.stDateInput, div.stTimeInput, div.stSelectbox, div.stMultiselect {
        background-color: transparent !important;
    }
    
    /* Cor de texto para elementos de entrada */
    input, textarea, [data-baseweb="select"] span {
        color: #262730 !important;
    }
    
    /* Cores para cabeçalhos e links */
    h1, h2, h3, h4, h5, h6, a {
        color: #262730 !important;
    }
    
    /* Exceção para o título principal que deve manter a cor definida */
    h1.youtube-title {
        color: white !important;
    }
    
    /* Estilização para o painel info (azul claro) */
    .stAlert.stInfo {
        background-color: #d7e9f7 !important;
        border: none !important;
        border-radius: 8px !important;
    }
    
    /* Cor de fundo para caixas de código e outras áreas */
    .stCodeBlock {
        background-color: #f6f6f6 !important;
    }
    
    /* Garante que toda a aplicação tenha fundo claro */
    .stApp {
        background-color: #f0f2f6 !important;
    }
</style>
""", unsafe_allow_html=True)

# Estilos CSS personalizados mais parecidos com o app HTTP
st.markdown("""
<style>
    .main .block-container {
        padding-top: 1rem;
        padding-bottom: 1rem;
        padding-left: 1rem;
        padding-right: 1rem;
        max-width: 1200px;
    }
    
    h1 {
        color: white;
        background-color: #FF0000;
        padding: 1rem;
        border-radius: 8px;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    
    .search-panel {
        background-color: white;
        padding: 1.5rem;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
        margin-bottom: 1.5rem;
    }
    
    .content-panel {
        background-color: white;
        padding: 1.5rem;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
    }
    
    .stButton > button {
        background-color: #FF0000;
        color: white;
        border: none;
        padding: 0.5rem 1rem;
        border-radius: 4px;
        font-weight: bold;
        cursor: pointer;
    }
    
    .stButton > button:hover {
        background-color: #CC0000;
    }
    
    .video-card {
        border: 1px solid #ddd;
        border-radius: 8px;
        overflow: hidden;
        transition: transform 0.3s, box-shadow 0.3s;
        background-color: white;
        height: 100%;
    }
    
    .video-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
    }
    
    .video-thumbnail-container {
        position: relative;
        height: 180px;
        background-color: #000;
        overflow: hidden;
    }
    
    .video-info {
        padding: 12px;
    }
    
    .video-title {
        color: #333;
        font-weight: bold;
        font-size: 16px;
        margin-bottom: 8px;
        overflow: hidden;
        text-overflow: ellipsis;
        display: -webkit-box;
        -webkit-line-clamp: 2;
        -webkit-box-orient: vertical;
        height: 42px;
    }
    
    .video-channel {
        color: #666;
        font-size: 13px;
        margin-bottom: 6px;
    }
    
    .video-metadata {
        display: flex;
        justify-content: space-between;
        font-size: 12px;
        color: #666;
    }
    
    .duration-badge {
        position: absolute;
        bottom: 8px;
        right: 8px;
        background-color: rgba(0, 0, 0, 0.8);
        color: white;
        padding: 2px 6px;
        border-radius: 3px;
        font-size: 12px;
        font-weight: 600;
    }
    
    /* Estilos adicionais para thumbnails indisponíveis */
    .video-thumbnail {
        transition: all 0.3s ease;
    }
    
    .video-thumbnail[src*="Preview+Indispon"] {
        filter: brightness(0.9);
        background-color: #000 !important;
        display: flex;
        align-items: center;
        justify-content: center;
        font-family: Arial, sans-serif;
    }
    
    .video-thumbnail[src*="Preview+Indispon"]::before {
        content: "\\e901";
        font-family: "Font Awesome 5 Free";
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        font-size: 2rem;
        color: rgba(255, 0, 0, 0.8);
        z-index: 10;
    }
    
    .video-thumbnail[src*="Preview+Indispon"]::after {
        content: "Pré-visualização indisponível";
        position: absolute;
        top: 60%;
        left: 50%;
        transform: translateX(-50%);
        color: white;
        font-size: 12px;
        font-weight: bold;
        text-align: center;
        width: 90%;
        background-color: rgba(0, 0, 0, 0.7);
        padding: 4px;
        border-radius: 4px;
    }
    
    footer {
        margin-top: 30px;
        text-align: center;
        padding: 20px;
        color: #666;
        font-size: 14px;
    }
</style>
""", unsafe_allow_html=True)

# Função para converter imagem para Base64
def get_base64_image(image_path):
    """
    Converte uma imagem em uma string base64 para uso em HTML/CSS.
    
    Args:
        image_path: Caminho para a imagem
        
    Returns:
        String base64 da imagem
    """
    try:
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except Exception as e:
        print(f"Erro ao ler imagem {image_path}: {str(e)}")
        return ""

# Carregar a imagem do Instagram em base64
instagram_image_path = os.path.join(os.path.dirname(__file__), "static", "instagram.jpg")
INSTAGRAM_IMAGE_BASE64 = get_base64_image(instagram_image_path)

# Definir URL de fallback para Instagram (com base64 se disponível ou link externo)
if INSTAGRAM_IMAGE_BASE64:
    INSTAGRAM_FALLBACK_URL = f"data:image/jpeg;base64,{INSTAGRAM_IMAGE_BASE64}"
else:
    # Fallback para uma URL online caso a imagem local não seja encontrada
    INSTAGRAM_FALLBACK_URL = "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e7/Instagram_logo_2016.svg/1200px-Instagram_logo_2016.svg.png"

# Função para extrair ID do YouTube da URL
def extract_youtube_id(url):
    """Extrai o ID do YouTube de uma URL."""
    if not url:
        return None
    
    # Padrão para URLs do YouTube
    yt_patterns = [
        r"youtube\.com/watch\?v=([a-zA-Z0-9_-]+)",
        r"youtu\.be/([a-zA-Z0-9_-]+)",
        r"youtube\.com/embed/([a-zA-Z0-9_-]+)",
        r"youtube\.com/shorts/([a-zA-Z0-9_-]+)",  # Para shorts
        r"youtube\.com/v/([a-zA-Z0-9_-]+)",  # Outro formato
        r"youtube\.com/\?v=([a-zA-Z0-9_-]+)"  # Variante da URL
    ]
    
    for pattern in yt_patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
            
    # Tenta extrair se houver um parâmetro v= em qualquer lugar da URL
    match = re.search(r"[?&]v=([a-zA-Z0-9_-]+)", url)
    if match:
        return match.group(1)
    
    return None

def search_videos(query, location="Brazil", gl="br", hl="pt-br", 
                num=20, tbs=None):
    """
    Busca vídeos do YouTube usando a API Serper.
    
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
        
        # Adicionar filtro de tempo se fornecido
        if tbs:
            payload["tbs"] = tbs
        
        headers = {
            'X-API-KEY': SERPER_API_KEY,
            'Content-Type': 'application/json'
        }
        
        # Enviar requisição
        conn.request('POST', '/videos', json.dumps(payload), headers)
        
        # Receber resposta
        response = conn.getresponse()
        data = response.read()
        
        # Verificar erro
        if response.status != 200:
            return {
                "error": f"Erro na API: {response.status} {response.reason}", 
                "raw": data.decode('utf-8')
            }
            
        # Processar resposta
        return json.loads(data.decode('utf-8'))
    except Exception as e:
        return {"error": f"Erro na requisição: {str(e)}"}
    finally:
        conn.close()


def format_views(views_text):
    """Formata o texto de visualizações para exibição mais amigável."""
    if not views_text:
        # Retorna string vazia em vez de "Visualizações indisponíveis"
        return ""  
    return views_text.replace(" visualizações", "").replace("views", "")


def format_upload_date(date_text):
    """Formata a data de upload para exibição mais amigável."""
    if not date_text:
        return ""
    return date_text


def get_thumbnail_url(video):
    """
    Obtém a URL da thumbnail do vídeo, com múltiplos fallbacks.
    
    Args:
        video: Objeto do vídeo retornado pela API
        
    Returns:
        URL da thumbnail ou URL de fallback
    """
    video_link = video.get('link', '')
    
    # Verificar se é um vídeo do Instagram
    is_instagram = "instagram.com" in video_link.lower()
    
    if is_instagram:
        # Usar a imagem do Instagram em base64 ou a URL externa de fallback
        return INSTAGRAM_FALLBACK_URL
    
    # Para vídeos do YouTube e outros
    video_id = extract_youtube_id(video_link)
    
    if video_id:
        # Tentar vários formatos de thumbnail disponíveis no YouTube
        # em ordem decrescente de qualidade, mas que sejam mais prováveis de existir
        return f"https://i.ytimg.com/vi/{video_id}/hqdefault.jpg"
    
    # Se não conseguir extrair o ID, tentar usar a URL fornecida pela API
    thumbnail_url = video.get('thumbnailUrl', '')
    
    # Se ainda não tiver URL, tentar obter da propriedade do vídeo
    if not thumbnail_url and 'richSnippet' in video and 'videoobject' in video['richSnippet']:
        thumbnail_url = video['richSnippet']['videoobject'].get('thumbnailurl', '')
    
    # Se ainda não tiver URL, retornar uma imagem de fallback
    if not thumbnail_url:
        # Usando uma URL customizada do via.placeholder com design profissional
        return "https://via.placeholder.com/480x360/000000/FFFFFF?text=Preview+Indispon%C3%ADvel"
    
    return thumbnail_url


def render_video_card(video):
    """
    Renderiza o card de um vídeo com tratamento para falhas de carregamento.
    
    Args:
        video: Objeto do vídeo a ser renderizado
        
    Returns:
        HTML do card de vídeo
    """
    # Determinar a plataforma do vídeo
    video_link = video.get('link', '#')
    is_instagram = "instagram.com" in video_link.lower()
    is_youtube = "youtube.com" in video_link.lower() or "youtu.be" in video_link.lower()
    
    # Definir badge de plataforma
    if is_instagram:
        platform_badge = '<div class="platform-badge instagram">Instagram</div>'
        platform_class = "instagram-card"
    elif is_youtube:
        platform_badge = '<div class="platform-badge youtube">YouTube</div>'
        platform_class = "youtube-card"
    else:
        platform_badge = '<div class="platform-badge other">Outro</div>'
        platform_class = "other-card"
    
    # Obter URL da thumbnail com fallback
    thumbnail_url = get_thumbnail_url(video)
    
    # Informações do vídeo
    video_title = html.escape(video.get('title', 'Sem título'))
    video_channel = html.escape(video.get('channel', 'Canal desconhecido'))
    duration = video.get('duration', 'N/A')
    views = format_views(video.get('views', ''))
    upload_date = format_upload_date(video.get('uploadDate', ''))
    
    # Definir imagem de fallback conforme plataforma
    if is_instagram:
        fallback_img = INSTAGRAM_FALLBACK_URL
        fallback_text = "Instagram+V%C3%ADdeo"
    else:
        fallback_img = "https://via.placeholder.com/480x360/000000/FFFFFF"
        fallback_text = "Preview+Indispon%C3%ADvel"
    
    # Melhorar o script de tratamento de erro para thumbnail
    # com estilização e mensagem mais amigável
    onerror_script = (
        "this.onerror=null;" +
        f"this.src='{fallback_img}?text={fallback_text}';" +
        "this.style.backgroundColor='#000';" +
        "this.style.opacity='0.8';" +
        "this.style.border='1px solid #333';" +
        "console.log('Erro ao carregar thumbnail, usando fallback personalizado');"
    )
    
    button_style = (
        "background-color: #FF0000; color: white; border: none; " +
        "padding: 6px 12px; margin-top: 8px; border-radius: 4px; " +
        "cursor: pointer; width: 100%;"
    )
    
    # Personalizar estilo do botão para Instagram
    if is_instagram:
        button_style = (
            "background: linear-gradient(45deg, #405DE6, #5851DB, #833AB4, #C13584, #E1306C, #FD1D1D); " +
            "color: white; border: none; " +
            "padding: 6px 12px; margin-top: 8px; border-radius: 4px; " +
            "cursor: pointer; width: 100%;"
        )
    
    # Construir de forma ainda mais precisa, separando cada elemento
    # Início do card
    card_html = f'<div class="video-card {platform_class}">'
    
    # Seção da thumbnail com overlay de ícone e classe personalizada para indisponíveis
    card_html += '<div class="video-thumbnail-container">'
    card_html += platform_badge
    card_html += f'<img src="{thumbnail_url}" width="100%" height="100%" ' + \
                f'style="object-fit: cover;" ' + \
                f'onerror="{onerror_script}" ' + \
                f'alt="{html.escape(video_title)}" ' + \
                f'class="video-thumbnail">'
    card_html += f'<div class="duration-badge">{duration}</div>'
    card_html += '</div>'
    
    # Seção de informações
    card_html += '<div class="video-info">'
    card_html += f'<div class="video-title">{video_title}</div>'
    
    # Mostrar canal apenas para vídeos que não são do Instagram
    if not is_instagram:
        card_html += f'<div class="video-channel">{video_channel}</div>'
    
    # Metadados
    card_html += '<div class="video-metadata">'
    if views:
        card_html += f'<span>{views}</span>'
    if upload_date:
        card_html += f'<span>{upload_date}</span>'
    card_html += '</div>'
    
    # Botão - usando escape para o link e sem expressões aninhadas
    button_text = "Assistir no Instagram" if is_instagram else "Assistir no YouTube"
    if not (is_instagram or is_youtube):
        button_text = "Ver vídeo"
        
    card_html += f'<a href="{html.escape(video_link)}" target="_blank" style="text-decoration: none;">'
    card_html += f'<button style="{button_style}">{button_text}</button>'
    card_html += '</a>'
    
    # Fechamento
    card_html += '</div>'
    card_html += '</div>'
    card_html += '<br>'
    
    return card_html


def get_search_suggestions(query: str) -> List[str]:
    """
    Obtém sugestões de busca do Google para o termo digitado.
    
    Args:
        query: Termo de busca parcial
        
    Returns:
        Lista de sugestões de busca (até 20 sugestões)
    """
    if not query or len(query) < 2:
        return []
    
    try:
        # Codificar a consulta para URL
        encoded_query = urllib.parse.quote(query)
        
        # URL da API de sugestões do Google (usada pelo YouTube)
        url = f"https://suggestqueries.google.com/complete/search?client=youtube&ds=yt&q={encoded_query}"
        
        # Adicionar parâmetros de região e idioma
        url += "&hl=pt-BR&gl=br"
        
        # Adicionar parâmetro para obter mais sugestões (se suportado)
        url += "&max_suggestions=20"
        
        # Configurar headers para evitar bloqueio
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'application/json, text/javascript, */*; q=0.01',
            'Accept-Language': 'pt-BR,pt;q=0.9,en-US;q=0.8,en;q=0.7',
            'Referer': 'https://www.youtube.com/',
            'Origin': 'https://www.youtube.com'
        }
        
        # Fazer a requisição com os headers
        response = requests.get(url, headers=headers, timeout=5)
        
        # Obter as sugestões (o formato é um array JavaScript)
        if response.status_code == 200:
            # A resposta é algo como: window.google.ac.h(["QUERY", ["SUGESTÃO1","SUGESTÃO2",...]])
            content = response.text
            
            # Extrair as sugestões usando regex para maior robustez
            import re
            pattern = r'\[\s*"[^"]*"\s*,\s*(\[[^\]]*\])'
            match = re.search(pattern, content)
            
            if match:
                suggestions_json = match.group(1)
                # Extrair as strings das sugestões
                suggestions_pattern = r'"([^"]*)"'
                suggestions = re.findall(suggestions_pattern, suggestions_json)
                return suggestions[:20]  # Aumentado de 10 para 20 sugestões
            
            # Fallback para o método anterior se o regex falhar
            elif ",[" in content and "]])" in content:
                suggestions_str = content.split(",[")[1].split("]])[0")
                # Converter string das sugestões em lista
                suggestions = [s.strip('"') for s in suggestions_str.split('","')]
                return suggestions[:20]  # Aumentado de 10 para 20 sugestões
        
        # Fallback: gerar algumas sugestões simples baseadas no query
        return fallback_suggestions(query)
    except Exception as e:
        print(f"Erro ao obter sugestões: {str(e)}")
        # Em caso de erro, retornar algumas sugestões baseadas no query
        return fallback_suggestions(query)

def fallback_suggestions(query: str) -> List[str]:
    """
    Gera sugestões de fallback quando a API falha.
    
    Args:
        query: Termo de busca parcial
        
    Returns:
        Lista de sugestões de busca geradas localmente
    """
    # Base de sugestões para termos comuns
    base_suggestions = {
        "como": ["como fazer", "como funciona", "como usar", "como aprender"],
        "melhor": ["melhores dicas", "melhor tutorial", "melhores práticas", "melhor forma de"],
        "tutorial": ["tutorial para iniciantes", "tutorial passo a passo", "tutorial avançado"],
        "aprend": ["aprender python", "aprender inglês", "aprender a programar", "aprendizado de máquina"],
        "inteligência": ["inteligência artificial", "inteligência artificial para iniciantes", "inteligência emocional"],
        "agente": ["agentes de ia", "agentes inteligentes", "agentes conversacionais", "agentes virtuais"]
    }
    
    # Lista para armazenar sugestões geradas
    suggestions = []
    
    # Verificar se o termo de busca contém alguma palavra-chave conhecida
    lower_query = query.lower()
    for key, values in base_suggestions.items():
        if key in lower_query:
            suggestions.extend(values)
    
    # Adicionar algumas sugestões genéricas baseadas no query
    suggestions.extend([
        f"{query} tutorial",
        f"{query} para iniciantes",
        f"{query} como funciona",
        f"{query} avançado",
        f"o que é {query}",
        f"aprender {query}",
        f"{query} exemplos",
        f"{query} passo a passo"
    ])
    
    # Remover duplicatas e limitar a 20 sugestões
    return list(dict.fromkeys(suggestions))[:20]

# Layout similar ao app HTTP - com cabeçalho chamativo e formulário centralizado
st.markdown("<h1 class='youtube-title'>🎬 Agente de IA Videos</h1>", unsafe_allow_html=True)

# CSS adicional para melhorar o autocomplete
st.markdown("""
<style>
    /* Estilo para destacar o autocomplete */
    .autocomplete-info {
        background-color: #e6f7ff;
        border-left: 4px solid #1890ff;
        padding: 8px 12px;
        margin-bottom: 10px;
        font-size: 14px;
        border-radius: 4px;
    }
    
    /* Estilo para o campo de busca com ícone */
    .search-with-icon {
        position: relative;
    }
    
    .search-with-icon input {
        padding-left: 36px !important;
    }
    
    .search-icon {
        position: absolute;
        left: 10px;
        top: 50%;
        transform: translateY(-50%);
        color: #666;
        z-index: 100;
    }
    
    /* Estilização para as sugestões */
    .suggestion-item {
        display: block;
        padding: 8px 12px;
        border-bottom: 1px solid #eee;
        cursor: pointer;
    }
    
    .suggestion-item:hover {
        background-color: #f5f5f5;
    }
    
    /* Estilo para o painel de opções */
    .options-panel {
        background-color: #f8f8f8;
        border-radius: 8px;
        padding: 15px;
        margin-top: 10px;
        border: 1px solid #eee;
    }
    
    /* Estilo para botões de sugestão - agora usando as mesmas cores do botão principal */
    .suggestion-button button {
        background-color: #FF0000 !important;
        color: white !important;
        font-weight: bold !important;
        height: 46px !important;
        font-size: 16px !important;
        border: none !important;
        padding: 0.5rem 1rem !important;
        border-radius: 4px !important;
        cursor: pointer !important;
    }
    
    .suggestion-button button:hover {
        background-color: #CC0000 !important;
    }
    
    /* Estilo para o botão de busca de vídeos */
    .search-button button {
        height: 46px;
        font-size: 16px;
    }
    
    /* Estilo para o filtro de tempo */
    .time-filter {
        padding: 8px 12px;
        border-radius: 4px;
        background-color: white;
    }
    
    /* Estilo geral para todos os botões primários */
    .stButton > button[data-baseweb="button"] {
        background-color: #FF0000 !important;
        color: white !important;
        border: none !important;
        font-weight: bold !important;
    }
    
    /* Hover para todos os botões */
    .stButton > button[data-baseweb="button"]:hover {
        background-color: #CC0000 !important;
    }
    
    /* NOVOS ESTILOS PARA GARANTIR QUE OS BOTÕES FIQUEM VERMELHOS */
    /* Estilo mais agressivo para TODOS os botões no Streamlit */
    button, .stButton > button, div[data-testid="stButton"] > button, button[kind="primary"] {
        background-color: #FF0000 !important;
        color: white !important;
        border: none !important;
        font-weight: bold !important;
        border-radius: 4px !important;
    }
    
    /* Hover para TODOS os botões */
    button:hover, .stButton > button:hover, div[data-testid="stButton"] > button:hover, button[kind="primary"]:hover {
        background-color: #CC0000 !important;
    }
    
    /* Estilo específico para o botão "Buscar Vídeos no YouTube" */
    button[kind="primary"], button[data-testid="baseButton-primary"], .stButton > button[kind="primary"] {
        background-color: #FF0000 !important;
        color: white !important;
        border: none !important;
        font-weight: bold !important;
        height: 46px !important;
    }
</style>
""", unsafe_allow_html=True)

# Formulário centralizado (em vez de barra lateral)
search_container = st.container()

with search_container:
    # Informações sobre o autocomplete
    st.markdown("""
    <div class="autocomplete-info">
        ✨ <b>Busca de vídeos:</b> Digite sua consulta, obtenha sugestões e filtre resultados conforme necessário.
    </div>
    """, unsafe_allow_html=True)
    
    # Primeira linha: Campo de busca e botão de sugestões
    col1, col2 = st.columns([4, 1])
    
    with col1:
        # Campo de busca com placeholder informativo e usando session_state para manter o valor
        if 'user_query' not in st.session_state:
            st.session_state['user_query'] = ""
        
        # Função para atualizar o campo de busca quando uma sugestão é selecionada
        def set_query(suggestion):
            st.session_state['user_query'] = suggestion
        
        initial_query = st.text_input(
            "Digite o que deseja buscar", 
            value=st.session_state['user_query'], 
            placeholder="Ex: agentes de IA para, receitas fáceis, tutoriais python...",
            help="Digite o que deseja buscar no YouTube",
            key="search_input"
        )
        # Atualizar a variável de estado com o valor atual, mas apenas se não foi definido por uma sugestão
        if 'suggestion_clicked' not in st.session_state or not st.session_state['suggestion_clicked']:
            st.session_state['user_query'] = initial_query
    
    with col2:
        # Adicionando um estilo personalizado diretamente para o botão - Estratégia mais direta
        st.markdown("""
        <style>
        /* Força VERMELHO para todos os botões na coluna 2 - super específico */
        [data-testid="column"][data-column-index="1"] .stButton > button {
            background-color: #FF0000 !important;
            color: white !important;
            border: none !important;
            font-weight: bold !important;
            height: 46px !important;
            font-size: 16px !important;
            width: 100% !important;
            padding: 0.5rem 1rem !important;
            border-radius: 4px !important;
            cursor: pointer !important;
        }
        
        /* Força o hover também */
        [data-testid="column"][data-column-index="1"] .stButton > button:hover {
            background-color: #CC0000 !important;
        }
        </style>
        """, unsafe_allow_html=True)
        
        # Botão para buscar sugestões (sem div wrapper para simplicidade)
        suggest_button = st.button(
            "🔍 Ver sugestões", 
            key="suggest_button", 
            help="Clique para ver sugestões relacionadas à sua busca",
            use_container_width=True,
            type="primary"  # Adicionando o tipo primary para garantir consistência
        )

# Limpar estado de sugestão clicada quando o botão de sugestões é pressionado
if suggest_button:
    st.session_state['suggestion_clicked'] = False

# Variáveis que controlarão o fluxo
show_suggestions = False
suggestions = []
all_options = []  # Inicializar fora do bloco if para acesso global

# Só busca sugestões se o botão for clicado e houver consulta
if suggest_button and initial_query and len(initial_query) >= 2:
    with st.spinner("Buscando sugestões..."):
        suggestions = get_search_suggestions(initial_query)
        show_suggestions = True

# Se houver sugestões para mostrar
if show_suggestions and suggestions:
    # Não adicionar a consulta original como primeira opção
    all_options = [s for s in suggestions if s != initial_query]
        
    # Exibir um subtítulo para as sugestões
    st.caption(f"Sugestões disponíveis ({len(all_options)} encontradas):")
    
    # Adicione CSS para melhorar a aparência dos botões de sugestão
    st.markdown("""
    <style>
    /* Estilização para botões de sugestão */
    div[data-testid="column"] .stButton > button {
        min-height: 0px !important;
        line-height: 1.2 !important;
        padding: 6px 12px !important;
        font-size: 14px !important;
        margin: 3px 0px !important;
        width: 100% !important;
        background-color: #FF0000 !important;
        color: white !important;
        border-radius: 20px !important;
        border: none !important;
        text-overflow: ellipsis !important;
        overflow: hidden !important;
        white-space: nowrap !important;
    }
    
    div[data-testid="column"] .stButton > button:hover {
        background-color: #CC0000 !important;
        transform: translateY(-2px);
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Criar uma variável para armazenar qual sugestão foi selecionada
    suggestion_selected = False
    selected_suggestion = ""  # Iniciar vazio
    
    # Número máximo de sugestões a mostrar
    max_suggestions = min(20, len(all_options))
    
    # Exibir mensagem se não houver sugestões além do termo original
    if max_suggestions == 0:
        st.info("Não foram encontradas sugestões adicionais. Tente outro termo de busca.")
    
    # Definir quantos botões por linha (ajustável)
    buttons_per_row = 4
    
    # Criação dinâmica das linhas de botões
    for i in range(0, max_suggestions, buttons_per_row):
        # Criar uma linha com número adequado de colunas
        cols = st.columns(buttons_per_row)
        
        # Preencher as colunas com botões
        for j in range(buttons_per_row):
            idx = i + j
            if idx < max_suggestions:
                with cols[j]:
                    option_text = all_options[idx]
                    # Não truncar mais o texto, mostrar texto completo no tooltip
                    if st.button(option_text, key=f"suggestion_{idx}", help=option_text, on_click=set_query, args=(option_text,)):
                        # Marcar que uma sugestão foi clicada para evitar sobrescrita
                        st.session_state['suggestion_clicked'] = True
                        # Definir a query para uso posterior
                        query = option_text
                        # Indicador visual de seleção
                        st.success(f"✓ Sugestão '{option_text}' selecionada!")

# Mostrar mensagem informativa sobre as sugestões se houver muitas
if show_suggestions and len(all_options) > 4:
    st.info("✨ Clique em qualquer sugestão para usá-la como termo de busca. Use o botão \"Buscar Vídeos\" para realizar a busca.")
elif show_suggestions and not suggestions:
    # Se o usuário clicou em sugestões mas não há resultados
    st.caption("Nenhuma sugestão encontrada. Continue sua busca com o termo atual.")
    query = initial_query
else:
    # Se não está mostrando sugestões, usar o valor inicial
    query = initial_query
    
# Nova linha para os controles de filtro (3 colunas agora)
filter_col1, filter_col2, filter_col3 = st.columns(3)

with filter_col1:
    # Filtro de tempo
    time_filter = st.selectbox(
        "Filtrar por período",
        options=[
            "Qualquer período", 
            "Última hora", 
            "Hoje", 
            "Esta semana", 
            "Este mês",
            "Este ano"
        ],
        index=0
    )
    
    # Valores correspondentes para a API
    tbs_mapping = {
        "Qualquer período": "",
        "Última hora": "qdr:h",
        "Hoje": "qdr:d",
        "Esta semana": "qdr:w",
        "Este mês": "qdr:m",
        "Este ano": "qdr:y"
    }
    tbs = tbs_mapping[time_filter]

with filter_col2:
    # Número de resultados como dropdown em vez de slider
    num_options = [5, 10, 15, 20, 25, 30, 40, 50]
    num_results = st.selectbox(
        "Número de resultados",
        options=num_options,
        index=2  # 15 resultados por padrão (índice 2)
    )

with filter_col3:
    # Filtro de plataforma
    platform_filter = st.selectbox(
        "Plataforma",
        options=[
            "Todas", 
            "YouTube", 
            "Instagram"
        ],
        index=0,
        help="Filtrar resultados por plataforma de vídeo"
    )

# Definir valores padrão para região (Brasil)
gl = "br"
location = "Brasil"
selected_region = "Brasil"  # Adicionando a definição que estava faltando

# Região e idioma
region_options = [
    ("Brasil", "br", "Brasil"),
    ("Estados Unidos", "us", "United States"),
    ("Portugal", "pt", "Portugal"),
    ("Espanha", "es", "Spain"),
    ("Reino Unido", "uk", "United Kingdom"),
    ("Canadá", "ca", "Canada"),
    ("França", "fr", "France"),
    ("Alemanha", "de", "Germany"),
    ("Itália", "it", "Italy"),
    ("Japão", "jp", "Japan")
]

# Idioma em uma nova linha para mais espaço
language_options = [
    ("Português (Brasil)", "pt-br"),
    ("Inglês (EUA)", "en"),
    ("Espanhol", "es"),
    ("Português (Portugal)", "pt-pt"),
    ("Francês", "fr"),
    ("Alemão", "de"),
    ("Italiano", "it"),
    ("Japonês", "ja")
]

# Localizar idioma selecionado (usando o primeiro por padrão)
selected_language = language_options[0][0]
selected_language_data = language_options[0]
hl = selected_language_data[1]

# Botão de busca principal
st.markdown("""
<style>
/* Estilo extra forçando cor para o botão principal específico */
div.search-button .stButton > button {
    background-color: #FF0000 !important;
    color: white !important;
    border: none !important;
    font-weight: bold !important;
    height: 46px !important;
    font-size: 16px !important;
    width: 100% !important;
}
</style>
<div class="search-button">
""", unsafe_allow_html=True)
search_button = st.button("🎬 Buscar Vídeos", type="primary", use_container_width=True)
st.markdown('</div>', unsafe_allow_html=True)

# Container de resultados com nova classe
content_container = st.container()

# Lógica principal
if search_button and query:
    # Mostrar parâmetros de busca ao usuário
    st.caption(f"Buscando '{query}' em {selected_region} ({gl}) • Idioma: {selected_language} • Filtro de tempo: {time_filter} • Máximo: {num_results} vídeos • Plataforma: {platform_filter}")
    
    # Realizar a busca
    with st.spinner(f"Buscando vídeos para: '{query}'..."):
        results = search_videos(query, location, gl, hl, num_results, tbs)
    
    # Verificar erros
    if "error" in results:
        st.error(f"Erro ao realizar a busca: {results['error']}")
        if "raw" in results:
            with st.expander("Detalhes do erro"):
                st.code(results["raw"])
    else:
        # Exibir parâmetros da busca
        with st.expander("Parâmetros técnicos da busca", expanded=False):
            st.json(results.get("searchParameters", {}))
        
        # Exibir informações
        all_videos = results.get("videos", [])
        
        # Filtrar vídeos pela plataforma selecionada
        if platform_filter == "YouTube":
            videos = [v for v in all_videos if "youtube.com" in v.get('link', '') or "youtu.be" in v.get('link', '')]
        elif platform_filter == "Instagram":
            videos = [v for v in all_videos if "instagram.com" in v.get('link', '')]
        else:
            videos = all_videos  # Todas as plataformas
        
        if not videos:
            if platform_filter != "Todas":
                st.warning(f"Nenhum vídeo do {platform_filter} encontrado para '{query}'. Tente mudar a plataforma para 'Todas'.")
            else:
                st.warning(f"Nenhum vídeo encontrado para '{query}'")
        else:
            st.subheader(f"Resultados para: '{query}' - {platform_filter}")
            
            # Mostrar quantos vídeos foram encontrados e quantos estão sendo mostrados após filtro
            if platform_filter != "Todas" and len(videos) != len(all_videos):
                st.write(f"Encontrados {len(all_videos)} vídeos no total, exibindo {len(videos)} vídeos do {platform_filter}")
            else:
                st.write(f"Encontrados {len(videos)} vídeos")
            
            # Organizar vídeos em grade (3 por linha)
            cols = st.columns(3)
            
            for i, video in enumerate(videos):
                with cols[i % 3]:
                    # Usar a função render_video_card para criar o HTML do card
                    # com melhor tratamento de erros, e garantir que ele seja
                    # renderizado corretamente com unsafe_allow_html=True
                    try:
                        card_html = render_video_card(video)
                        st.markdown(card_html, unsafe_allow_html=True)
                    except Exception as e:
                        st.error(f"Erro ao renderizar vídeo: {str(e)}")
elif not query and search_button:
    st.warning("Por favor, insira um termo de busca.")
else:
    # Mensagem inicial quando nenhuma busca foi realizada
    with content_container:
        st.info("""
        ## Bem-vindo ao Agente de IA Videos
        
        Digite uma consulta, clique em "Ver sugestões" para obter recomendações,
        use o painel de "Mais opções" para filtrar seus resultados, e então
        clique em "Buscar Vídeos" para visualizar os resultados.
        
        Este aplicativo utiliza a API Serper para realizar buscas de vídeos.
        """)

# Rodapé
st.markdown("""
<footer>
    <p>Desenvolvido com Python, Streamlit e API Serper | Agente de IA Videos v1.0</p>
</footer>
""", unsafe_allow_html=True)

if __name__ == "__main__":
    # O código principal já foi executado acima
    pass 