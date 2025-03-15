"""
Cliente para a API Serper que permite realizar buscas na web e extrair conteúdo de páginas.
"""

import logging
from typing import Any, Dict, Optional

import httpx

from . import config

logger = logging.getLogger(__name__)


class SerperClient:
    """Cliente para a API Serper."""

    def __init__(
        self,
        api_key: Optional[str] = None,
        timeout: int = 30,
    ):
        """
        Inicializa o cliente Serper.
        
        Args:
            api_key: Chave da API Serper (se não fornecida, usa a variável de
                ambiente SERPER_API_KEY)
            timeout: Tempo de espera máximo em segundos para as requisições
        """
        self.api_key = api_key or config.SERPER_API_KEY
        if not self.api_key:
            raise ValueError(
                "API key não fornecida e não encontrada nas variáveis "
                "de ambiente."
            )
        
        self.base_url = config.SERPER_API_URL
        self.timeout = timeout
        self.client = httpx.AsyncClient(timeout=timeout)

    async def search(
        self,
        q: str,
        gl: str,
        hl: str,
        num: Optional[int] = None,
        **kwargs,
    ) -> Dict[str, Any]:
        """
        Realiza uma busca no Google via API Serper.
        
        Args:
            q: Termo de busca
            gl: Código de geolocalização (ex: us, br)
            hl: Código de idioma (ex: en, pt)
            num: Número de resultados (opcional)
            **kwargs: Parâmetros adicionais da API Serper
            
        Returns:
            Dict[str, Any]: Resultados da busca
        """
        url = f"{self.base_url}/search"
        
        # Cria o payload com os parâmetros obrigatórios
        payload = {
            "q": q,
            "gl": gl,
            "hl": hl,
        }
        
        # Adiciona parâmetros opcionais
        if num is not None:
            payload["num"] = num
        
        # Adiciona outros parâmetros adicionais
        payload.update(kwargs)
        
        # Define os cabeçalhos
        headers = {
            "X-API-KEY": self.api_key,
            "Content-Type": "application/json",
        }
        
        try:
            response = await self.client.post(
                url,
                json=payload,
                headers=headers,
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(
                f"Erro na requisição de busca: {e.response.status_code} "
                f"{e.response.text}"
            )
            raise
        except Exception as e:
            logger.error(f"Erro ao fazer busca: {e}")
            raise

    async def scrape(
        self,
        url: str,
        include_markdown: bool = False,
    ) -> Dict[str, Any]:
        """
        Extrai conteúdo de uma página web.
        
        Args:
            url: URL da página a ser extraída
            include_markdown: Incluir conteúdo formatado em Markdown
            
        Returns:
            Dict[str, Any]: Conteúdo extraído
        """
        scrape_url = f"{self.base_url}/scrape"
        
        payload = {
            "url": url,
            "includeMarkdown": include_markdown,
        }
        
        headers = {
            "X-API-KEY": self.api_key,
            "Content-Type": "application/json",
        }
        
        try:
            response = await self.client.post(
                scrape_url,
                json=payload,
                headers=headers,
            )
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(
                f"Erro na extração de conteúdo: {e.response.status_code} "
                f"{e.response.text}"
            )
            raise
        except Exception as e:
            logger.error(f"Erro ao extrair conteúdo: {e}")
            raise

    async def health(self) -> Dict[str, Any]:
        """
        Verifica a saúde do serviço Serper.
        
        Returns:
            Dict[str, Any]: Status do serviço
        """
        url = f"{self.base_url}/_health"
        
        headers = {
            "X-API-KEY": self.api_key,
        }
        
        try:
            response = await self.client.get(url, headers=headers)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            logger.error(
                f"Erro na verificação de saúde: {e.response.status_code} "
                f"{e.response.text}"
            )
            return {"status": "error", "message": str(e)}
        except Exception as e:
            logger.error(f"Erro ao verificar saúde: {e}")
            return {"status": "error", "message": str(e)}

    def close(self):
        """Fecha o cliente HTTP."""
        if self.client:
            self.client.aclose() 