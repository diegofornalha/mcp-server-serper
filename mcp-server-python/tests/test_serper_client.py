"""
Testes para o cliente Serper.
"""

import unittest
from unittest.mock import MagicMock, patch

import pytest

from mcp_server_serper.serper_client import SerperClient


class TestSerperClient(unittest.TestCase):
    """Testes para a classe SerperClient."""

    def setUp(self):
        """Configuração dos testes."""
        self.api_key = "chave_teste"
        self.client = SerperClient(api_key=self.api_key)

    def tearDown(self):
        """Limpeza após os testes."""
        self.client.close()

    @pytest.mark.asyncio
    @patch("mcp_server_serper.serper_client.httpx.AsyncClient.post")
    async def test_search(self, mock_post):
        """Testa o método de busca."""
        # Configura o mock
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "searchParameters": {"q": "python"},
            "organic": [{"title": "Python", "link": "https://python.org"}],
        }
        mock_post.return_value = mock_response

        # Executa o método
        result = await self.client.search(
            q="python",
            gl="us",
            hl="pt",
        )

        # Verifica as chamadas
        mock_post.assert_called_once()
        args, kwargs = mock_post.call_args
        self.assertEqual(kwargs["json"]["q"], "python")
        self.assertEqual(kwargs["json"]["gl"], "us")
        self.assertEqual(kwargs["json"]["hl"], "pt")
        self.assertEqual(
            kwargs["headers"]["X-API-KEY"],
            self.api_key,
        )

        # Verifica o resultado
        self.assertEqual(result["searchParameters"]["q"], "python")
        self.assertEqual(len(result["organic"]), 1)
        self.assertEqual(result["organic"][0]["title"], "Python")

    @pytest.mark.asyncio
    @patch("mcp_server_serper.serper_client.httpx.AsyncClient.post")
    async def test_scrape(self, mock_post):
        """Testa o método de extração de conteúdo."""
        # Configura o mock
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "url": "https://python.org",
            "title": "Python",
            "text": "Python é uma linguagem de programação.",
        }
        mock_post.return_value = mock_response

        # Executa o método
        result = await self.client.scrape(
            url="https://python.org",
            include_markdown=True,
        )

        # Verifica as chamadas
        mock_post.assert_called_once()
        args, kwargs = mock_post.call_args
        self.assertEqual(kwargs["json"]["url"], "https://python.org")
        self.assertEqual(kwargs["json"]["includeMarkdown"], True)
        self.assertEqual(
            kwargs["headers"]["X-API-KEY"],
            self.api_key,
        )

        # Verifica o resultado
        self.assertEqual(result["url"], "https://python.org")
        self.assertEqual(result["title"], "Python")
        self.assertEqual(
            result["text"],
            "Python é uma linguagem de programação.",
        )

    @pytest.mark.asyncio
    @patch("mcp_server_serper.serper_client.httpx.AsyncClient.get")
    async def test_health(self, mock_get):
        """Testa o método de verificação de saúde."""
        # Configura o mock
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"status": "ok"}
        mock_get.return_value = mock_response

        # Executa o método
        result = await self.client.health()

        # Verifica as chamadas
        mock_get.assert_called_once()
        
        # Verifica o resultado
        self.assertEqual(result["status"], "ok")


if __name__ == "__main__":
    unittest.main() 