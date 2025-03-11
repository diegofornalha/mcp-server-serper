#!/usr/bin/env python3

"""
Script de teste para busca de vídeos usando a API Serper.
Este script demonstra como realizar uma busca de vídeos usando a API Serper
e exibe os resultados em formato JSON formatado.
"""

import os
import json
import http.client
from dotenv import load_dotenv

# Carregar variáveis de ambiente de .env (se existir)
load_dotenv()

def test_video_search():
    """
    Testa a funcionalidade de busca de vídeos da API Serper.
    Realiza uma busca simples e exibe os resultados.
    """
    # Obter a chave da API do ambiente ou usar uma padrão para testes
    api_key = os.getenv("SERPER_API_KEY", "5b5305befa6a1187c56d7ba06e2971aca87e6a0e")
    
    # Configurar a conexão HTTPS
    conn = http.client.HTTPSConnection("google.serper.dev")
    
    # Preparar o payload da requisição
    payload = json.dumps({
        "q": "agentes de inteligência artificial",
        "location": "Brazil",
        "gl": "br",
        "hl": "pt-br"
    })
    
    # Configurar os headers
    headers = {
        'X-API-KEY': api_key,
        'Content-Type': 'application/json'
    }
    
    # Enviar a requisição para o endpoint de vídeos
    print("Enviando requisição para o endpoint de busca de vídeos...")
    conn.request("POST", "/videos", payload, headers)
    
    # Obter a resposta
    res = conn.getresponse()
    data = res.read()
    
    # Exibir o status da resposta
    print(f"Status: {res.status} {res.reason}")
    
    # Processar e exibir os resultados
    if res.status == 200:
        # Decodificar e formatar a resposta JSON
        response_data = json.loads(data.decode("utf-8"))
        print("\nParâmetros da busca:")
        print(f"- Consulta: {response_data.get('searchParameters', {}).get('q', 'N/A')}")
        print(f"- Localização: {response_data.get('searchParameters', {}).get('location', 'N/A')}")
        print(f"- Idioma: {response_data.get('searchParameters', {}).get('hl', 'N/A')}")
        
        videos = response_data.get("videos", [])
        print(f"\nForam encontrados {len(videos)} vídeos:\n")
        
        for i, video in enumerate(videos, start=1):
            print(f"Vídeo {i}:")
            print(f"- Título: {video.get('title', 'Sem título')}")
            print(f"- Canal: {video.get('channelTitle', 'Canal desconhecido')}")
            print(f"- Duração: {video.get('duration', 'Desconhecida')}")
            print(f"- Link: {video.get('link', 'N/A')}")
            print(f"- Thumbnail: {video.get('thumbnailUrl', 'N/A')}")
            print(f"- Data: {video.get('publishedDate', 'N/A')}")
            print(f"- Visualizações: {video.get('views', 'N/A')}")
            print()
        
        # Exibir informações de uso
        print(f"Créditos usados: {response_data.get('usage', {}).get('used', 'N/A')}")
    else:
        # Exibir mensagem de erro
        print(f"Erro na requisição: {data.decode('utf-8')}")
    
    # Fechar a conexão
    conn.close()

if __name__ == "__main__":
    test_video_search() 