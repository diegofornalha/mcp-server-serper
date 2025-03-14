# Resolução de Problemas de Renderização HTML em Aplicativos Streamlit

## Problema Identificado

O aplicativo Streamlit de busca de vídeos do YouTube apresentava problemas de renderização HTML, onde o código HTML aparecia como texto bruto na interface em vez de ser renderizado corretamente:

- Tags HTML como `<span></span>`, `<div>`, `<a href="...">` sendo exibidas como texto
- Botões "Assistir no YouTube" aparecendo como código HTML bruto
- Elementos condicionais (como visualizações de vídeos) não sendo renderizados corretamente
- **Thumbnails de vídeos não aparecendo ou exibindo apenas placeholders/ícones pequenos**

Esse problema ocorria principalmente em componentes dinâmicos cujo HTML era gerado com base em dados da API Serper.

## Diagnóstico do Problema

Após análise, identificamos as seguintes causas:

1. **Uso de expressões condicionais dentro de strings f-string complexas**:
   ```python
   return f"""
       <div>
           {f'<span>{views}</span>' if views else ''}
           <span>{date}</span>
       </div>
   """
   ```

2. **Falta de escape correto de caracteres especiais** nos dados recebidos da API

3. **Renderização inconsistente** quando expressões condicionais eram aninhadas dentro de strings HTML maiores

4. **Problemas com URLs de thumbnails**:
   - A ordem de tentativa de URLs não era ideal, tentando primeiro a URL da API que nem sempre era confiável
   - Uso de URLs do formato `img.youtube.com` em vez do mais confiável `i.ytimg.com`
   - Manipulação inadequada de falhas no carregamento de imagens

## Solução Implementada

### 1. Modificação da função `render_video_card`

Alteramos a função que gera o HTML dos cards de vídeo para construir progressivamente o HTML em vez de usar expressões condicionais aninhadas:

**Antes:**
```python
def render_video_card(video):
    # ... código para obter dados ...
    
    views_html = f'<span>{views}</span>' if views else ''
    
    return f"""
    <div class="video-card">
        <div class="video-thumbnail-container">
            <img src="{thumbnail_url}" ... >
            <div class="duration-badge">{duration}</div>
        </div>
        <div class="video-info">
            <div class="video-title">{video_title}</div>
            <div class="video-channel">{video_channel}</div>
            <div class="video-metadata">
                {views_html}
                <span>{upload_date}</span>
            </div>
            <a href="{video_link}" target="_blank" style="text-decoration: none;">
                <button style="...">Assistir no YouTube</button>
            </a>
        </div>
    </div>
    """
```

**Depois:**
```python
def render_video_card(video):
    # ... código para obter dados ...
    
    # Construir HTML progressivamente
    video_html = f"""
    <div class="video-card">
        <div class="video-thumbnail-container">
            <img src="{thumbnail_url}" ... >
            <div class="duration-badge">{duration}</div>
        </div>
        <div class="video-info">
            <div class="video-title">{video_title}</div>
            <div class="video-channel">{video_channel}</div>
            <div class="video-metadata">
    """
    
    # Adicionar visualizações apenas se disponíveis
    if views:
        video_html += f'<span>{views}</span>'
    
    # Adicionar data de upload
    if upload_date:
        video_html += f'<span>{upload_date}</span>'
    
    # Fechar div de metadados e adicionar botão
    video_html += f"""
            </div>
            <a href="{video_link}" target="_blank" style="text-decoration: none;">
                <button style="{button_style}">
                    Assistir no YouTube
                </button>
            </a>
        </div>
    </div>
    <br>
    """
    
    return video_html
```

### 2. Uso do módulo `html` para escapar caracteres especiais

Garantimos que todos os dados recebidos da API fossem adequadamente escapados:

```python
video_title = html.escape(video.get('title', 'Sem título'))
video_channel = html.escape(video.get('channel', 'Canal desconhecido'))
```

### 3. Adição de tratamento de exceções

Implementamos tratamento de exceções durante a renderização dos cards:

```python
for i, video in enumerate(videos):
    with cols[i % 3]:
        try:
            card_html = render_video_card(video)
            st.markdown(card_html, unsafe_allow_html=True)
        except Exception as e:
            st.error(f"Erro ao renderizar vídeo: {str(e)}")
```

### 4. Pré-processamento de elementos complexos

Extraímos a lógica complexa para variáveis antes de incluí-las no HTML:

```python
fallback_img = "https://via.placeholder.com/480x360.png"
fallback_text = "Thumbnail+indispon%C3%ADvel"
onerror_script = (
    f"this.onerror=null; this.src='{fallback_img}?text={fallback_text}'; "
    "this.style.backgroundColor='#f0f0f0';"
)

button_style = (
    "background-color: #FF0000; color: white; border: none; "
    "padding: 6px 12px; margin-top: 8px; border-radius: 4px; "
    "cursor: pointer; width: 100%;"
)
```

### 5. Melhorias específicas para o carregamento de thumbnails

Para resolver o problema específico das thumbnails não exibidas, implementamos as seguintes melhorias:

**Antes (estratégia ineficiente):**
```python
def get_thumbnail_url(video):
    # Primeiro tenta usar a URL da thumbnail fornecida pela API
    thumbnail_url = video.get('thumbnailUrl', '')
    
    # Se não tiver thumbnail, tenta extrair o ID do YouTube e construir a URL
    if not thumbnail_url:
        video_link = video.get('link', '')
        video_id = extract_youtube_id(video_link)
        # ... resto do código
```

**Depois (estratégia mais eficaz):**
```python
def get_thumbnail_url(video):
    # Primeiro tentamos extrair o ID do YouTube e construir URLs diretas
    # que são mais confiáveis que as URLs fornecidas pela API
    video_link = video.get('link', '')
    video_id = extract_youtube_id(video_link)
    
    if video_id:
        # URL direta do CDN de imagens do YouTube (mais confiável)
        return f"https://i.ytimg.com/vi/{video_id}/hqdefault.jpg"
    
    # Fallbacks para outras fontes de URLs...
```

Principais melhorias na abordagem para obtenção das thumbnails:

1. **Ordem de prioridade invertida**: Usar primeiro a extração do ID do YouTube e construção direta da URL, em vez de confiar na URL da API
2. **Uso do domínio mais confiável**: Mudar de `img.youtube.com` para `i.ytimg.com` (CDN oficial de imagens do YouTube)
3. **Simplificação**: Em vez de testar várias URLs, focar na mais confiável (`hqdefault.jpg`)
4. **Aprimoramento do atributo onerror**: Melhor tratamento de falhas de carregamento de imagem
5. **Adição de atributo alt**: Melhoramento de acessibilidade com texto alternativo

A tag de imagem final ficou mais robusta:
```html
<img src="{thumbnail_url}" width="100%" height="100%" 
     style="object-fit: cover;" 
     onerror="this.onerror=null;this.src='https://via.placeholder.com/480x360.png?text=Thumbnail+indispon%C3%ADvel';this.style.backgroundColor='#f0f0f0';console.log('Erro ao carregar thumbnail, usando fallback');" 
     alt="{html.escape(video_title)}">
```

## Guia Passo a Passo para Resolver Problemas Similares

Se você estiver enfrentando problemas semelhantes em seu aplicativo Streamlit, siga estes passos:

### Passo 1: Identifique as áreas problemáticas

1. Execute seu aplicativo e identifique os elementos que mostram código HTML bruto
2. Localize no código onde esses elementos são gerados (normalmente funções que retornam HTML)
3. Preste atenção especial a partes do código que usam expressões condicionais dentro de strings HTML
4. Verifique no console do navegador erros de carregamento de imagens ou recursos

### Passo 2: Importe e use o módulo `html` para escape

```python
import html

# Use nos dados externos
texto_seguro = html.escape(texto_da_api)
```

### Passo 3: Refatore a construção do HTML

1. Divida a construção de HTML complexo em etapas
2. Inicie com uma estrutura básica
3. Adicione elementos condicionais de forma progressiva
4. Finalize a estrutura HTML

Exemplo:

```python
# Iniciar com estrutura básica
html_string = f"""
<div class="container">
    <h2>{titulo_seguro}</h2>
"""

# Adicionar elementos condicionais
if descricao:
    html_string += f'<p class="descricao">{html.escape(descricao)}</p>'

# Finalizar estrutura
html_string += """
</div>
"""
```

### Passo 4: Pré-processe elementos complexos

1. Extraia a lógica complexa para variáveis antes de incluí-las no HTML
2. Isso torna o código mais legível e evita problemas de interpolação aninhada

```python
# Pré-processar formatação complexa
if rating:
    stars_html = "★" * int(rating)
    if rating % 1 >= 0.5:
        stars_html += "½"
else:
    stars_html = ""

# Usar no HTML
html_string += f'<div class="rating">{stars_html}</div>'
```

### Passo 5: Para carregamento de imagens, implemente estratégias robustas

1. **Use atributos onerror** para tratar falhas de carregamento:
```html
<img src="url_da_imagem" onerror="this.onerror=null;this.src='imagem_fallback.jpg'">
```

2. **Priorize URLs confiáveis** quando trabalhar com serviços externos:
```python
# Para thumbnails do YouTube, prefira usar:
f"https://i.ytimg.com/vi/{video_id}/hqdefault.jpg"
```

3. **Teste a disponibilidade de recursos** quando possível:
```python
import requests
def url_existe(url):
    try:
        response = requests.head(url, timeout=2)
        return response.status_code == 200
    except:
        return False
```

### Passo 6: Adicione tratamento de exceções

Envolva a renderização de HTML em blocos try-except para capturar problemas:

```python
try:
    html_content = gerar_html(dados)
    st.markdown(html_content, unsafe_allow_html=True)
except Exception as e:
    st.error(f"Erro ao renderizar conteúdo: {str(e)}")
```

### Passo 7: Teste com diversos cenários de dados

1. Teste com dados que contenham caracteres especiais (`<`, `>`, `"`, `'`, `&`)
2. Teste com valores nulos ou vazios para campos condicionais
3. Verifique o comportamento com valores extremos (textos muito longos, números muito grandes)
4. Teste com URLs de imagens inválidas ou inacessíveis para verificar os fallbacks

## Conclusão

Os problemas de renderização HTML em aplicativos Streamlit geralmente surgem de práticas inadequadas ao combinar dados dinâmicos com templating HTML. Seguindo os princípios acima, você pode garantir que seu aplicativo renderize corretamente o HTML em todos os cenários:

1. **Construa HTML progressivamente**, não use expressões condicionais aninhadas
2. **Escape todos os dados externos** usando `html.escape()`
3. **Pré-processe elementos complexos** antes de incluí-los no HTML
4. **Adicione tratamento de exceções** para capturar problemas de renderização
5. **Implemente estratégias robustas para carregamento de imagens** com fallbacks adequados
6. **Teste com diversos tipos de dados** para garantir robustez

Estas práticas não apenas resolvem problemas de renderização, mas também melhoram a segurança, prevenindo possíveis ataques de injeção de código e tornando seu aplicativo Streamlit mais robusto e profissional. 