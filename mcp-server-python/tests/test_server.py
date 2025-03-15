"""
Testes para o servidor MCP.
"""

import json
import unittest
from unittest.mock import AsyncMock, MagicMock, patch

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient

from mcp_server_serper.server import MCPServerApp, SSEServerTransport


class TestSSEServerTransport(unittest.TestCase):
    """Testes para a classe SSEServerTransport."""

    def setUp(self):
        """Configuração dos testes."""
        self.app = FastAPI()
        self.transport = SSEServerTransport()
        
    @pytest.mark.asyncio
    async def test_start(self):
        """Testa o método de inicialização."""
        with patch.object(self.transport, "_send_open_message") as mock_open:
            mock_response = MagicMock()
            await self.transport.start(mock_response)
            
            # Verifica se o método de envio da mensagem open foi chamado
            mock_open.assert_called_once_with(mock_response)
            
            # Verifica se o atributo response foi definido
            self.assertEqual(self.transport.response, mock_response)
    
    @pytest.mark.asyncio
    async def test_send_message(self):
        """Testa o método de envio de mensagens."""
        mock_response = MagicMock()
        mock_response.send = AsyncMock()
        self.transport.response = mock_response
        
        message = {
            "type": "toolResult",
            "name": "test_tool",
            "result": {"data": "test_data"},
        }
        
        await self.transport.send_message(message)
        
        # Verifica se o método send foi chamado com os dados corretos
        mock_response.send.assert_called_once()
        args = mock_response.send.call_args[0][0]
        self.assertIn("data:", args)
        
        # Verifica se os dados estão no formato JSON correto
        data = args.replace("data: ", "")
        message_data = json.loads(data)
        self.assertEqual(message_data["type"], "toolResult")
        self.assertEqual(message_data["name"], "test_tool")
        self.assertEqual(message_data["result"]["data"], "test_data")


class TestMCPServerApp(unittest.TestCase):
    """Testes para a classe MCPServerApp."""

    def setUp(self):
        """Configuração dos testes."""
        # Configura patches para evitar inicialização real
        self.serper_client_patch = patch(
            "mcp_server_serper.server.SerperClient"
        )
        self.mock_serper_client = self.serper_client_patch.start()
        
        # Cria uma instância do app
        self.app = MCPServerApp()
        
        # Cria um cliente de teste para o app FastAPI
        self.client = TestClient(self.app.app)

    def tearDown(self):
        """Limpeza após os testes."""
        self.serper_client_patch.stop()

    def test_home_endpoint(self):
        """Testa o endpoint home."""
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["status"], "ok")
        self.assertIn("version", data)

    @patch("mcp_server_serper.server.SSEServerTransport")
    def test_sse_endpoint(self, mock_transport_class):
        """Testa o endpoint SSE."""
        # Configure o mock para SSEServerTransport
        mock_transport = MagicMock()
        mock_transport_class.return_value = mock_transport
        
        # O teste não pode verificar o streaming de SSE diretamente
        # devido à natureza do SSE, mas pode verificar a rota
        
        # Verifica se a rota existe
        routes = [route.path for route in self.app.app.routes]
        self.assertIn("/sse", routes)

    @patch("mcp_server_serper.server.SSEServerTransport")
    def test_messages_endpoint(self, mock_transport_class):
        """Testa o endpoint de mensagens."""
        # Configure o mock para o transporte
        mock_transport = MagicMock()
        self.app.transports = {"test_session": mock_transport}
        
        # Simula uma mensagem de invocação de ferramenta
        message = {
            "type": "toolInvocation",
            "query": "Busca por Python",
            "parameters": {}
        }
        
        # Configura o mock do cliente Serper
        mock_serper = MagicMock()
        self.app.serper_client = mock_serper
        mock_serper.search.return_value = {"results": ["result1"]}
        
        # Faz a requisição
        response = self.client.post(
            "/messages",
            json=message,
            headers={"X-MCP-Session-ID": "test_session"}
        )
        
        # Verifica a resposta
        self.assertEqual(response.status_code, 200)


if __name__ == "__main__":
    unittest.main() 