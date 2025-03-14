#!/usr/bin/env python3

"""
MCP server implementation that provides web search capabilities via Serper API in Python.
This is a migration from the TypeScript version.
"""

import os
import json
import sys
import logging
import http.client
from typing import Dict, Any, List, Optional, Union

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stderr)]
)
logger = logging.getLogger("serper-mcp-server")

class SerperClient:
    """Cliente para interação com a API Serper."""
    
    def __init__(self, api_key: str, base_url: str = "google.serper.dev"):
        """
        Inicializa o cliente da API Serper.
        
        Args:
            api_key: Chave da API Serper para autenticação
            base_url: URL base para a API Serper (opcional)
        """
        self.api_key = api_key
        self.base_url = base_url
        
    def _make_request(self, method: str, endpoint: str, payload: Any) -> Dict[str, Any]:
        """
        Faz uma requisição para a API Serper.
        
        Args:
            method: Método HTTP (GET, POST, etc.)
            endpoint: Endpoint da API
            payload: Dados a serem enviados na requisição
            
        Returns:
            Resposta da API como um dicionário
        """
        try:
            conn = http.client.HTTPSConnection(self.base_url)
            headers = {
                "X-API-KEY": self.api_key,
                "Content-Type": "application/json"
            }
            
            json_payload = json.dumps(payload) if payload is not None else None
            conn.request(method, endpoint, json_payload, headers)
            
            response = conn.getresponse()
            data = response.read().decode("utf-8")
            
            if response.status != 200:
                logger.error(f"Serper API error: {response.status} {data}")
                raise Exception(f"Serper API error: {response.status} {data}")
                
            return json.loads(data)
        except Exception as e:
            logger.error(f"Error making request to Serper API: {e}")
            raise
        finally:
            conn.close()
    
    def search(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Realiza uma busca web usando a API Serper.
        
        Args:
            params: Parâmetros de busca
            
        Returns:
            Resultados da busca
        """
        try:
            # Prepara o payload para a API Serper
            payload = {
                "q": params.get("q"),
                "gl": params.get("gl", "us"),
                "hl": params.get("hl", "en"),
                "autocorrect": params.get("autocorrect", True),
            }
            
            # Adiciona parâmetros opcionais se fornecidos
            if "location" in params:
                payload["location"] = params["location"]
            if "num" in params:
                payload["num"] = params["num"]
            if "page" in params:
                payload["page"] = params["page"]
            
            # Processa operadores de busca avançada
            for op in ["site", "filetype", "inurl", "intitle", "related", 
                       "cache", "before", "after", "exact", "exclude", "or",
                       "tbs"]:
                if op in params and params[op]:
                    payload[op] = params[op]
            
            return self._make_request("POST", "/search", payload)
        except Exception as e:
            logger.error(f"Error in search: {e}")
            raise Exception(f"Failed to search for '{params.get('q')}': {e}")
    
    def scrape(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Realiza raspagem de dados de uma página web.
        
        Args:
            params: Parâmetros de raspagem
            
        Returns:
            Dados raspados
        """
        try:
            payload = {
                "url": params.get("url"),
                "includeMarkdown": params.get("includeMarkdown", False)
            }
            
            return self._make_request("POST", "/scrape", payload)
        except Exception as e:
            logger.error(f"Error in scrape: {e}")
            raise Exception(f"Failed to scrape URL '{params.get('url')}': {e}")
    
    def health(self, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Verifica o status de saúde da API.
        
        Returns:
            Status de saúde
        """
        try:
            # A verificação de saúde é simples e não envia payload
            conn = http.client.HTTPSConnection(self.base_url)
            headers = {"X-API-KEY": self.api_key}
            
            conn.request("GET", "/health", None, headers)
            response = conn.getresponse()
            
            if response.status == 200:
                return {"status": "healthy", "version": "1.0.0"}
            else:
                return {"status": "unhealthy", "error": f"Status code: {response.status}"}
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {"status": "unhealthy", "error": str(e)}
        finally:
            conn.close()
            
    def analyze_serp(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analisa os resultados de busca SERP para uma consulta.
        
        Args:
            params: Parâmetros para análise SERP
            
        Returns:
            Análise SERP
        """
        try:
            payload = {
                "query": params.get("query"),
                "gl": params.get("gl", "us"),
                "hl": params.get("hl", "en"),
                "google_domain": params.get("google_domain", "google.com"),
                "num": params.get("num", 10),
                "device": params.get("device", "desktop"),
            }
            
            if "location" in params:
                payload["location"] = params["location"]
            if "safe" in params:
                payload["safe"] = params["safe"]
                
            response = self._make_request("POST", "/analyze-serp", payload)
            return {"analyzedData": response}
        except Exception as e:
            logger.error(f"Error in analyze_serp: {e}")
            raise Exception(f"Failed to analyze SERP for '{params.get('query')}': {e}")
            
    def research_keywords(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Pesquisa palavras-chave relacionadas a uma palavra-chave semente.
        
        Args:
            params: Parâmetros para pesquisa de palavras-chave
            
        Returns:
            Dados de pesquisa de palavras-chave
        """
        try:
            payload = {
                "keyword": params.get("keyword"),
            }
            
            # Adiciona parâmetros opcionais
            for param in ["language", "location"]:
                if param in params:
                    payload[param] = params[param]
            
            # Opções booleanas
            for option in ["include_questions", "include_related", "include_suggestions"]:
                if option in params:
                    payload[option] = params[option]
                    
            response = self._make_request("POST", "/keyword-research", payload)
            return {"keywordData": response}
        except Exception as e:
            logger.error(f"Error in research_keywords: {e}")
            raise Exception(f"Failed to research keywords for '{params.get('keyword')}': {e}")
            
    def analyze_competitors(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analisa concorrentes para um domínio/palavra-chave.
        
        Args:
            params: Parâmetros para análise de concorrentes
            
        Returns:
            Dados de análise de concorrentes
        """
        try:
            payload = {
                "domain": params.get("domain"),
            }
            
            # Adiciona parâmetros opcionais
            if "keyword" in params:
                payload["keyword"] = params["keyword"]
            if "num_results" in params:
                payload["num_results"] = params["num_results"]
            if "include_features" in params:
                payload["include_features"] = params["include_features"]
                
            response = self._make_request("POST", "/competitor-analysis", payload)
            return {"competitorData": response}
        except Exception as e:
            logger.error(f"Error in analyze_competitors: {e}")
            raise Exception(f"Failed to analyze competitors for '{params.get('domain')}': {e}")
            
    def autocomplete(self, query_list: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Obtém sugestões de autocompletar para múltiplas consultas.
        
        Args:
            query_list: Lista de consultas formatadas
            
        Returns:
            Sugestões de autocompletar para cada consulta
        """
        try:
            # Faz a requisição para o endpoint de autocompletar
            return self._make_request("POST", "/autocomplete", query_list)
        except Exception as e:
            logger.error(f"Error in autocomplete: {e}")
            raise Exception(f"Failed to get autocomplete suggestions: {e}")
            
    def image_search(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Realiza uma busca de imagens.
        
        Args:
            params: Parâmetros para a busca de imagens
            
        Returns:
            Resultados da busca de imagens
        """
        try:
            # Prepara o payload com os parâmetros necessários
            payload = {
                "q": params["q"]
            }
            
            # Adiciona parâmetros opcionais
            if "location" in params:
                payload["location"] = params["location"]
            if "gl" in params:
                payload["gl"] = params["gl"]
            if "hl" in params:
                payload["hl"] = params["hl"]
            if "num" in params:
                payload["num"] = params["num"]
                
            response = self._make_request("POST", "/images", payload)
            return {"imageResults": response}
        except Exception as e:
            logger.error(f"Error in image_search: {e}")
            raise Exception(f"Failed to search for images with query '{params.get('q')}': {e}")

    def video_search(self, query, location=None, gl=None, hl=None, num=None):
        """Search for videos using the Serper API."""
        return self._make_request("/videos", {
            "q": query,
            **({"location": location} if location else {}),
            **({"gl": gl} if gl else {}),
            **({"hl": hl} if hl else {}),
            **({"num": num} if num else {})
        })
        
    def youtube_search(self, q, location=None, gl=None, hl=None, num=None, tbs=None):
        """
        Busca exclusivamente vídeos do YouTube usando a API Serper.
        
        Args:
            q: Termo de busca
            location: Localização geográfica
            gl: Código de região do Google
            hl: Código de idioma
            num: Número de resultados
            tbs: Filtro de tempo (opcional)
            
        Returns:
            Resultados da busca filtrados para YouTube
        """
        try:
            # Realizar busca padrão de vídeos
            payload = {
                "q": q,
                **({"location": location} if location else {}),
                **({"gl": gl} if gl else {}),
                **({"hl": hl} if hl else {}),
                **({"num": num} if num else {}),
                **({"tbs": tbs} if tbs else {})
            }
            
            result = self._make_request("/videos", payload)
            
            # Filtrar apenas vídeos do YouTube
            if "videos" in result:
                result["videos"] = [v for v in result["videos"] 
                                   if "youtube.com" in v.get('link', '') or 
                                      "youtu.be" in v.get('link', '')]
            
            # Adicionar metadados adicionais
            result["platform"] = "YouTube"
            result["filtered"] = True
                                      
            return result
        except Exception as e:
            logger.error(f"Error in youtube_search: {e}")
            raise Exception(f"Failed to search for YouTube videos with '{q}': {e}")
    
    def instagram_search(self, q, location=None, gl=None, hl=None, num=None, tbs=None):
        """
        Busca exclusivamente vídeos do Instagram usando a API Serper.
        
        Args:
            q: Termo de busca
            location: Localização geográfica
            gl: Código de região do Google
            hl: Código de idioma
            num: Número de resultados
            tbs: Filtro de tempo (opcional)
            
        Returns:
            Resultados da busca filtrados para Instagram
        """
        try:
            # Realizar busca padrão de vídeos
            payload = {
                "q": q,
                **({"location": location} if location else {}),
                **({"gl": gl} if gl else {}),
                **({"hl": hl} if hl else {}),
                **({"num": num} if num else {}),
                **({"tbs": tbs} if tbs else {})
            }
            
            result = self._make_request("/videos", payload)
            
            # Filtrar apenas vídeos do Instagram
            if "videos" in result:
                result["videos"] = [v for v in result["videos"] 
                                   if "instagram.com" in v.get('link', '')]
            
            # Adicionar metadados adicionais
            result["platform"] = "Instagram"
            result["filtered"] = True
                                      
            return result
        except Exception as e:
            logger.error(f"Error in instagram_search: {e}")
            raise Exception(f"Failed to search for Instagram videos with '{q}': {e}")

    def maps_search(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Realiza uma busca de mapas usando a API Serper.
        
        Args:
            params: Parâmetros para a busca de mapas
            
        Returns:
            Resultados da busca de mapas
        """
        try:
            # Prepara o payload com os parâmetros necessários
            payload = {
                "q": params["q"]
            }
            
            # Adiciona parâmetros opcionais
            if "location" in params:
                payload["location"] = params["location"]
            if "gl" in params:
                payload["gl"] = params["gl"]
            if "hl" in params:
                payload["hl"] = params["hl"]
            if "num" in params:
                payload["num"] = params["num"]
                
            response = self._make_request("POST", "/maps", payload)
            return {"mapsResults": response}
        except Exception as e:
            logger.error(f"Error in maps_search: {e}")
            raise Exception(f"Failed to search for maps with query '{params.get('q')}': {e}")
    
    def reviews_search(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Realiza uma busca de avaliações usando a API Serper.
        
        Args:
            params: Parâmetros para a busca de avaliações
            
        Returns:
            Resultados da busca de avaliações
        """
        try:
            # Prepara o payload com os parâmetros necessários
            payload = {
                "q": params["q"]
            }
            
            # Adiciona parâmetros opcionais
            if "location" in params:
                payload["location"] = params["location"]
            if "gl" in params:
                payload["gl"] = params["gl"]
            if "hl" in params:
                payload["hl"] = params["hl"]
            if "num" in params:
                payload["num"] = params["num"]
                
            response = self._make_request("POST", "/reviews", payload)
            return {"reviewsResults": response}
        except Exception as e:
            logger.error(f"Error in reviews_search: {e}")
            raise Exception(f"Failed to search for reviews with query '{params.get('q')}': {e}")
    
    def shopping_search(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Realiza uma busca de produtos para compras usando a API Serper.
        
        Args:
            params: Parâmetros para a busca de produtos
            
        Returns:
            Resultados da busca de produtos
        """
        try:
            # Prepara o payload com os parâmetros necessários
            payload = {
                "q": params["q"]
            }
            
            # Adiciona parâmetros opcionais
            if "location" in params:
                payload["location"] = params["location"]
            if "gl" in params:
                payload["gl"] = params["gl"]
            if "hl" in params:
                payload["hl"] = params["hl"]
            if "num" in params:
                payload["num"] = params["num"]
                
            response = self._make_request("POST", "/shopping", payload)
            return {"shoppingResults": response}
        except Exception as e:
            logger.error(f"Error in shopping_search: {e}")
            raise Exception(f"Failed to search for products with query '{params.get('q')}': {e}")
    
    def lens_search(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Realiza uma busca por imagem (Google Lens) usando a API Serper.
        
        Args:
            params: Parâmetros para a busca por imagem
                image_url: URL da imagem para buscar
                
        Returns:
            Resultados da busca por imagem
        """
        try:
            # Prepara o payload com os parâmetros necessários
            payload = {
                "image_url": params["image_url"]
            }
            
            # Adiciona parâmetros opcionais
            if "location" in params:
                payload["location"] = params["location"]
            if "gl" in params:
                payload["gl"] = params["gl"]
            if "hl" in params:
                payload["hl"] = params["hl"]
                
            response = self._make_request("POST", "/lens", payload)
            return {"lensResults": response}
        except Exception as e:
            logger.error(f"Error in lens_search: {e}")
            raise Exception(f"Failed to search with image '{params.get('image_url')}': {e}")
    
    def scholar_search(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Realiza uma busca acadêmica (Google Scholar) usando a API Serper.
        
        Args:
            params: Parâmetros para a busca acadêmica
            
        Returns:
            Resultados da busca acadêmica
        """
        try:
            # Prepara o payload com os parâmetros necessários
            payload = {
                "q": params["q"]
            }
            
            # Adiciona parâmetros opcionais
            if "location" in params:
                payload["location"] = params["location"]
            if "gl" in params:
                payload["gl"] = params["gl"]
            if "hl" in params:
                payload["hl"] = params["hl"]
            if "num" in params:
                payload["num"] = params["num"]
            if "year_min" in params:
                payload["year_min"] = params["year_min"]
            if "year_max" in params:
                payload["year_max"] = params["year_max"]
                
            response = self._make_request("POST", "/scholar", payload)
            return {"scholarResults": response}
        except Exception as e:
            logger.error(f"Error in scholar_search: {e}")
            raise Exception(f"Failed to search for academic papers with query '{params.get('q')}': {e}")
    
    def patents_search(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Realiza uma busca de patentes usando a API Serper.
        
        Args:
            params: Parâmetros para a busca de patentes
            
        Returns:
            Resultados da busca de patentes
        """
        try:
            # Prepara o payload com os parâmetros necessários
            payload = {
                "q": params["q"]
            }
            
            # Adiciona parâmetros opcionais
            if "location" in params:
                payload["location"] = params["location"]
            if "gl" in params:
                payload["gl"] = params["gl"]
            if "hl" in params:
                payload["hl"] = params["hl"]
            if "num" in params:
                payload["num"] = params["num"]
            if "patent_office" in params:
                payload["patent_office"] = params["patent_office"]
                
            response = self._make_request("POST", "/patents", payload)
            return {"patentsResults": response}
        except Exception as e:
            logger.error(f"Error in patents_search: {e}")
            raise Exception(f"Failed to search for patents with query '{params.get('q')}': {e}")
    
    def webpage_search(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Realiza uma busca específica de uma página web usando a API Serper.
        
        Args:
            params: Parâmetros para a busca de página web
                url: URL da página web para buscar informações
                
        Returns:
            Resultados da busca de página web
        """
        try:
            # Prepara o payload com os parâmetros necessários
            payload = {
                "url": params["url"]
            }
            
            # Adiciona parâmetros opcionais
            if "extract_content" in params:
                payload["extract_content"] = params["extract_content"]
            if "extract_metadata" in params:
                payload["extract_metadata"] = params["extract_metadata"]
                
            response = self._make_request("POST", "/webpage", payload)
            return {"webpageResults": response}
        except Exception as e:
            logger.error(f"Error in webpage_search: {e}")
            raise Exception(f"Failed to get webpage information for '{params.get('url')}': {e}")
    
    def news_search(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Realiza uma busca de notícias usando a API Serper.
        
        Args:
            params: Parâmetros para a busca de notícias
            
        Returns:
            Resultados da busca de notícias
        """
        try:
            # Prepara o payload com os parâmetros necessários
            payload = {
                "q": params["q"]
            }
            
            # Adiciona parâmetros opcionais
            if "location" in params:
                payload["location"] = params["location"]
            if "gl" in params:
                payload["gl"] = params["gl"]
            if "hl" in params:
                payload["hl"] = params["hl"]
            if "num" in params:
                payload["num"] = params["num"]
            if "timerange" in params:
                payload["timerange"] = params["timerange"]
                
            response = self._make_request("POST", "/news", payload)
            return {"newsResults": response}
        except Exception as e:
            logger.error(f"Error in news_search: {e}")
            raise Exception(f"Failed to search for news with query '{params.get('q')}': {e}")
    
    def places_search(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Realiza uma busca de lugares usando a API Serper.
        
        Args:
            params: Parâmetros para a busca de lugares
            
        Returns:
            Resultados da busca de lugares
        """
        try:
            # Prepara o payload com os parâmetros necessários
            payload = {
                "q": params["q"]
            }
            
            # Adiciona parâmetros opcionais
            if "location" in params:
                payload["location"] = params["location"]
            if "gl" in params:
                payload["gl"] = params["gl"]
            if "hl" in params:
                payload["hl"] = params["hl"]
            if "num" in params:
                payload["num"] = params["num"]
                
            response = self._make_request("POST", "/places", payload)
            return {"placesResults": response}
        except Exception as e:
            logger.error(f"Error in places_search: {e}")
            raise Exception(f"Failed to search for places with query '{params.get('q')}': {e}")


class SerperSearchTools:
    """Implementação das ferramentas de busca para o servidor MCP."""
    
    def __init__(self, client: SerperClient):
        """
        Inicializa as ferramentas de busca com o cliente Serper.
        
        Args:
            client: Instância do cliente da API Serper
        """
        self.serper_client = client
        
    def search(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executa uma consulta de busca na web.
        
        Args:
            params: Parâmetros da consulta
            
        Returns:
            Resultados da busca
        """
        try:
            return self.serper_client.search(params)
        except Exception as e:
            raise Exception(f"SearchTool: failed to search for '{params.get('q')}'. {e}")
            
    def scrape(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executa uma operação de raspagem de web.
        
        Args:
            params: Parâmetros de raspagem
            
        Returns:
            Resultado da raspagem
        """
        try:
            return self.serper_client.scrape(params)
        except Exception as e:
            raise Exception(f"SearchTool: failed to scrape. {e}")
            
    def image_search(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executa uma busca por imagens.
        
        Args:
            params: Parâmetros da busca
            
        Returns:
            Resultados da busca de imagens
        """
        try:
            return self.serper_client.image_search(params)
        except Exception as e:
            raise Exception(f"SearchTool: failed to search images for '{params.get('q')}'. {e}")
            
    def health(self, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Executa uma verificação de saúde.
        
        Returns:
            Status de saúde
        """
        try:
            return self.serper_client.health(params)
        except Exception as e:
            raise Exception(f"SearchTool: health check failed. {e}")
            
    def analyze_serp(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analisa SERP para uma consulta.
        
        Args:
            params: Parâmetros de análise SERP
            
        Returns:
            Análise SERP
        """
        try:
            return self.serper_client.analyze_serp(params)
        except Exception as e:
            raise Exception(f"SearchTool: failed to analyze SERP for '{params.get('query')}'. {e}")
            
    def research_keywords(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Pesquisa palavras-chave relacionadas a uma palavra-chave semente.
        
        Args:
            params: Parâmetros de pesquisa de palavras-chave
            
        Returns:
            Dados de pesquisa de palavras-chave
        """
        try:
            return self.serper_client.research_keywords(params)
        except Exception as e:
            raise Exception(f"SearchTool: failed to research keywords for '{params.get('keyword')}'. {e}")
            
    def analyze_competitors(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analisa concorrentes para um domínio/palavra-chave.
        
        Args:
            params: Parâmetros de análise de concorrentes
            
        Returns:
            Dados de análise de concorrentes
        """
        try:
            return self.serper_client.analyze_competitors(params)
        except Exception as e:
            raise Exception(f"SearchTool: failed to analyze competitors for '{params.get('domain')}'. {e}")
            
    def autocomplete(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Obtém sugestões de autocompletar para múltiplas consultas.
        
        Args:
            params: Parâmetros para autocompletar
                queries: Lista de consultas para autocompletar
                location: Local para resultados de busca (opcional)
                gl: Código do país (opcional)
                hl: Código de idioma (opcional)
            
        Returns:
            Sugestões de autocompletar para cada consulta
        """
        try:
            queries = params.get("queries", [])
            location = params.get("location", "")
            gl = params.get("gl", "us")
            hl = params.get("hl", "en")
            
            if not queries:
                raise ValueError("No queries provided for autocomplete")
                
            # Formata as consultas para o formato esperado pela API
            query_list = []
            for q in queries:
                query_item = {
                    "q": q,
                    "gl": gl,
                    "hl": hl
                }
                if location:
                    query_item["location"] = location
                    
                query_list.append(query_item)
                
            # Faz a requisição para o endpoint de autocompletar
            return self.serper_client.autocomplete(query_list)
        except Exception as e:
            raise Exception(f"SearchTool: failed to get autocomplete suggestions. {e}")

    def video_search(self, query, location=None, gl=None, hl=None, num=None):
        """Search for videos using the Serper API."""
        return self.serper_client.video_search(query, location, gl, hl, num)

    def youtube_search(self, q, location=None, gl=None, hl=None, num=None, tbs=None):
        """
        Busca exclusivamente vídeos do YouTube usando a API Serper.
        
        Args:
            q: Termo de busca
            location: Localização geográfica
            gl: Código de região do Google
            hl: Código de idioma
            num: Número de resultados
            tbs: Filtro de tempo (opcional)
            
        Returns:
            Resultados da busca filtrados para YouTube
        """
        return self.serper_client.youtube_search(q, location, gl, hl, num, tbs)
    
    def instagram_search(self, q, location=None, gl=None, hl=None, num=None, tbs=None):
        """
        Busca exclusivamente vídeos do Instagram usando a API Serper.
        
        Args:
            q: Termo de busca
            location: Localização geográfica
            gl: Código de região do Google
            hl: Código de idioma
            num: Número de resultados
            tbs: Filtro de tempo (opcional)
            
        Returns:
            Resultados da busca filtrados para Instagram
        """
        return self.serper_client.instagram_search(q, location, gl, hl, num, tbs)

    def maps_search(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executa uma busca de mapas.
        
        Args:
            params: Parâmetros da busca
            
        Returns:
            Resultados da busca de mapas
        """
        try:
            return self.serper_client.maps_search(params)
        except Exception as e:
            raise Exception(f"SearchTool: failed to search maps for '{params.get('q')}'. {e}")
    
    def reviews_search(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executa uma busca de avaliações.
        
        Args:
            params: Parâmetros da busca
            
        Returns:
            Resultados da busca de avaliações
        """
        try:
            return self.serper_client.reviews_search(params)
        except Exception as e:
            raise Exception(f"SearchTool: failed to search reviews for '{params.get('q')}'. {e}")
    
    def shopping_search(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executa uma busca de produtos para compras.
        
        Args:
            params: Parâmetros da busca
            
        Returns:
            Resultados da busca de produtos
        """
        try:
            return self.serper_client.shopping_search(params)
        except Exception as e:
            raise Exception(f"SearchTool: failed to search shopping for '{params.get('q')}'. {e}")
    
    def lens_search(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executa uma busca por imagem (Google Lens).
        
        Args:
            params: Parâmetros da busca
            
        Returns:
            Resultados da busca por imagem
        """
        try:
            return self.serper_client.lens_search(params)
        except Exception as e:
            raise Exception(f"SearchTool: failed to search with image '{params.get('image_url')}'. {e}")
    
    def scholar_search(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executa uma busca acadêmica (Google Scholar).
        
        Args:
            params: Parâmetros da busca
            
        Returns:
            Resultados da busca acadêmica
        """
        try:
            return self.serper_client.scholar_search(params)
        except Exception as e:
            raise Exception(f"SearchTool: failed to search scholar for '{params.get('q')}'. {e}")
    
    def patents_search(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executa uma busca de patentes.
        
        Args:
            params: Parâmetros da busca
            
        Returns:
            Resultados da busca de patentes
        """
        try:
            return self.serper_client.patents_search(params)
        except Exception as e:
            raise Exception(f"SearchTool: failed to search patents for '{params.get('q')}'. {e}")
    
    def webpage_search(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executa uma busca específica de uma página web.
        
        Args:
            params: Parâmetros da busca
            
        Returns:
            Resultados da busca de página web
        """
        try:
            return self.serper_client.webpage_search(params)
        except Exception as e:
            raise Exception(f"SearchTool: failed to get webpage information for '{params.get('url')}'. {e}")
    
    def news_search(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executa uma busca de notícias.
        
        Args:
            params: Parâmetros da busca
            
        Returns:
            Resultados da busca de notícias
        """
        try:
            return self.serper_client.news_search(params)
        except Exception as e:
            raise Exception(f"SearchTool: failed to search news for '{params.get('q')}'. {e}")
    
    def places_search(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Executa uma busca de lugares.
        
        Args:
            params: Parâmetros da busca
            
        Returns:
            Resultados da busca de lugares
        """
        try:
            return self.serper_client.places_search(params)
        except Exception as e:
            raise Exception(f"SearchTool: failed to search places for '{params.get('q')}'. {e}")


# Inicializa cliente Serper com a chave da API do ambiente
serper_api_key = os.environ.get("SERPER_API_KEY")
if not serper_api_key:
    raise ValueError("SERPER_API_KEY environment variable is required")

# Cria cliente Serper, ferramentas de busca
serper_client = SerperClient(serper_api_key)
search_tools = SerperSearchTools(serper_client)

# Definições das ferramentas disponíveis
tools_definitions = {
    "google_search": {
        "description": "Ferramenta para realizar buscas na web via API Serper e recuperar resultados completos. Capaz de recuperar resultados orgânicos de busca, pessoas também perguntam, buscas relacionadas e gráfico de conhecimento.",
        "parameters": {
            "q": {
                "description": "String de consulta de busca (ex: 'inteligência artificial', 'soluções para mudanças climáticas')",
                "type": "string"
            },
            "gl": {
                "description": "Código de região opcional para resultados da busca no formato ISO 3166-1 alpha-2 (ex: 'us', 'br', 'pt')",
                "type": "string"
            },
            "hl": {
                "description": "Código de idioma opcional para resultados da busca no formato ISO 639-1 (ex: 'en', 'pt', 'es')",
                "type": "string"
            },
            "location": {
                "description": "Localização opcional para resultados da busca (ex: 'São Paulo, Brasil', 'Rio de Janeiro, Brasil')",
                "type": "string"
            },
            "num": {
                "description": "Número de resultados a retornar (padrão: 10)",
                "type": "number"
            },
            "tbs": {
                "description": "Filtro de busca baseado em tempo ('qdr:h' para última hora, 'qdr:d' para último dia, 'qdr:w' para última semana, 'qdr:m' para último mês, 'qdr:y' para último ano)",
                "type": "string"
            },
            "page": {
                "description": "Número da página de resultados a retornar (padrão: 1)",
                "type": "number"
            },
            "autocorrect": {
                "description": "Se deve corrigir automaticamente a ortografia na consulta",
                "type": "boolean"
            },
            # Operadores avançados de busca
            "site": {
                "description": "Limitar resultados a domínio específico (ex: 'github.com', 'wikipedia.org')",
                "type": "string"
            },
            "filetype": {
                "description": "Limitar a tipos específicos de arquivo (ex: 'pdf', 'doc', 'xls')",
                "type": "string"
            },
            "inurl": {
                "description": "Buscar páginas com palavra na URL (ex: 'download', 'tutorial')",
                "type": "string"
            },
            "intitle": {
                "description": "Buscar páginas com palavra no título (ex: 'avaliação', 'como fazer')",
                "type": "string"
            },
            "related": {
                "description": "Encontrar sites similares (ex: 'github.com', 'stackoverflow.com')",
                "type": "string"
            },
            "cache": {
                "description": "Ver versão em cache do Google de uma URL específica (ex: 'example.com/page')",
                "type": "string"
            },
            "before": {
                "description": "Data antes no formato AAAA-MM-DD (ex: '2024-01-01')",
                "type": "string"
            },
            "after": {
                "description": "Data depois no formato AAAA-MM-DD (ex: '2023-01-01')",
                "type": "string"
            },
            "exact": {
                "description": "Correspondência exata de frase (ex: 'aprendizado de máquina', 'computação quântica')",
                "type": "string"
            },
            "exclude": {
                "description": "Termos a excluir dos resultados de busca como string separada por vírgula (ex: 'spam,anúncios', 'iniciante,básico')",
                "type": "string"
            },
            "or": {
                "description": "Termos alternativos como string separada por vírgula (ex: 'tutorial,guia,curso', 'documentação,manual')",
                "type": "string"
            }
        }
    },
    "scrape": {
        "description": "Ferramenta para extrair o conteúdo de uma página web e recuperar o texto e, opcionalmente, o conteúdo em markdown. Também recupera os metadados JSON-LD e os metadados do cabeçalho.",
        "parameters": {
            "url": {
                "description": "A URL da página web para extrair",
                "type": "string"
            },
            "includeMarkdown": {
                "description": "Se deve incluir conteúdo em markdown",
                "type": "boolean",
                "default": False
            }
        }
    },
    "_health": {
        "description": "Endpoint de verificação de saúde",
        "parameters": {
            "random_string": {
                "description": "Parâmetro fictício para ferramentas sem parâmetros",
                "type": "string"
            }
        }
    },
    "analyze_serp": {
        "description": "Analisar uma SERP (Página de Resultados de Busca) para uma consulta específica",
        "parameters": {
            "query": {
                "description": "Consulta de busca a ser analisada",
                "type": "string"
            },
            "gl": {
                "description": "Código de região para resultados da busca",
                "type": "string",
                "default": "us"
            },
            "hl": {
                "description": "Código de idioma para resultados da busca",
                "type": "string",
                "default": "en"
            },
            "google_domain": {
                "description": "Domínio do Google a ser usado para a busca",
                "type": "string",
                "default": "google.com"
            },
            "num": {
                "description": "Número de resultados a analisar",
                "type": "number",
                "default": 10
            },
            "device": {
                "description": "Tipo de dispositivo para emular (desktop ou mobile)",
                "type": "string",
                "enum": ["desktop", "mobile"],
                "default": "desktop"
            },
            "location": {
                "description": "Localização específica para resultados localizados",
                "type": "string"
            },
            "safe": {
                "description": "Modo de pesquisa segura (ativo ou desativado)",
                "type": "string",
                "enum": ["active", "off"]
            }
        }
    },
    "research_keywords": {
        "description": "Pesquisar palavras-chave relacionadas a um tópico ou palavra-chave inicial",
        "parameters": {
            "keyword": {
                "description": "Palavra-chave semente para pesquisa",
                "type": "string"
            },
            "language": {
                "description": "Idioma para resultados de palavras-chave",
                "type": "string"
            },
            "location": {
                "description": "Localização para resultados de palavras-chave",
                "type": "string"
            },
            "include_questions": {
                "description": "Incluir perguntas relacionadas nos resultados",
                "type": "boolean",
                "default": False
            },
            "include_related": {
                "description": "Incluir termos relacionados nos resultados",
                "type": "boolean",
                "default": False
            },
            "include_suggestions": {
                "description": "Incluir sugestões de palavras-chave nos resultados",
                "type": "boolean",
                "default": False
            }
        }
    },
    "analyze_competitors": {
        "description": "Analisar concorrentes para uma palavra-chave ou domínio específico",
        "parameters": {
            "domain": {
                "description": "Domínio para analisar concorrentes",
                "type": "string"
            },
            "keyword": {
                "description": "Palavra-chave opcional para focar a análise",
                "type": "string"
            },
            "include_features": {
                "description": "Incluir recursos detalhados dos concorrentes",
                "type": "boolean"
            },
            "num_results": {
                "description": "Número de concorrentes a analisar",
                "type": "number"
            }
        }
    },
    "autocomplete": {
        "description": "Obter sugestões de autocompletar para múltiplas consultas de uma vez",
        "parameters": {
            "queries": {
                "description": "Lista de consultas de busca para obter sugestões de autocompletar",
                "type": "array",
                "items": {
                    "type": "string"
                }
            },
            "location": {
                "description": "Localização para resultados de busca (ex: 'Brasil', 'Estados Unidos')",
                "type": "string"
            },
            "gl": {
                "description": "Código de país (ex: 'br', 'us')",
                "type": "string"
            },
            "hl": {
                "description": "Código de idioma (ex: 'pt-br', 'en')",
                "type": "string"
            }
        },
        "required": ["queries"]
    },
    "maps_search": {
        "description": "Ferramenta para buscar mapas e locais usando a API Serper.",
        "parameters": {
            "q": {
                "description": "String de consulta para mapas (ex: 'restaurantes em São Paulo', 'parques em Lisboa')",
                "type": "string"
            },
            "gl": {
                "description": "Código de região opcional para resultados de mapas no formato ISO 3166-1 alpha-2 (ex: 'us', 'br', 'pt')",
                "type": "string"
            },
            "hl": {
                "description": "Código de idioma opcional para resultados de mapas no formato ISO 639-1 (ex: 'en', 'pt', 'es')",
                "type": "string"
            },
            "location": {
                "description": "Localização opcional para resultados de mapas (ex: 'São Paulo, SP', 'Lisboa, Portugal')",
                "type": "string"
            },
            "num": {
                "description": "Número de resultados de mapas a retornar (padrão: 10)",
                "type": "number"
            }
        },
        "required": ["q"]
    },
    "reviews_search": {
        "description": "Ferramenta para buscar avaliações usando a API Serper.",
        "parameters": {
            "q": {
                "description": "String de consulta para avaliações (ex: 'avaliações iPhone 13', 'avaliações de hotéis em Paris')",
                "type": "string"
            },
            "gl": {
                "description": "Código de região opcional para resultados de avaliações no formato ISO 3166-1 alpha-2 (ex: 'us', 'br', 'pt')",
                "type": "string"
            },
            "hl": {
                "description": "Código de idioma opcional para resultados de avaliações no formato ISO 639-1 (ex: 'en', 'pt', 'es')",
                "type": "string"
            },
            "location": {
                "description": "Localização opcional para resultados de avaliações (ex: 'São Paulo, SP', 'Lisboa, Portugal')",
                "type": "string"
            },
            "num": {
                "description": "Número de avaliações a retornar (padrão: 10)",
                "type": "number"
            }
        },
        "required": ["q"]
    },
    "shopping_search": {
        "description": "Ferramenta para buscar produtos e informações de compras usando a API Serper.",
        "parameters": {
            "q": {
                "description": "String de consulta para produtos (ex: 'melhores smartphones 2024', 'tênis de corrida')",
                "type": "string"
            },
            "gl": {
                "description": "Código de região opcional para resultados de produtos no formato ISO 3166-1 alpha-2 (ex: 'us', 'br', 'pt')",
                "type": "string"
            },
            "hl": {
                "description": "Código de idioma opcional para resultados de produtos no formato ISO 639-1 (ex: 'en', 'pt', 'es')",
                "type": "string"
            },
            "location": {
                "description": "Localização opcional para resultados de produtos (ex: 'São Paulo, SP', 'Lisboa, Portugal')",
                "type": "string"
            },
            "num": {
                "description": "Número de produtos a retornar (padrão: 10)",
                "type": "number"
            }
        },
        "required": ["q"]
    },
    "lens_search": {
        "description": "Ferramenta para buscar informações sobre uma imagem usando o Google Lens via API Serper.",
        "parameters": {
            "image_url": {
                "description": "URL da imagem para buscar (deve ser uma URL de imagem publicamente acessível)",
                "type": "string"
            },
            "gl": {
                "description": "Código de região opcional para resultados no formato ISO 3166-1 alpha-2 (ex: 'us', 'br', 'pt')",
                "type": "string"
            },
            "hl": {
                "description": "Código de idioma opcional para resultados no formato ISO 639-1 (ex: 'en', 'pt', 'es')",
                "type": "string"
            },
            "location": {
                "description": "Localização opcional para resultados (ex: 'São Paulo, SP', 'Lisboa, Portugal')",
                "type": "string"
            }
        },
        "required": ["image_url"]
    },
    "scholar_search": {
        "description": "Ferramenta para buscar artigos acadêmicos e informações escolares usando a API Serper.",
        "parameters": {
            "q": {
                "description": "String de consulta para artigos acadêmicos (ex: 'avanços em aprendizado de máquina', 'pesquisa sobre mudanças climáticas')",
                "type": "string"
            },
            "gl": {
                "description": "Código de região opcional para resultados acadêmicos no formato ISO 3166-1 alpha-2 (ex: 'us', 'br', 'pt')",
                "type": "string"
            },
            "hl": {
                "description": "Código de idioma opcional para resultados acadêmicos no formato ISO 639-1 (ex: 'en', 'pt', 'es')",
                "type": "string"
            },
            "location": {
                "description": "Localização opcional para resultados acadêmicos (ex: 'São Paulo, SP', 'Lisboa, Portugal')",
                "type": "string"
            },
            "num": {
                "description": "Número de artigos acadêmicos a retornar (padrão: 10)",
                "type": "number"
            },
            "year_min": {
                "description": "Ano mínimo de publicação para filtrar resultados (ex: 2020)",
                "type": "number"
            },
            "year_max": {
                "description": "Ano máximo de publicação para filtrar resultados (ex: 2023)",
                "type": "number"
            }
        },
        "required": ["q"]
    },
    "patents_search": {
        "description": "Ferramenta para buscar informações sobre patentes usando a API Serper.",
        "parameters": {
            "q": {
                "description": "String de consulta para patentes (ex: 'patentes de inteligência artificial', 'carregamento de veículos elétricos')",
                "type": "string"
            },
            "gl": {
                "description": "Código de região opcional para resultados de patentes no formato ISO 3166-1 alpha-2 (ex: 'us', 'br', 'pt')",
                "type": "string"
            },
            "hl": {
                "description": "Código de idioma opcional para resultados de patentes no formato ISO 639-1 (ex: 'en', 'pt', 'es')",
                "type": "string"
            },
            "location": {
                "description": "Localização opcional para resultados de patentes (ex: 'São Paulo, SP', 'Lisboa, Portugal')",
                "type": "string"
            },
            "num": {
                "description": "Número de patentes a retornar (padrão: 10)",
                "type": "number"
            },
            "patent_office": {
                "description": "Escritório de patentes para pesquisar (ex: 'USPTO', 'EPO', 'WIPO')",
                "type": "string"
            }
        },
        "required": ["q"]
    },
    "webpage_search": {
        "description": "Ferramenta para obter informações detalhadas sobre uma página web específica usando a API Serper.",
        "parameters": {
            "url": {
                "description": "URL da página web para analisar (deve ser uma URL publicamente acessível)",
                "type": "string"
            },
            "extract_content": {
                "description": "Se deve extrair o conteúdo principal da página web (padrão: true)",
                "type": "boolean"
            },
            "extract_metadata": {
                "description": "Se deve extrair metadados da página web (padrão: true)",
                "type": "boolean"
            }
        },
        "required": ["url"]
    },
    "news_search": {
        "description": "Ferramenta para buscar artigos de notícias usando a API Serper.",
        "parameters": {
            "q": {
                "description": "String de consulta para artigos de notícias (ex: 'últimas notícias de tecnologia', 'atualizações covid-19')",
                "type": "string"
            },
            "gl": {
                "description": "Código de região opcional para resultados de notícias no formato ISO 3166-1 alpha-2 (ex: 'us', 'br', 'pt')",
                "type": "string"
            },
            "hl": {
                "description": "Código de idioma opcional para resultados de notícias no formato ISO 639-1 (ex: 'en', 'pt', 'es')",
                "type": "string"
            },
            "location": {
                "description": "Localização opcional para resultados de notícias (ex: 'São Paulo, SP', 'Lisboa, Portugal')",
                "type": "string"
            },
            "num": {
                "description": "Número de artigos de notícias a retornar (padrão: 10)",
                "type": "number"
            },
            "timerange": {
                "description": "Intervalo de tempo para artigos de notícias (ex: 'd' para dia, 'w' para semana, 'm' para mês)",
                "type": "string"
            }
        },
        "required": ["q"]
    },
    "places_search": {
        "description": "Ferramenta para buscar lugares e localizações usando a API Serper.",
        "parameters": {
            "q": {
                "description": "String de consulta para lugares (ex: 'restaurantes perto de mim', 'parques em São Francisco')",
                "type": "string"
            },
            "gl": {
                "description": "Código de região opcional para resultados de lugares no formato ISO 3166-1 alpha-2 (ex: 'us', 'br', 'pt')",
                "type": "string"
            },
            "hl": {
                "description": "Código de idioma opcional para resultados de lugares no formato ISO 639-1 (ex: 'en', 'pt', 'es')",
                "type": "string"
            },
            "location": {
                "description": "Localização opcional para resultados de lugares (ex: 'São Paulo, SP', 'Lisboa, Portugal')",
                "type": "string"
            },
            "num": {
                "description": "Número de lugares a retornar (padrão: 10)",
                "type": "number"
            }
        },
        "required": ["q"]
    },
    "youtube_search": {
        "description": "Ferramenta para buscar vídeos especificamente do YouTube usando a API Serper.",
        "parameters": {
            "q": {
                "description": "String de consulta para vídeos do YouTube (ex: 'tutoriais de programação', 'músicas de relaxamento')",
                "type": "string"
            },
            "gl": {
                "description": "Código de região opcional para resultados do YouTube no formato ISO 3166-1 alpha-2 (ex: 'us', 'br', 'pt')",
                "type": "string"
            },
            "hl": {
                "description": "Código de idioma opcional para resultados do YouTube no formato ISO 639-1 (ex: 'en', 'pt', 'es')",
                "type": "string"
            },
            "location": {
                "description": "Localização opcional para resultados do YouTube (ex: 'São Paulo, SP', 'Lisboa, Portugal')",
                "type": "string"
            },
            "num": {
                "description": "Número de vídeos do YouTube a retornar (padrão: 10)",
                "type": "number"
            },
            "tbs": {
                "description": "Filtro de tempo opcional para vídeos do YouTube (ex: 'qdr:h' para última hora, 'qdr:d' para último dia, 'qdr:w' para última semana, 'qdr:m' para último mês, 'qdr:y' para último ano)",
                "type": "string"
            }
        },
        "required": ["q"]
    },
    "instagram_search": {
        "description": "Ferramenta para buscar conteúdo especificamente do Instagram usando a API Serper.",
        "parameters": {
            "q": {
                "description": "String de consulta para conteúdo do Instagram (ex: 'fotografias de natureza', 'receitas de cozinha')",
                "type": "string"
            },
            "gl": {
                "description": "Código de região opcional para resultados do Instagram no formato ISO 3166-1 alpha-2 (ex: 'us', 'br', 'pt')",
                "type": "string"
            },
            "hl": {
                "description": "Código de idioma opcional para resultados do Instagram no formato ISO 639-1 (ex: 'en', 'pt', 'es')",
                "type": "string"
            },
            "location": {
                "description": "Localização opcional para resultados do Instagram (ex: 'São Paulo, SP', 'Lisboa, Portugal')",
                "type": "string"
            },
            "num": {
                "description": "Número de resultados do Instagram a retornar (padrão: 10)",
                "type": "number"
            },
            "tbs": {
                "description": "Filtro de tempo opcional para resultados do Instagram (ex: 'qdr:h' para última hora, 'qdr:d' para último dia, 'qdr:w' para última semana, 'qdr:m' para último mês, 'qdr:y' para último ano)",
                "type": "string"
            }
        },
        "required": ["q"]
    }
}

# Protocolo MCP por stdio
def handle_message(message: Dict[Any, Any]) -> Dict[Any, Any]:
    """Trata mensagens MCP recebidas."""
    try:
        method = message.get("method")
        if not method:
            return {"error": {"message": "Nenhum método especificado"}}

        message_id = message.get("id")
        
        # Manipulador ListTools
        if method == "mcp.ListTools":
            return {
                "id": message_id,
                "result": {
                    "tools": tools_definitions
                }
            }
            
        # Manipulador CallTool
        elif method == "mcp.CallTool":
            params = message.get("params", {})
            tool_name = params.get("name")
            arguments = params.get("arguments", {})
            
            if tool_name == "google_search":
                result = search_tools.search(arguments)
                return {
                    "id": message_id,
                    "result": {
                        "content": [
                            {"type": "text", "text": json.dumps(result, ensure_ascii=False)}
                        ]
                    }
                }
                
            elif tool_name == "scrape":
                result = search_tools.scrape(arguments)
                return {
                    "id": message_id,
                    "result": {
                        "content": [
                            {"type": "text", "text": json.dumps(result, ensure_ascii=False)}
                        ]
                    }
                }
                
            elif tool_name == "_health":
                result = search_tools.health(arguments)
                return {
                    "id": message_id,
                    "result": {
                        "content": [
                            {"type": "text", "text": json.dumps(result, ensure_ascii=False)}
                        ]
                    }
                }
                
            elif tool_name == "analyze_serp":
                result = search_tools.analyze_serp(arguments)
                return {
                    "id": message_id,
                    "result": {
                        "content": [
                            {"type": "text", "text": json.dumps(result, ensure_ascii=False)}
                        ]
                    }
                }
                
            elif tool_name == "research_keywords":
                result = search_tools.research_keywords(arguments)
                return {
                    "id": message_id,
                    "result": {
                        "content": [
                            {"type": "text", "text": json.dumps(result, ensure_ascii=False)}
                        ]
                    }
                }
                
            elif tool_name == "analyze_competitors":
                result = search_tools.analyze_competitors(arguments)
                return {
                    "id": message_id,
                    "result": {
                        "content": [
                            {"type": "text", "text": json.dumps(result, ensure_ascii=False)}
                        ]
                    }
                }
                
            elif tool_name == "autocomplete":
                result = search_tools.autocomplete(arguments)
                return {
                    "id": message_id,
                    "result": {
                        "content": [
                            {"type": "text", "text": json.dumps(result, ensure_ascii=False)}
                        ]
                    }
                }
                
            elif tool_name == "image_search":
                result = search_tools.image_search(arguments)
                return {
                    "id": message_id,
                    "result": {
                        "content": [
                            {"type": "text", "text": json.dumps(result, ensure_ascii=False)}
                        ]
                    }
                }
                
            elif tool_name == "video_search":
                result = search_tools.video_search(**arguments)
                return {
                    "id": message_id,
                    "result": {
                        "content": [
                            {"type": "text", "text": json.dumps(result, ensure_ascii=False)}
                        ]
                    }
                }
                
            elif tool_name == "youtube_search":
                result = search_tools.youtube_search(**arguments)
                return {
                    "id": message_id,
                    "result": {
                        "content": [
                            {"type": "text", "text": json.dumps(result, ensure_ascii=False)}
                        ]
                    }
                }
                
            elif tool_name == "instagram_search":
                result = search_tools.instagram_search(**arguments)
                return {
                    "id": message_id,
                    "result": {
                        "content": [
                            {"type": "text", "text": json.dumps(result, ensure_ascii=False)}
                        ]
                    }
                }
                
            elif tool_name == "maps_search":
                result = search_tools.maps_search(arguments)
                return {
                    "id": message_id,
                    "result": {
                        "content": [
                            {"type": "text", "text": json.dumps(result, ensure_ascii=False)}
                        ]
                    }
                }
                
            elif tool_name == "reviews_search":
                result = search_tools.reviews_search(arguments)
                return {
                    "id": message_id,
                    "result": {
                        "content": [
                            {"type": "text", "text": json.dumps(result, ensure_ascii=False)}
                        ]
                    }
                }
                
            elif tool_name == "shopping_search":
                result = search_tools.shopping_search(arguments)
                return {
                    "id": message_id,
                    "result": {
                        "content": [
                            {"type": "text", "text": json.dumps(result, ensure_ascii=False)}
                        ]
                    }
                }
                
            elif tool_name == "lens_search":
                result = search_tools.lens_search(arguments)
                return {
                    "id": message_id,
                    "result": {
                        "content": [
                            {"type": "text", "text": json.dumps(result, ensure_ascii=False)}
                        ]
                    }
                }
                
            elif tool_name == "scholar_search":
                result = search_tools.scholar_search(arguments)
                return {
                    "id": message_id,
                    "result": {
                        "content": [
                            {"type": "text", "text": json.dumps(result, ensure_ascii=False)}
                        ]
                    }
                }
                
            elif tool_name == "patents_search":
                result = search_tools.patents_search(arguments)
                return {
                    "id": message_id,
                    "result": {
                        "content": [
                            {"type": "text", "text": json.dumps(result, ensure_ascii=False)}
                        ]
                    }
                }
                
            elif tool_name == "webpage_search":
                result = search_tools.webpage_search(arguments)
                return {
                    "id": message_id,
                    "result": {
                        "content": [
                            {"type": "text", "text": json.dumps(result, ensure_ascii=False)}
                        ]
                    }
                }
                
            elif tool_name == "news_search":
                result = search_tools.news_search(arguments)
                return {
                    "id": message_id,
                    "result": {
                        "content": [
                            {"type": "text", "text": json.dumps(result, ensure_ascii=False)}
                        ]
                    }
                }
                
            elif tool_name == "places_search":
                result = search_tools.places_search(arguments)
                return {
                    "id": message_id,
                    "result": {
                        "content": [
                            {"type": "text", "text": json.dumps(result, ensure_ascii=False)}
                        ]
                    }
                }
                
            else:
                return {
                    "id": message_id,
                    "error": {
                        "message": f"Ferramenta desconhecida: {tool_name}"
                    }
                }
        else:
            # Lidando com outros métodos (ListPrompts, GetPrompt, etc.)
            return {
                "id": message_id,
                "error": {
                    "message": f"Método não implementado: {method}"
                }
            }
            
    except Exception as e:
        logger.error(f"Erro ao manipular mensagem: {e}", exc_info=True)
        return {
            "id": message.get("id"),
            "error": {
                "message": f"Erro interno do servidor: {str(e)}"
            }
        }

def main():
    """Main function to run the MCP server."""
    logger.info("Starting Serper MCP Server in Python")
    
    try:
        # Loop for stdin/stdout communication
        for line in sys.stdin:
            try:
                message = json.loads(line)
                response = handle_message(message)
                
                # Send response
                json_response = json.dumps(response)
                sys.stdout.write(json_response + "\n")
                sys.stdout.flush()
                
            except json.JSONDecodeError:
                logger.error(f"Failed to parse message: {line}")
                continue
    except KeyboardInterrupt:
        logger.info("Shutting down Serper MCP Server")
        sys.exit(0)

if __name__ == "__main__":
    main()