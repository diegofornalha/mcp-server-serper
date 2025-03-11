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
        "description": "Tool to perform web searches via Serper API and retrieve rich results. It is able to retrieve organic search results, people also ask, related searches, and knowledge graph.",
        "parameters": {
            "q": {
                "description": "Search query string (e.g., 'artificial intelligence', 'climate change solutions')",
                "type": "string"
            },
            "gl": {
                "description": "Optional region code for search results in ISO 3166-1 alpha-2 format (e.g., 'us', 'gb', 'de')",
                "type": "string"
            },
            "hl": {
                "description": "Optional language code for search results in ISO 639-1 format (e.g., 'en', 'es', 'fr')",
                "type": "string"
            },
            "num": {
                "type": "number",
                "description": "Number of results to return (default: 10)"
            },
            "page": {
                "type": "number",
                "description": "Page number of results to return (default: 1)"
            },
            "location": {
                "type": "string",
                "description": "Optional location for search results (e.g., 'SoHo, New York, United States', 'California, United States')"
            },
            "site": {
                "type": "string",
                "description": "Limit results to specific domain (e.g., 'github.com', 'wikipedia.org')"
            },
            "related": {
                "type": "string",
                "description": "Find similar websites (e.g., 'github.com', 'stackoverflow.com')"
            },
            "tbs": {
                "type": "string",
                "description": "Time-based search filter ('qdr:h' for past hour, 'qdr:d' for past day, 'qdr:w' for past week, 'qdr:m' for past month, 'qdr:y' for past year)"
            },
            "intitle": {
                "type": "string",
                "description": "Search for pages with word in title (e.g., 'review', 'how to')"
            },
            "inurl": {
                "type": "string",
                "description": "Search for pages with word in URL (e.g., 'download', 'tutorial')"
            },
            "filetype": {
                "type": "string",
                "description": "Limit to specific file types (e.g., 'pdf', 'doc', 'xls')"
            },
            "or": {
                "type": "string",
                "description": "Alternative terms as comma-separated string (e.g., 'tutorial,guide,course', 'documentation,manual')"
            },
            "exclude": {
                "type": "string",
                "description": "Terms to exclude from search results as comma-separated string (e.g., 'spam,ads', 'beginner,basic')"
            },
            "exact": {
                "type": "string",
                "description": "Exact phrase match (e.g., 'machine learning', 'quantum computing')"
            },
            "cache": {
                "type": "string", 
                "description": "View Google's cached version of a specific URL (e.g., 'example.com/page')"
            },
            "before": {
                "type": "string",
                "description": "Date before in YYYY-MM-DD format (e.g., '2024-01-01')"
            },
            "after": {
                "type": "string",
                "description": "Date after in YYYY-MM-DD format (e.g., '2023-01-01')"
            },
            "autocorrect": {
                "type": "boolean",
                "description": "Whether to autocorrect spelling in query"
            }
        },
        "required": ["q", "gl", "hl"]
    },
    "scrape": {
        "description": "Tool to scrape a webpage and retrieve the text and, optionally, the markdown content. It will retrieve also the JSON-LD metadata and the head metadata.",
        "parameters": {
            "url": {
                "description": "The URL of the webpage to scrape.",
                "type": "string"
            },
            "includeMarkdown": {
                "description": "Whether to include markdown content.",
                "type": "boolean",
                "default": False
            }
        },
        "required": ["url"]
    },
    "image_search": {
        "description": "Tool to search for images via Serper API and retrieve results including thumbnails and source information.",
        "parameters": {
            "q": {
                "type": "string",
                "description": "Search query string for image search (e.g., 'sunset over mountains', 'cats playing')"
            },
            "gl": {
                "type": "string",
                "description": "Optional region code for image results in ISO 3166-1 alpha-2 format (e.g., 'us', 'gb', 'de')"
            },
            "hl": {
                "type": "string",
                "description": "Optional language code for image results in ISO 639-1 format (e.g., 'en', 'es', 'fr')"
            },
            "num": {
                "type": "number",
                "description": "Number of image results to return (default: 10)"
            },
            "location": {
                "type": "string",
                "description": "Optional location for image results (e.g., 'New York, United States', 'Paris, France')"
            }
        },
        "required": ["q"]
    },
    "_health": {
        "description": "Health check endpoint",
        "parameters": {
            "random_string": {
                "description": "Dummy parameter for no-parameter tools",
                "type": "string"
            }
        },
        "required": ["random_string"]
    },
    "analyze_serp": {
        "description": "Analyze a SERP (Search Engine Results Page) for a given query",
        "parameters": {
            "query": {
                "type": "string"
            },
            "gl": {
                "type": "string",
                "default": "us"
            },
            "hl": {
                "type": "string",
                "default": "en"
            },
            "google_domain": {
                "type": "string",
                "default": "google.com"
            },
            "num": {
                "type": "number",
                "minimum": 1,
                "maximum": 100,
                "default": 10
            },
            "device": {
                "type": "string",
                "enum": ["desktop", "mobile"],
                "default": "desktop"
            },
            "location": {
                "type": "string"
            },
            "safe": {
                "type": "string",
                "enum": ["active", "off"]
            }
        },
        "required": ["query"]
    },
    "research_keywords": {
        "description": "Research keywords related to a given topic or seed keyword",
        "parameters": {
            "keyword": {
                "type": "string"
            },
            "language": {
                "type": "string"
            },
            "location": {
                "type": "string"
            },
            "include_questions": {
                "type": "boolean",
                "default": False
            },
            "include_related": {
                "type": "boolean",
                "default": False
            },
            "include_suggestions": {
                "type": "boolean",
                "default": False
            }
        },
        "required": ["keyword"]
    },
    "analyze_competitors": {
        "description": "Analyze competitors for a given keyword or domain",
        "parameters": {
            "domain": {
                "type": "string"
            },
            "keyword": {
                "type": "string"
            },
            "include_features": {
                "type": "boolean"
            },
            "num_results": {
                "type": "number",
                "minimum": 1,
                "maximum": 100
            }
        },
        "required": ["domain"]
    },
    "autocomplete": {
        "description": "Get search autocomplete suggestions for multiple queries at once",
        "parameters": {
            "queries": {
                "description": "List of search queries to get autocomplete suggestions for",
                "type": "array",
                "items": {
                    "type": "string"
                }
            },
            "location": {
                "description": "Location for search results (e.g., 'Brazil', 'United States')",
                "type": "string"
            },
            "gl": {
                "description": "Country code (e.g., 'br', 'us')",
                "type": "string"
            },
            "hl": {
                "description": "Language code (e.g., 'pt-br', 'en')",
                "type": "string"
            }
        },
        "required": ["queries"]
    },
    "serper_maps_search": {
        "description": "Tool to search for maps and locations using the Serper API.",
        "parameters": {
            "q": {
                "description": "Search query string for maps (e.g., 'restaurants in New York', 'parks in London')",
                "type": "string"
            },
            "gl": {
                "description": "Optional region code for search results in ISO 3166-1 alpha-2 format (e.g., 'us', 'gb', 'de')",
                "type": "string"
            },
            "hl": {
                "description": "Optional language code for search results in ISO 639-1 format (e.g., 'en', 'es', 'fr')",
                "type": "string"
            },
            "location": {
                "description": "Optional location for search results (e.g., 'New York, NY', 'London, UK')",
                "type": "string"
            },
            "num": {
                "description": "Number of results to return (default: 10)",
                "type": "number"
            }
        }
    },
    "serper_reviews_search": {
        "description": "Tool to search for reviews using the Serper API.",
        "parameters": {
            "q": {
                "description": "Search query string for reviews (e.g., 'iPhone 13 reviews', 'hotel reviews in Paris')",
                "type": "string"
            },
            "gl": {
                "description": "Optional region code for search results in ISO 3166-1 alpha-2 format (e.g., 'us', 'gb', 'de')",
                "type": "string"
            },
            "hl": {
                "description": "Optional language code for search results in ISO 639-1 format (e.g., 'en', 'es', 'fr')",
                "type": "string"
            },
            "location": {
                "description": "Optional location for search results (e.g., 'New York, NY', 'London, UK')",
                "type": "string"
            },
            "num": {
                "description": "Number of results to return (default: 10)",
                "type": "number"
            }
        }
    },
    "serper_shopping_search": {
        "description": "Tool to search for products and shopping information using the Serper API.",
        "parameters": {
            "q": {
                "description": "Search query string for products (e.g., 'best smartphones 2024', 'running shoes')",
                "type": "string"
            },
            "gl": {
                "description": "Optional region code for search results in ISO 3166-1 alpha-2 format (e.g., 'us', 'gb', 'de')",
                "type": "string"
            },
            "hl": {
                "description": "Optional language code for search results in ISO 639-1 format (e.g., 'en', 'es', 'fr')",
                "type": "string"
            },
            "location": {
                "description": "Optional location for search results (e.g., 'New York, NY', 'London, UK')",
                "type": "string"
            },
            "num": {
                "description": "Number of results to return (default: 10)",
                "type": "number"
            }
        }
    },
    "serper_lens_search": {
        "description": "Tool to search for information about an image using Google Lens via the Serper API.",
        "parameters": {
            "image_url": {
                "description": "URL of the image to search with (must be a publicly accessible image URL)",
                "type": "string"
            },
            "gl": {
                "description": "Optional region code for search results in ISO 3166-1 alpha-2 format (e.g., 'us', 'gb', 'de')",
                "type": "string"
            },
            "hl": {
                "description": "Optional language code for search results in ISO 639-1 format (e.g., 'en', 'es', 'fr')",
                "type": "string"
            },
            "location": {
                "description": "Optional location for search results (e.g., 'New York, NY', 'London, UK')",
                "type": "string"
            }
        }
    },
    "serper_scholar_search": {
        "description": "Tool to search for academic papers and scholarly information using the Serper API.",
        "parameters": {
            "q": {
                "description": "Search query string for academic papers (e.g., 'machine learning advances', 'climate change research')",
                "type": "string"
            },
            "gl": {
                "description": "Optional region code for search results in ISO 3166-1 alpha-2 format (e.g., 'us', 'gb', 'de')",
                "type": "string"
            },
            "hl": {
                "description": "Optional language code for search results in ISO 639-1 format (e.g., 'en', 'es', 'fr')",
                "type": "string"
            },
            "location": {
                "description": "Optional location for search results (e.g., 'New York, NY', 'London, UK')",
                "type": "string"
            },
            "num": {
                "description": "Number of results to return (default: 10)",
                "type": "number"
            },
            "year_min": {
                "description": "Minimum publication year to filter results (e.g., 2020)",
                "type": "number"
            },
            "year_max": {
                "description": "Maximum publication year to filter results (e.g., 2023)",
                "type": "number"
            }
        }
    },
    "serper_patents_search": {
        "description": "Tool to search for patents information using the Serper API.",
        "parameters": {
            "q": {
                "description": "Search query string for patents (e.g., 'artificial intelligence patents', 'electric vehicle charging')",
                "type": "string"
            },
            "gl": {
                "description": "Optional region code for search results in ISO 3166-1 alpha-2 format (e.g., 'us', 'gb', 'de')",
                "type": "string"
            },
            "hl": {
                "description": "Optional language code for search results in ISO 639-1 format (e.g., 'en', 'es', 'fr')",
                "type": "string"
            },
            "location": {
                "description": "Optional location for search results (e.g., 'New York, NY', 'London, UK')",
                "type": "string"
            },
            "num": {
                "description": "Number of results to return (default: 10)",
                "type": "number"
            },
            "patent_office": {
                "description": "Patent office to search in (e.g., 'USPTO', 'EPO', 'WIPO')",
                "type": "string"
            }
        }
    },
    "serper_webpage_search": {
        "description": "Tool to get detailed information about a specific webpage using the Serper API.",
        "parameters": {
            "url": {
                "description": "URL of the webpage to analyze (must be a publicly accessible URL)",
                "type": "string"
            },
            "extract_content": {
                "description": "Whether to extract the main content from the webpage (default: true)",
                "type": "boolean"
            },
            "extract_metadata": {
                "description": "Whether to extract metadata from the webpage (default: true)",
                "type": "boolean"
            }
        }
    },
    "serper_news_search": {
        "description": "Tool to search for news articles using the Serper API.",
        "parameters": {
            "q": {
                "description": "Search query string for news articles (e.g., 'latest tech news', 'covid-19 updates')",
                "type": "string"
            },
            "gl": {
                "description": "Optional region code for search results in ISO 3166-1 alpha-2 format (e.g., 'us', 'gb', 'de')",
                "type": "string"
            },
            "hl": {
                "description": "Optional language code for search results in ISO 639-1 format (e.g., 'en', 'es', 'fr')",
                "type": "string"
            },
            "location": {
                "description": "Optional location for search results (e.g., 'New York, NY', 'London, UK')",
                "type": "string"
            },
            "num": {
                "description": "Number of results to return (default: 10)",
                "type": "number"
            },
            "timerange": {
                "description": "Time range for news articles (e.g., 'd' for day, 'w' for week, 'm' for month)",
                "type": "string"
            }
        }
    },
    "serper_places_search": {
        "description": "Tool to search for places and locations using the Serper API.",
        "parameters": {
            "q": {
                "description": "Search query string for places (e.g., 'restaurants near me', 'parks in San Francisco')",
                "type": "string"
            },
            "gl": {
                "description": "Optional region code for search results in ISO 3166-1 alpha-2 format (e.g., 'us', 'gb', 'de')",
                "type": "string"
            },
            "hl": {
                "description": "Optional language code for search results in ISO 639-1 format (e.g., 'en', 'es', 'fr')",
                "type": "string"
            },
            "location": {
                "description": "Optional location for search results (e.g., 'New York, NY', 'London, UK')",
                "type": "string"
            },
            "num": {
                "description": "Number of results to return (default: 10)",
                "type": "number"
            }
        }
    }
}

# Protocolo MCP por stdio
def handle_message(message: Dict[Any, Any]) -> Dict[Any, Any]:
    """Handle incoming MCP messages."""
    try:
        method = message.get("method")
        if not method:
            return {"error": {"message": "No method specified"}}

        message_id = message.get("id")
        
        # ListTools handler
        if method == "mcp.ListTools":
            return {
                "id": message_id,
                "result": {
                    "tools": tools_definitions
                }
            }
            
        # CallTool handler
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
                
            elif tool_name == "serper_maps_search":
                result = search_tools.maps_search(arguments)
                return {
                    "id": message_id,
                    "result": {
                        "content": [
                            {"type": "text", "text": json.dumps(result, ensure_ascii=False)}
                        ]
                    }
                }
                
            elif tool_name == "serper_reviews_search":
                result = search_tools.reviews_search(arguments)
                return {
                    "id": message_id,
                    "result": {
                        "content": [
                            {"type": "text", "text": json.dumps(result, ensure_ascii=False)}
                        ]
                    }
                }
                
            elif tool_name == "serper_shopping_search":
                result = search_tools.shopping_search(arguments)
                return {
                    "id": message_id,
                    "result": {
                        "content": [
                            {"type": "text", "text": json.dumps(result, ensure_ascii=False)}
                        ]
                    }
                }
                
            elif tool_name == "serper_lens_search":
                result = search_tools.lens_search(arguments)
                return {
                    "id": message_id,
                    "result": {
                        "content": [
                            {"type": "text", "text": json.dumps(result, ensure_ascii=False)}
                        ]
                    }
                }
                
            elif tool_name == "serper_scholar_search":
                result = search_tools.scholar_search(arguments)
                return {
                    "id": message_id,
                    "result": {
                        "content": [
                            {"type": "text", "text": json.dumps(result, ensure_ascii=False)}
                        ]
                    }
                }
                
            elif tool_name == "serper_patents_search":
                result = search_tools.patents_search(arguments)
                return {
                    "id": message_id,
                    "result": {
                        "content": [
                            {"type": "text", "text": json.dumps(result, ensure_ascii=False)}
                        ]
                    }
                }
                
            elif tool_name == "serper_webpage_search":
                result = search_tools.webpage_search(arguments)
                return {
                    "id": message_id,
                    "result": {
                        "content": [
                            {"type": "text", "text": json.dumps(result, ensure_ascii=False)}
                        ]
                    }
                }
                
            elif tool_name == "serper_news_search":
                result = search_tools.news_search(arguments)
                return {
                    "id": message_id,
                    "result": {
                        "content": [
                            {"type": "text", "text": json.dumps(result, ensure_ascii=False)}
                        ]
                    }
                }
                
            elif tool_name == "serper_places_search":
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
                        "message": f"Unknown tool: {tool_name}"
                    }
                }
        else:
            # Lidando com outros métodos (ListPrompts, GetPrompt, etc.)
            return {
                "id": message_id,
                "error": {
                    "message": f"Method not implemented: {method}"
                }
            }
            
    except Exception as e:
        logger.error(f"Error handling message: {e}", exc_info=True)
        return {
            "id": message.get("id"),
            "error": {
                "message": f"Internal server error: {str(e)}"
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