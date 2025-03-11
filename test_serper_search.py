#!/usr/bin/env python3

"""
Script de teste unificado para busca usando a API Serper.
Este script demonstra como realizar diferentes tipos de busca usando a API Serper
e exibe os resultados em formato JSON formatado.
"""

import os
import sys
import json
import http.client
import argparse
from dotenv import load_dotenv

# Carregar variáveis de ambiente de .env (se existir)
load_dotenv()

class SerperTester:
    """Classe para testar a API Serper com diferentes tipos de busca."""
    
    def __init__(self, api_key=None):
        """
        Inicializa o testador da API Serper.
        
        Args:
            api_key: Chave da API Serper. Se não for fornecida, tentará obter do ambiente.
        """
        # Obter a chave da API do ambiente ou usar a fornecida
        self.api_key = api_key or os.getenv("SERPER_API_KEY", "5b5305befa6a1187c56d7ba06e2971aca87e6a0e")
    
    def test_search(self, search_type, query, location="Brazil", gl="br", hl="pt-br", num=10):
        """
        Testa a busca Serper com os parâmetros especificados.
        
        Args:
            search_type: Tipo de busca (web, images, videos, news, places)
            query: Consulta de busca
            location: Localização para resultados
            gl: Código da região
            hl: Código de idioma
            num: Número de resultados
            
        Returns:
            Dados da resposta da API ou None em caso de erro
        """
        # Mapear tipos de busca para endpoints
        endpoints = {
            "web": "/search",
            "images": "/images",
            "videos": "/videos",
            "news": "/news",
            "places": "/places",
            "maps": "/maps",
            "reviews": "/reviews",
            "shopping": "/shopping",
            "lens": "/lens",
            "scholar": "/scholar",
            "patents": "/patents",
            "webpage": "/webpage"
        }
        
        # Obter o endpoint correto
        endpoint = endpoints.get(search_type)
        if not endpoint:
            print(f"Erro: Tipo de busca inválido: {search_type}")
            print(f"Tipos válidos: {', '.join(endpoints.keys())}")
            return None
        
        # Configurar a conexão HTTPS
        conn = http.client.HTTPSConnection("google.serper.dev")
        
        # Preparar o payload da requisição
        payload = json.dumps({
            "q": query,
            "location": location,
            "gl": gl,
            "hl": hl,
            "num": num
        })
        
        # Configurar os headers
        headers = {
            'X-API-KEY': self.api_key,
            'Content-Type': 'application/json'
        }
        
        # Enviar a requisição para o endpoint
        print(f"Enviando requisição para o endpoint de busca {search_type}...")
        conn.request("POST", endpoint, payload, headers)
        
        # Obter a resposta
        res = conn.getresponse()
        data = res.read()
        
        # Exibir o status da resposta
        print(f"Status: {res.status} {res.reason}")
        
        if res.status == 200:
            # Decodificar os dados JSON
            response_data = json.loads(data.decode("utf-8"))
            return response_data
        else:
            # Exibir mensagem de erro
            print(f"Erro na requisição: {data.decode('utf-8')}")
            return None
        
    def display_results(self, search_type, response_data):
        """
        Exibe os resultados da busca de forma amigável.
        
        Args:
            search_type: Tipo de busca
            response_data: Dados da resposta da API
        """
        if not response_data:
            return
        
        # Exibir parâmetros da busca
        print("\nParâmetros da busca:")
        print(f"- Consulta: {response_data.get('searchParameters', {}).get('q', 'N/A')}")
        print(f"- Localização: {response_data.get('searchParameters', {}).get('location', 'N/A')}")
        print(f"- Idioma: {response_data.get('searchParameters', {}).get('hl', 'N/A')}")
        
        # Obter os resultados com base no tipo de busca
        results_key_map = {
            "web": "organic",
            "images": "images",
            "videos": "videos",
            "news": "news",
            "places": "places"
        }
        
        results_key = results_key_map.get(search_type, "organic")
        results = response_data.get(results_key, [])
        
        # Exibir o número de resultados
        print(f"\nForam encontrados {len(results)} resultados de {search_type}:\n")
        
        # Exibir cada resultado
        for i, item in enumerate(results, start=1):
            print(f"Resultado {i}:")
            self._display_item_info(search_type, item)
            print()
        
        # Exibir informações de uso
        print(f"Créditos usados: {response_data.get('usage', {}).get('used', 'N/A')}")
    
    def _display_item_info(self, search_type, item):
        """
        Exibe informações específicas de um item com base no tipo de busca.
        
        Args:
            search_type: Tipo de busca
            item: Item do resultado
        """
        if search_type == "web":
            print(f"- Título: {item.get('title', 'Sem título')}")
            print(f"- Link: {item.get('link', 'N/A')}")
            
            snippet = item.get('snippet', 'N/A')
            if len(snippet) > 100:
                snippet = snippet[:97] + "..."
            print(f"- Snippet: {snippet}")
            
        elif search_type == "images":
            print(f"- Título: {item.get('title', 'Sem título')}")
            print(f"- Link: {item.get('link', 'N/A')}")
            print(f"- Imagem: {item.get('imageUrl', 'N/A')}")
            print(f"- Fonte: {item.get('source', 'N/A')}")
            
        elif search_type == "videos":
            print(f"- Título: {item.get('title', 'Sem título')}")
            print(f"- Canal: {item.get('channelTitle', 'Canal desconhecido')}")
            print(f"- Duração: {item.get('duration', 'Desconhecida')}")
            print(f"- Link: {item.get('link', 'N/A')}")
            print(f"- Thumbnail: {item.get('thumbnailUrl', 'N/A')}")
            print(f"- Data: {item.get('publishedDate', 'N/A')}")
            print(f"- Visualizações: {item.get('views', 'N/A')}")
            
        elif search_type == "news":
            print(f"- Título: {item.get('title', 'Sem título')}")
            print(f"- Link: {item.get('link', 'N/A')}")
            print(f"- Data: {item.get('date', 'N/A')}")
            print(f"- Fonte: {item.get('source', 'N/A')}")
            
            snippet = item.get('snippet', 'N/A')
            if len(snippet) > 100:
                snippet = snippet[:97] + "..."
            print(f"- Snippet: {snippet}")
            
        elif search_type == "places":
            print(f"- Nome: {item.get('name', 'Sem nome')}")
            print(f"- Endereço: {item.get('address', 'N/A')}")
            print(f"- Avaliação: {item.get('rating', 'N/A')}")
            print(f"- Categoria: {item.get('category', 'N/A')}")
            
        else:
            # Exibir dados genéricos para outros tipos
            for key, value in item.items():
                if isinstance(value, str) and len(value) > 100:
                    value = value[:97] + "..."
                print(f"- {key}: {value}")


def main():
    """Função principal para testar a API Serper."""
    # Configurar parser de argumentos
    parser = argparse.ArgumentParser(description="Testar a API Serper com diferentes tipos de busca")
    parser.add_argument("--type", "-t", default="web", 
                       choices=["web", "images", "videos", "news", "places", "maps", "reviews", 
                                "shopping", "lens", "scholar", "patents", "webpage"],
                       help="Tipo de busca (web, images, videos, news, places, maps, reviews, shopping, lens, scholar, patents, webpage)")
    parser.add_argument("--query", "-q", default="agentes de inteligência artificial",
                       help="Consulta de busca")
    parser.add_argument("--location", "-l", default="Brazil",
                       help="Localização para resultados")
    parser.add_argument("--gl", "-g", default="br",
                       help="Código da região")
    parser.add_argument("--hl", "-i", default="pt-br",
                       help="Código de idioma")
    parser.add_argument("--num", "-n", default=10, type=int,
                       help="Número de resultados")
    parser.add_argument("--key", "-k", 
                       help="Chave da API Serper (opcional, se não fornecida usa a do ambiente)")
    parser.add_argument("--json", "-j", action="store_true",
                       help="Exibir a resposta completa em formato JSON")
    
    # Analisar argumentos
    args = parser.parse_args()
    
    # Criar e executar o testador
    tester = SerperTester(args.key)
    response = tester.test_search(
        search_type=args.type,
        query=args.query,
        location=args.location,
        gl=args.gl,
        hl=args.hl,
        num=args.num
    )
    
    # Exibir resultados
    if response:
        if args.json:
            # Exibir a resposta completa em JSON formatado
            print("\nResposta completa em JSON:")
            print(json.dumps(response, indent=2, ensure_ascii=False))
        else:
            # Exibir resultados formatados
            tester.display_results(args.type, response)

if __name__ == "__main__":
    main() 