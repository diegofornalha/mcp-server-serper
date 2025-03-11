"""
Cliente para interagir com a API Serper.
"""

import logging
import http.client
import json
from typing import Dict, Any, List, Optional, Union, TypedDict

logger = logging.getLogger("serper-client")

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
        
    def _make_request(self, method: str, endpoint: str, payload: Dict[str, Any]) -> Dict[str, Any]:
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
            
            json_payload = json.dumps(payload)
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
            response = self._make_request("POST", "/autocomplete", query_list)
            return {"autocompleteData": response}
        except Exception as e:
            logger.error(f"Error in autocomplete: {e}")
            raise Exception(f"Failed to get autocomplete suggestions: {e}")