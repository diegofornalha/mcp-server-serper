#!/usr/bin/env node

/**
 * Implementação do servidor MCP que fornece recursos de busca na web via API Serper.
 */

import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
  ListPromptsRequestSchema,
  GetPromptRequestSchema,
} from "@modelcontextprotocol/sdk/types.js";
import { SerperClient } from "./services/serper-client.js";
import { SerperSearchTools } from "./tools/search-tool.js";
import { SerperPrompts } from "./prompts/index.js";

// Inicializa o cliente Serper com a chave de API do ambiente
const serperApiKey = process.env.SERPER_API_KEY;
if (!serperApiKey) {
  throw new Error("Variável de ambiente SERPER_API_KEY é obrigatória");
}

// Cria cliente Serper, ferramenta de busca e prompts
const serperClient = new SerperClient(serperApiKey);
const searchTools = new SerperSearchTools(serperClient);
const prompts = new SerperPrompts(searchTools);

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
 * Inicia o servidor usando transporte stdio.
 */
async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
}

main().catch((error) => {
  console.error("Erro ao iniciar o servidor:", error);
  process.exit(1);
});
