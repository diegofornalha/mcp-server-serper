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
    version: "0.1.0",
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
      // Operadores avançados de busca
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
    required: ["q", "gl", "hl"],
  };

  // Retorna lista de ferramentas com esquemas de entrada
  return {
    tools: [
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
      },
      {
        name: "analyze_serp",
        description: "Analisar uma SERP (Página de Resultados de Busca) para uma consulta específica",
        inputSchema: {
          $schema: "http://json-schema.org/draft-07/schema#",
          type: "object",
          additionalProperties: false,
          properties: {
            query: {
              type: "string"
            },
            gl: {
              type: "string",
              default: "us"
            },
            hl: {
              type: "string",
              default: "en"
            },
            google_domain: {
              type: "string",
              default: "google.com"
            },
            num: {
              type: "number",
              minimum: 1,
              maximum: 100,
              default: 10
            },
            device: {
              type: "string",
              enum: ["desktop", "mobile"],
              default: "desktop"
            },
            location: {
              type: "string"
            },
            safe: {
              type: "string",
              enum: ["active", "off"]
            }
          },
          required: ["query"]
        }
      },
      {
        name: "research_keywords",
        description: "Pesquisar palavras-chave relacionadas a um tópico ou palavra-chave inicial",
        inputSchema: {
          $schema: "http://json-schema.org/draft-07/schema#",
          type: "object",
          additionalProperties: false,
          properties: {
            keyword: {
              type: "string" 
            },
            language: {
              type: "string"
            },
            location: {
              type: "string"
            },
            include_questions: {
              type: "boolean",
              default: false
            },
            include_related: {
              type: "boolean",
              default: false 
            },
            include_suggestions: {
              type: "boolean",
              default: false
            }
          },
          required: ["keyword"]
        }
      },
      {
        name: "analyze_competitors",
        description: "Analisar concorrentes para uma palavra-chave ou domínio específico",
        inputSchema: {
          $schema: "http://json-schema.org/draft-07/schema#",
          type: "object",
          additionalProperties: false,
          properties: {
            domain: {
              type: "string"
            },
            keyword: {
              type: "string"
            },
            include_features: {
              type: "boolean"
            },
            num_results: {
              type: "number",
              minimum: 1,
              maximum: 100
            }
          },
          required: ["domain"]
        }
      },
      {
        name: "google_search",
        description:
          "Ferramenta para realizar buscas na web via API Serper e recuperar resultados completos. Capaz de recuperar resultados orgânicos de busca, pessoas também perguntam, buscas relacionadas e gráfico de conhecimento.",
        inputSchema: searchInputSchema,
      },
      {
        name: "scrape",
        description:
          "Ferramenta para extrair o conteúdo de uma página web e recuperar o texto e, opcionalmente, o conteúdo em markdown. Também recupera os metadados JSON-LD e os metadados do cabeçalho.",
        inputSchema: {
          type: "object",
          properties: {
            url: {
              type: "string",
              description: "A URL da página web para extrair.",
            },
            includeMarkdown: {
              type: "boolean",
              description: "Se deve incluir conteúdo em markdown.",
              default: false,
            },
          },
          required: ["url"],
        },
      },
    ],
  };
});

/**
 * Manipulador para as ferramentas de busca e análise.
 * Realiza buscas e análises usando a API Serper e retorna os resultados.
 */
server.setRequestHandler(CallToolRequestSchema, async (request) => {
  switch (request.params.name) {
    case "_health": {
      try {
        const result = await searchTools.health();
        return {
          content: [
            {
              type: "text",
              text: "Servidor está saudável"
            },
          ],
        };
      } catch (error) {
        throw new Error(`Verificação de saúde falhou: ${error}`);
      }
    }
    
    case "analyze_serp": {
      const { 
        query, 
        gl = "us", 
        hl = "en", 
        google_domain = "google.com", 
        num = 10, 
        device = "desktop", 
        location, 
        safe 
      } = request.params.arguments || {};
      
      if (!query) {
        throw new Error("Consulta é obrigatória para análise de SERP");
      }
      
      try {
        const result = await searchTools.analyzeSERP({
          query: String(query),
          gl: gl as string,
          hl: hl as string,
          num: Number(num),
          device: (device as string) as "desktop" | "mobile",
          location: location as string | undefined,
          google_domain: google_domain as string,
          safe: (safe as string) as "active" | "off" | undefined
        });
        
        return {
          content: [
            {
              type: "text",
              text: result.analyzedData
            },
          ],
        };
      } catch (error) {
        throw new Error(`Análise de SERP falhou: ${error}`);
      }
    }
    
    case "research_keywords": {
      const { 
        keyword, 
        language, 
        location, 
        include_questions = false, 
        include_related = false, 
        include_suggestions = false 
      } = request.params.arguments || {};
      
      if (!keyword) {
        throw new Error("Palavra-chave é obrigatória para pesquisa de palavras-chave");
      }
      
      try {
        const result = await searchTools.researchKeywords({
          keyword: String(keyword),
          language: language as string | undefined,
          location: location as string | undefined,
          include_questions: Boolean(include_questions),
          include_related: Boolean(include_related),
          include_suggestions: Boolean(include_suggestions)
        });
        
        return {
          content: [
            {
              type: "text",
              text: result.keywordData
            },
          ],
        };
      } catch (error) {
        throw new Error(`Pesquisa de palavras-chave falhou: ${error}`);
      }
    }
    
    case "analyze_competitors": {
      const { 
        domain, 
        keyword, 
        include_features = false, 
        num_results 
      } = request.params.arguments || {};
      
      if (!domain) {
        throw new Error("Domínio é obrigatório para análise de concorrentes");
      }
      
      try {
        const result = await searchTools.analyzeCompetitors({
          domain: String(domain),
          keyword: keyword as string | undefined,
          include_features: Boolean(include_features),
          num_results: num_results ? Number(num_results) : undefined
        });
        
        return {
          content: [
            {
              type: "text",
              text: result.competitorData
            },
          ],
        };
      } catch (error) {
        throw new Error(`Análise de concorrentes falhou: ${error}`);
      }
    }

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
          tbs: tbs as "qdr:h" | "qdr:d" | "qdr:w" | "qdr:m" | "qdr:y" | undefined,
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
              text: JSON.stringify(result, null, 2),
            },
          ],
        };
      } catch (error) {
        throw new Error(`Busca falhou: ${error}`);
      }
    }

    case "scrape": {
      const url = request.params.arguments?.url as string;
      const includeMarkdown = request.params.arguments
        ?.includeMarkdown as boolean;
      const result = await searchTools.scrape({ url, includeMarkdown });
      return {
        content: [
          {
            type: "text",
            text: JSON.stringify(result, null, 2),
          },
        ],
      };
    }

    default:
      throw new Error("Ferramenta desconhecida");
  }
});

// Trata requisições prompts/list
server.setRequestHandler(ListPromptsRequestSchema, async () => {
  return prompts.listPrompts();
});

// Trata requisições prompts/get
server.setRequestHandler(GetPromptRequestSchema, async (request) => {
  return prompts.getPrompt(request.params.name, request.params.arguments || {});
});

/**
 * Inicia o servidor usando transporte stdio.
 */
async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);
}

main().catch((error) => {
  console.error("Erro do servidor:", error);
  process.exit(1);
});
