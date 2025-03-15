"""
Implementação do servidor MCP em Python com suporte a SSE.
"""

import asyncio
import json
import logging
import os
import uuid
import time
from typing import Any, Dict, List, Optional

import uvicorn
from fastapi import Depends, FastAPI, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sse_starlette.sse import EventSourceResponse

from . import config
from .serper_client import SerperClient

logger = logging.getLogger(__name__)


class SSEServerTransport:
    """Implementação do transporte SSE para o servidor MCP."""

    def __init__(self):
        """Inicializa o transporte SSE."""
        self.response = None
        self.tools = []
        self.session_id = str(uuid.uuid4())
        
    async def start(self, response: EventSourceResponse):
        """
        Inicia o transporte SSE.
        
        Args:
            response: Resposta EventSource para enviar eventos SSE
        """
        self.response = response
        await self._send_open_message(response)
    
    async def _send_open_message(self, response: EventSourceResponse):
        """
        Envia a mensagem de abertura com as ferramentas disponíveis.
        
        Args:
            response: Resposta EventSource para enviar eventos SSE
        """
        open_message = {
            "tools": self.tools
        }
        await response.send(
            json.dumps(open_message),
            event="open"
        )
    
    async def send_message(self, message: Dict[str, Any]):
        """
        Envia uma mensagem para o cliente.
        
        Args:
            message: Mensagem a ser enviada
        """
        if not self.response:
            logger.error("Tentativa de enviar mensagem sem conexão inicializada")
            return
        
        await self.response.send(
            json.dumps(message),
            event="message"
        )
    
    async def send_error(self, error: str):
        """
        Envia uma mensagem de erro para o cliente.
        
        Args:
            error: Mensagem de erro
        """
        error_message = {
            "type": "error",
            "error": error
        }
        await self.send_message(error_message)
    
    async def close(self):
        """Fecha o transporte SSE."""
        if self.response:
            # A resposta SSE já tem mecanismos para se fechar
            self.response = None
    
    async def handle_message(self, message: Dict[str, Any]):
        """
        Manipula uma mensagem recebida do cliente.
        
        Args:
            message: Mensagem recebida
        """
        logger.info(f"Mensagem recebida: {message}")
        
        if message.get("type") != "toolInvocation":
            await self.send_error("Tipo de mensagem inválido")
            return
        
        # Neste ponto, processamos a mensagem e respondemos
        # conforme necessário
        await self.send_message({
            "type": "ack",
            "message": "Mensagem recebida com sucesso"
        })
    
    def register_tool(self, tool: Dict[str, Any]):
        """
        Registra uma ferramenta disponível.
        
        Args:
            tool: Definição da ferramenta
        """
        self.tools.append(tool)
    
    def stream_generator(self):
        """
        Gerador para streaming SSE.
        
        Yields:
            Mensagens formatadas para SSE
        """
        try:
            # Envia um evento connected com o session_id
            yield {
                "event": "connected",
                "data": json.dumps({"sessionId": self.session_id})
            }
            
            # Mantém a conexão aberta com pings periódicos
            count = 0
            while True:
                if count % 30 == 0:  # Envia ping a cada 30 iterações (aproximadamente 30 segundos)
                    yield {
                        "event": "ping",
                        "data": ""
                    }
                count += 1
                # Usa um pequeno delay sem bloquear o gerador
                time.sleep(1)
        except asyncio.CancelledError:
            logger.info("Cliente desconectado")
            # Limpeza necessária quando o cliente desconecta
            self.response = None
        except Exception as e:
            logger.error(f"Erro no streaming SSE: {e}")
            self.response = None


class MCPServerApp:
    """Aplicação de servidor MCP."""

    def __init__(self):
        """Inicializa a aplicação de servidor MCP."""
        # Inicializa a aplicação FastAPI
        self.app = FastAPI(
            title="MCP Serper Server",
            description="Servidor MCP para busca web via API Serper",
            version=config.APP_VERSION,
        )
        
        # Configura CORS
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        # Inicializa cliente Serper
        self.serper_client = SerperClient()
        
        # Dicionário para armazenar transportes ativos
        # Chave: ID da sessão, Valor: Instância do transporte
        self.transports = {}
        
        # Registra as rotas e ferramentas
        self.register_routes()
        self.register_tools()
    
    def register_routes(self):
        """Registra as rotas da API."""
        
        # Middleware para autenticação
        @self.app.middleware("http")
        async def auth_middleware(request: Request, call_next):
            # Verifica se a autenticação é necessária
            if config.MCP_TOKEN:
                auth_header = request.headers.get("Authorization")
                
                # Verifica se é uma rota que requer autenticação
                # Neste caso, todas exceto a rota de saúde
                if request.url.path != "/_health":
                    # Se o token está configurado, verifica autenticação
                    if not auth_header:
                        return JSONResponse(
                            status_code=401,
                            content={"error": "Sem token de autenticação"}
                        )
                    
                    # Formato esperado: "Bearer TOKEN"
                    parts = auth_header.split()
                    if len(parts) != 2 or parts[0].lower() != "bearer":
                        return JSONResponse(
                            status_code=401,
                            content={"error": "Formato de autenticação inválido"}
                        )
                    
                    if parts[1] != config.MCP_TOKEN:
                        return JSONResponse(
                            status_code=403,
                            content={"error": "Token inválido"}
                        )
            
            # Continua para o próximo middleware ou rota
            return await call_next(request)
        
        # Rota principal
        @self.app.get("/")
        async def home():
            return {
                "status": "ok",
                "name": config.APP_NAME,
                "version": config.APP_VERSION,
                "description": "Servidor MCP para busca web via API Serper",
            }
        
        # Endpoint SSE
        @self.app.get("/sse")
        async def sse_endpoint(request: Request):
            # Obtém o ID da sessão do cabeçalho
            session_id = request.headers.get("X-MCP-Session-ID")
            
            if not session_id:
                session_id = str(uuid.uuid4())
                logger.info(f"Criando nova sessão: {session_id}")
            else:
                logger.info(f"Usando sessão existente: {session_id}")
            
            # Cria um novo transporte SSE
            transport = SSEServerTransport()
            transport.session_id = session_id
            
            # Registra as ferramentas disponíveis
            self.register_tools_for_transport(transport)
            
            # Armazena o transporte
            self.transports[session_id] = transport
            
            # Configura a resposta SSE
            async def sse_stream():
                response = EventSourceResponse(transport.stream_generator())
                await transport.start(response)
                try:
                    # Mantém a conexão aberta até o cliente desconectar
                    while True:
                        await asyncio.sleep(1)
                except asyncio.CancelledError:
                    logger.info(f"Cliente desconectado: {session_id}")
                    await transport.close()
                    # Remove o transporte quando o cliente desconecta
                    if session_id in self.transports:
                        del self.transports[session_id]
                    raise
            
            return EventSourceResponse(sse_stream())
        
        # Endpoint de mensagens
        @self.app.post("/messages")
        async def messages_endpoint(
            request: Request,
            message: Dict[str, Any],
        ):
            # Obtém o ID da sessão do cabeçalho
            session_id = request.headers.get("X-MCP-Session-ID")
            
            if not session_id or session_id not in self.transports:
                raise HTTPException(
                    status_code=400,
                    detail="Sessão inválida ou expirada"
                )
            
            # Obtém o transporte associado à sessão
            transport = self.transports[session_id]
            
            # Processa a mensagem
            message_type = message.get("type")
            
            if message_type != "toolInvocation":
                raise HTTPException(
                    status_code=400,
                    detail="Tipo de mensagem inválido"
                )
            
            # Extrai informações da mensagem
            query = message.get("query", "")
            parameters = message.get("parameters", {})
            
            # Log da mensagem recebida
            logger.info(f"Mensagem recebida: query='{query}', parameters={parameters}")
            
            # Executa a query (neste caso, sempre faz uma busca)
            try:
                # Processa a consulta do usuário
                if "google" in query.lower() or "busca" in query.lower():
                    # Prepara os parâmetros de busca
                    search_params = {
                        "q": query,
                        "gl": parameters.get("gl", "us"),
                        "hl": parameters.get("hl", "pt"),
                    }
                    
                    # Adiciona parâmetros adicionais
                    if "num" in parameters:
                        search_params["num"] = parameters["num"]
                    
                    # Executa a busca
                    result = await self.serper_client.search(**search_params)
                    
                    # Envia o resultado
                    await transport.send_message({
                        "type": "toolResult",
                        "name": "google_search",
                        "result": result,
                    })
                elif "scrape" in query.lower() or "extrair" in query.lower():
                    # Verifica se a URL foi informada
                    if "url" not in parameters:
                        await transport.send_error("URL não informada")
                        return {"status": "error", "message": "URL não informada"}
                    
                    # Executa a extração de conteúdo
                    include_markdown = parameters.get("includeMarkdown", False)
                    result = await self.serper_client.scrape(
                        url=parameters["url"],
                        include_markdown=include_markdown,
                    )
                    
                    # Envia o resultado
                    await transport.send_message({
                        "type": "toolResult",
                        "name": "scrape",
                        "result": result,
                    })
                else:
                    # Assume busca por padrão
                    result = await self.serper_client.search(
                        q=query, 
                        gl=parameters.get("gl", "us"),
                        hl=parameters.get("hl", "pt"),
                    )
                    
                    # Envia o resultado
                    await transport.send_message({
                        "type": "toolResult",
                        "name": "google_search",
                        "result": result,
                    })
                
                return {"status": "ok"}
            except Exception as e:
                logger.error(f"Erro ao processar mensagem: {e}")
                await transport.send_error(f"Erro ao processar mensagem: {str(e)}")
                return {"status": "error", "message": str(e)}
        
        # Endpoint de saúde
        @self.app.get("/_health")
        async def health():
            # Verifica a saúde do cliente Serper
            serper_health = await self.serper_client.health()
            
            # Verifica a saúde geral do serviço
            is_healthy = serper_health.get("status") == "ok"
            
            return {
                "status": "ok" if is_healthy else "error",
                "version": config.APP_VERSION,
                "serper": serper_health,
            }
    
    def register_tools(self):
        """Registra as ferramentas disponíveis."""
        # As ferramentas serão registradas para cada transporte
        pass
    
    def register_tools_for_transport(self, transport: SSEServerTransport):
        """
        Registra as ferramentas para um transporte específico.
        
        Args:
            transport: Transporte SSE para registrar as ferramentas
        """
        # Ferramenta de busca Google
        transport.register_tool({
            "name": "google_search",
            "description": "Ferramenta para realizar buscas na web via API Serper e recuperar resultados completos. Capaz de recuperar resultados orgânicos de busca, pessoas também perguntam, buscas relacionadas e gráfico de conhecimento.",
            "parameters": {
                "type": "object",
                "properties": {
                    "q": {
                        "type": "string",
                        "description": "String de consulta de busca (ex: 'inteligência artificial', 'soluções para mudanças climáticas')"
                    },
                    "gl": {
                        "type": "string",
                        "description": "Código de região opcional para resultados da busca no formato ISO 3166-1 alpha-2 (ex: 'us', 'br', 'pt')"
                    },
                    "hl": {
                        "type": "string",
                        "description": "Código de idioma opcional para resultados da busca no formato ISO 639-1 (ex: 'en', 'pt', 'es')"
                    },
                    "num": {
                        "type": "number",
                        "description": "Número de resultados a retornar (padrão: 10)"
                    },
                    "page": {
                        "type": "number",
                        "description": "Número da página de resultados a retornar (padrão: 1)"
                    },
                    "tbs": {
                        "type": "string",
                        "description": "Filtro de busca baseado em tempo ('qdr:h' para última hora, 'qdr:d' para último dia, 'qdr:w' para última semana, 'qdr:m' para último mês, 'qdr:y' para último ano)"
                    },
                    "site": {
                        "type": "string",
                        "description": "Limitar resultados a domínio específico (ex: 'github.com', 'wikipedia.org')"
                    },
                    "filetype": {
                        "type": "string",
                        "description": "Limitar a tipos específicos de arquivo (ex: 'pdf', 'doc', 'xls')"
                    }
                },
                "required": ["q", "gl", "hl"]
            }
        })
        
        # Ferramenta de extração de conteúdo
        transport.register_tool({
            "name": "scrape",
            "description": "Ferramenta para extrair o conteúdo de uma página web e recuperar o texto e, opcionalmente, o conteúdo em markdown. Também recupera os metadados JSON-LD e os metadados do cabeçalho.",
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "A URL da página web para extrair."
                    },
                    "includeMarkdown": {
                        "type": "boolean",
                        "description": "Se deve incluir conteúdo em markdown.",
                        "default": False
                    }
                },
                "required": ["url"]
            }
        })
        
        # Ferramenta de verificação de saúde
        transport.register_tool({
            "name": "_health",
            "description": "Endpoint de verificação de saúde",
            "parameters": {
                "type": "object",
                "properties": {
                    "random_string": {
                        "type": "string",
                        "description": "Parâmetro fictício para ferramentas sem parâmetros"
                    }
                },
                "required": ["random_string"]
            }
        })
    
    async def shutdown(self):
        """Encerra os recursos do servidor."""
        # Fecha os transportes ativos
        for session_id, transport in list(self.transports.items()):
            await transport.close()
        
        # Limpa o dicionário de transportes
        self.transports.clear()
        
        # Fecha o cliente Serper
        self.serper_client.close()
    
    def run(self, host: Optional[str] = None, port: Optional[int] = None):
        """
        Inicia o servidor.
        
        Args:
            host: Host para executar o servidor (padrão: config.HOST)
            port: Porta para executar o servidor (padrão: config.PORT)
        """
        host = host or config.HOST
        port = port or config.PORT
        
        logger.info(f"Iniciando servidor MCP em {host}:{port}")
        
        uvicorn.run(
            self.app,
            host=host,
            port=port,
            log_level="info",
        ) 