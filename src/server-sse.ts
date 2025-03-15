#!/usr/bin/env node

/**
 * Implementação do servidor MCP com suporte a SSE que fornece recursos de busca na web via API Serper.
 */

import express from 'express';
import http from 'http';
import cors from 'cors';
import { randomUUID } from 'crypto';
import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { SSEServerTransport } from "@modelcontextprotocol/sdk/server/sse.js";
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
  ListPromptsRequestSchema,
  GetPromptRequestSchema,
  JSONRPCMessageSchema,
} from "@modelcontextprotocol/sdk/types.js";
import { SerperClient } from "./services/serper-client.js";
import { SerperSearchTools } from "./tools/search-tool.js";
import { SerperPrompts } from "./prompts/index.js";
import * as dotenv from 'dotenv';

// Carrega variáveis de ambiente do arquivo .env
dotenv.config();

// Token de autenticação (você pode alterar isso para um token mais seguro)
const AUTH_TOKEN = process.env.AUTH_TOKEN || 'mcp-serper-token';

// Configuração para habilitar/desabilitar autenticação
const REQUIRE_AUTH = process.env.REQUIRE_AUTH !== 'false';

// Porta para o servidor HTTP
const PORT = parseInt(process.env.PORT || '3001');

// Inicializa o cliente Serper com a chave de API do ambiente
const serperApiKey = process.env.SERPER_API_KEY;
if (!serperApiKey) {
  throw new Error("Variável de ambiente SERPER_API_KEY é obrigatória");
}

// Cria cliente Serper, ferramenta de busca e prompts
const serperClient = new SerperClient(serperApiKey);
const searchTools = new SerperSearchTools(serperClient);
const prompts = new SerperPrompts(searchTools);

// Armazena os transportes SSE ativos por sessionId
const sessions = new Map<string, SSEServerTransport>();

// Cria servidor MCP
const server = new Server(
  {
    name: "Servidor MCP Serper",
    version: "0.2.0",
  },
  {
    capabilities: {
      tools: {},
      prompts: {}
    },
  }
);

/**
 * Manipulador que lista as ferramentas disponíveis.
 * Expõe várias ferramentas para realizar buscas e análises na web.
 */
server.setRequestHandler(ListToolsRequestSchema, async () => {
  // Define o esquema de entrada para a ferramenta de busca
  const searchInputSchema = {
    type: "object",
    properties: {
      q: {
        type: "string",
        description: "String de consulta de busca (ex: 'inteligência artificial', 'soluções para mudanças climáticas')"
      },
      gl: {
        type: "string",
        description: "Código de região opcional para resultados da busca no formato ISO 3166-1 alpha-2 (ex: 'us', 'br', 'pt')"
      },
      hl: {
        type: "string",
        description: "Código de idioma opcional para resultados da busca no formato ISO 639-1 (ex: 'en', 'pt', 'es')"
      },
      location: {
        type: "string",
        description: "Localização opcional para resultados da busca (ex: 'São Paulo, Brasil', 'Rio de Janeiro, Brasil')"
      },
      num: {
        type: "number",
        description: "Número de resultados a retornar (padrão: 10)"
      },
      tbs: {
        type: "string",
        description: "Filtro de busca baseado em tempo ('qdr:h' para última hora, 'qdr:d' para último dia, 'qdr:w' para última semana, 'qdr:m' para último mês, 'qdr:y' para último ano)"
      },
      page: {
        type: "number",
        description: "Número da página de resultados a retornar (padrão: 1)"
      },
      autocorrect: {
        type: "boolean",
        description: "Se deve corrigir automaticamente a ortografia na consulta"
      },
      site: {
        type: "string",
        description: "Limitar resultados a domínio específico (ex: 'github.com', 'wikipedia.org')"
      },
      filetype: {
        type: "string",
        description: "Limitar a tipos específicos de arquivo (ex: 'pdf', 'doc', 'xls')"
      },
      inurl: {
        type: "string",
        description: "Buscar páginas com palavra na URL (ex: 'download', 'tutorial')"
      },
      intitle: {
        type: "string",
        description: "Buscar páginas com palavra no título (ex: 'avaliação', 'como fazer')"
      },
      related: {
        type: "string",
        description: "Encontrar sites similares (ex: 'github.com', 'stackoverflow.com')"
      },
      cache: {
        type: "string",
        description: "Ver versão em cache do Google de uma URL específica (ex: 'example.com/page')"
      },
      before: {
        type: "string",
        description: "Data antes no formato AAAA-MM-DD (ex: '2024-01-01')"
      },
      after: {
        type: "string",
        description: "Data depois no formato AAAA-MM-DD (ex: '2023-01-01')"
      },
      exact: {
        type: "string",
        description: "Correspondência exata de frase (ex: 'aprendizado de máquina', 'computação quântica')"
      },
      exclude: {
        type: "string",
        description: "Termos a excluir dos resultados de busca como string separada por vírgula (ex: 'spam,anúncios', 'iniciante,básico')"
      },
      or: {
        type: "string",
        description: "Termos alternativos como string separada por vírgula (ex: 'tutorial,guia,curso', 'documentação,manual')"
      }
    },
    required: ["q", "gl", "hl"]
  };

  return {
    tools: [
      {
        name: "google_search",
        description: "Ferramenta para realizar buscas na web via API Serper e recuperar resultados completos. Capaz de recuperar resultados orgânicos de busca, pessoas também perguntam, buscas relacionadas e gráfico de conhecimento.",
        inputSchema: searchInputSchema
      },
      {
        name: "scrape",
        description: "Ferramenta para extrair o conteúdo de uma página web e recuperar o texto e, opcionalmente, o conteúdo em markdown. Também recupera os metadados JSON-LD e os metadados do cabeçalho.",
        inputSchema: {
          type: "object",
          properties: {
            url: {
              type: "string",
              description: "A URL da página web para extrair."
            },
            includeMarkdown: {
              type: "boolean",
              default: false,
              description: "Se deve incluir conteúdo em markdown."
            }
          },
          required: ["url"]
        }
      },
      {
        name: "_health",
        description: "Endpoint de verificação de saúde",
        inputSchema: {
          type: "object",
          properties: {
            random_string: {
              type: "string",
              description: "Parâmetro fictício para ferramentas sem parâmetros"
            }
          },
          required: ["random_string"]
        }
      }
    ]
  };
});

/**
 * Manipulador que executa as ferramentas de busca.
 * Processa solicitações para diversas ferramentas relacionadas à busca na web.
 */
server.setRequestHandler(CallToolRequestSchema, async (request) => {
  console.log(`Tool called: ${request.params.name}`);

  switch (request.params.name) {
    case "google_search": {
      const {
        q,
        gl,
        hl,
        location,
        num,
        tbs,
        page,
        autocorrect,
        // Parâmetros avançados de busca
        site,
        filetype,
        inurl,
        intitle,
        related,
        cache,
        before,
        after,
        exact,
        exclude,
        or
      } = request.params.arguments || {};

      if (!q || !gl || !hl) {
        throw new Error(
          "Consulta de busca, código de região e idioma são obrigatórios"
        );
      }

      try {
        const result = await searchTools.search({
          q: String(q),
          gl: String(gl),
          hl: String(hl),
          location: location as string | undefined,
          num: num as number | undefined,
          tbs: tbs as string | undefined,
          page: page as number | undefined,
          autocorrect: autocorrect as boolean | undefined,
          // Parâmetros avançados de busca
          site: site as string | undefined,
          filetype: filetype as string | undefined,
          inurl: inurl as string | undefined,
          intitle: intitle as string | undefined,
          related: related as string | undefined,
          cache: cache as string | undefined,
          before: before as string | undefined,
          after: after as string | undefined,
          exact: exact as string | undefined,
          exclude: exclude as string | undefined,
          or: or as string | undefined
        });

        return {
          content: [
            {
              type: "text",
              text: JSON.stringify(result, null, 2)
            },
          ],
        };
      } catch (error) {
        throw new Error(`Busca web falhou: ${error}`);
      }
    }

    case "scrape": {
      const { url, includeMarkdown = false } = request.params.arguments || {};

      if (!url) {
        throw new Error("URL é obrigatória para scraping");
      }

      try {
        const result = await searchTools.scrape({
          url: String(url),
          includeMarkdown: Boolean(includeMarkdown)
        });

        return {
          content: [
            {
              type: "text",
              text: JSON.stringify(result, null, 2)
            },
          ],
        };
      } catch (error) {
        throw new Error(`Scraping falhou: ${error}`);
      }
    }

    case "_health": {
      try {
        const result = await searchTools.health({});

        return {
          content: [
            {
              type: "text",
              text: JSON.stringify(result, null, 2)
            },
          ],
        };
      } catch (error) {
        throw new Error(`Verificação de saúde falhou: ${error}`);
      }
    }

    default:
      throw new Error(`Ferramenta desconhecida: ${request.params.name}`);
  }
});

/**
 * Manipulador para listar prompts.
 */
server.setRequestHandler(ListPromptsRequestSchema, async () => {
  return {
    prompts: prompts.getPromptDefinitions(),
  };
});

/**
 * Manipulador para obter um prompt específico.
 */
server.setRequestHandler(GetPromptRequestSchema, async (request) => {
  const promptName = request.params.name;
  return prompts.getPrompt(promptName);
});

/**
 * Middleware de autenticação para verificar o token
 */
function authenticate(req: express.Request, res: express.Response, next: express.NextFunction) {
  // Se a autenticação estiver desabilitada, prossegue sem verificar o token
  if (!REQUIRE_AUTH) {
    next();
    return;
  }
  
  const authHeader = req.headers.authorization;
  
  if (!authHeader || !authHeader.startsWith('Bearer ')) {
    res.status(401).send('Unauthorized: No token provided');
    return;
  }
  
  const token = authHeader.split(' ')[1];
  
  if (token !== AUTH_TOKEN) {
    res.status(403).send('Forbidden: Invalid token');
    return;
  }
  
  next();
}

// Configuração do servidor Express
const app = express();
app.use(cors());
// Usar o express.json padrão para processar o corpo da requisição
app.use(express.json({
  limit: '4mb'
}));

// Rota principal
app.get('/', (req, res) => {
  res.send(`
    <h1>Servidor MCP Serper</h1>
    <p>Servidor MCP com suporte a SSE para busca na web e raspagem de páginas.</p>
    <p>Endpoint SSE: <code>/sse</code></p>
    <p>Bearer Token para autenticação: <code>${AUTH_TOKEN}</code></p>
  `);
});

// Endpoint para estabelecer a conexão SSE
app.get('/sse', authenticate, async (req, res) => {
  try {
    console.log('Nova solicitação de conexão SSE recebida');
    
    const transport = new SSEServerTransport('/sse-message', res);
    
    // Registrar informações sobre a conexão
    console.log(`Criando nova conexão SSE. SessionID: ${transport.sessionId}`);
    console.log(`Headers do cliente: ${JSON.stringify(req.headers)}`);
    
    // Quando a conexão for fechada, remover o transporte da lista
    transport.onclose = () => {
      sessions.delete(transport.sessionId);
      console.log(`Conexão SSE fechada: ${transport.sessionId}`);
    };
    
    // Adicionar o transporte à lista
    sessions.set(transport.sessionId, transport);
    
    // Conectar o servidor MCP a este transporte
    await server.connect(transport);
    
    console.log(`Nova conexão SSE estabelecida: ${transport.sessionId}`);
  } catch (error) {
    console.error('Erro ao estabelecer conexão SSE:', error);
    res.status(500).send('Erro interno do servidor');
  }
});

// Endpoint para receber mensagens via POST
app.post('/sse-message', authenticate, async (req, res) => {
  // Buscar o sessionId - verificar tanto na query quanto no cabeçalho X-MCP-Session-ID
  const sessionId = req.query.sessionId as string || req.headers['x-mcp-session-id'] as string;
  
  console.log(`Recebida solicitação POST para /sse-message`);
  console.log(`SessionID: ${sessionId}`);
  console.log(`Headers: ${JSON.stringify(req.headers)}`);
  console.log(`Query params: ${JSON.stringify(req.query)}`);
  
  if (!sessionId) {
    console.error('Erro: SessionID não fornecido');
    res.status(400).send('Parâmetro sessionId é obrigatório (via query ou cabeçalho X-MCP-Session-ID)');
    return;
  }
  
  const transport = sessions.get(sessionId);
  
  if (!transport) {
    console.error(`Erro: Sessão não encontrada para SessionID ${sessionId}`);
    console.log(`Sessões disponíveis: ${Array.from(sessions.keys()).join(', ')}`);
    res.status(404).send('Sessão não encontrada');
    return;
  }
  
  try {
    // Uma abordagem mais simples que não depende de getRawBody/content-type
    if (!req.body || typeof req.body !== 'object') {
      console.error('Erro: Corpo da requisição inválido');
      res.status(400).send('Corpo da requisição deve ser um objeto JSON válido');
      return;
    }

    console.log(`Corpo da requisição: ${JSON.stringify(req.body)}`);

    // Validar que é uma mensagem JSON-RPC válida
    try {
      const message = JSONRPCMessageSchema.parse(req.body);
      console.log(`Mensagem JSON-RPC válida: ${JSON.stringify(message)}`);
      await transport.handleMessage(message);
      console.log('Mensagem processada com sucesso');
      res.status(202).send("Accepted");
    } catch (error) {
      console.error('Erro ao validar mensagem JSON-RPC:', error);
      res.status(400).send(`Mensagem JSON-RPC inválida: ${error instanceof Error ? error.message : String(error)}`);
    }
  } catch (error: unknown) {
    console.error('Erro ao processar mensagem:', error);
    if (!res.headersSent) {
      res.status(500).send(`Erro interno do servidor: ${error instanceof Error ? error.message : String(error)}`);
    }
  }
});

// Função para iniciar o servidor
async function main() {
  try {
    // Inicia o servidor HTTP
    const httpServer = http.createServer(app);
    
    httpServer.listen(PORT, () => {
      console.log(`Servidor MCP com SSE iniciado em http://localhost:${PORT}`);
      console.log(`Endpoint SSE disponível em http://localhost:${PORT}/sse`);
      console.log(`Token de autenticação: ${AUTH_TOKEN}`);
    });
  } catch (error) {
    console.error("Erro ao iniciar o servidor:", error);
    process.exit(1);
  }
}

// Inicia o servidor
main(); 