#!/usr/bin/env python3

"""
Implementação do servidor MCP que fornece recursos de busca na web via API Serper em Python.
Esta é uma migração da versão TypeScript.
"""

import os
import json
import sys
from typing import Dict, Any, List, Optional
import logging

# Configuração de logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stderr)]
)
logger = logging.getLogger("serper-mcp-server")

from services.serper_client import SerperClient
from tools.search_tools import SerperSearchTools

# Inicializa cliente Serper com a chave da API do ambiente
serper_api_key = os.environ.get("SERPER_API_KEY")
if not serper_api_key:
    raise ValueError("Variável de ambiente SERPER_API_KEY é obrigatória")

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
        },
        "required": ["q", "gl", "hl"]
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
        },
        "required": ["url"]
    },
    "_health": {
        "description": "Endpoint de verificação de saúde",
        "parameters": {
            "random_string": {
                "description": "Parâmetro fictício para ferramentas sem parâmetros",
                "type": "string"
            }
        },
        "required": ["random_string"]
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
                "minimum": 1,
                "maximum": 100,
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
        },
        "required": ["query"]
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
        },
        "required": ["keyword"]
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
                "type": "number",
                "minimum": 1,
                "maximum": 100
            }
        },
        "required": ["domain"]
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
    "image_search": {
        "description": "Ferramenta para buscar imagens via API Serper e recuperar resultados incluindo miniaturas e informações de origem.",
        "parameters": {
            "q": {
                "description": "String de consulta para busca de imagens (ex: 'pôr do sol nas montanhas', 'gatos brincando')",
                "type": "string"
            },
            "gl": {
                "description": "Código de região opcional para resultados de imagens no formato ISO 3166-1 alpha-2 (ex: 'us', 'br', 'pt')",
                "type": "string"
            },
            "hl": {
                "description": "Código de idioma opcional para resultados de imagens no formato ISO 639-1 (ex: 'en', 'pt', 'es')",
                "type": "string"
            },
            "num": {
                "description": "Número de resultados de imagens a retornar (padrão: 10)",
                "type": "number"
            },
            "location": {
                "description": "Localização opcional para resultados de imagens (ex: 'São Paulo, Brasil', 'Rio de Janeiro, Brasil')",
                "type": "string"
            }
        },
        "required": ["q"]
    },
    "video_search": {
        "description": "Ferramenta para buscar vídeos usando a API Serper.",
        "parameters": {
            "q": {
                "description": "String de consulta para busca de vídeos (ex: 'tutoriais de programação', 'receitas de bolo')",
                "type": "string"
            },
            "gl": {
                "description": "Código de região opcional para resultados de vídeos (ex: 'us', 'br', 'pt')",
                "type": "string"
            },
            "hl": {
                "description": "Código de idioma opcional para resultados de vídeos (ex: 'en', 'pt', 'es')",
                "type": "string"
            },
            "num": {
                "description": "Número de vídeos a retornar (padrão: 10)",
                "type": "number"
            },
            "location": {
                "description": "Localização específica para resultados de vídeos (ex: 'São Paulo, Brasil')",
                "type": "string"
            }
        },
        "required": ["q"]
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
    """Função principal para executar o servidor MCP."""
    logger.info("Iniciando Servidor MCP Serper em Python")
    
    try:
        # Loop para comunicação stdin/stdout
        for line in sys.stdin:
            try:
                message = json.loads(line)
                response = handle_message(message)
                
                # Envia resposta
                json_response = json.dumps(response)
                sys.stdout.write(json_response + "\n")
                sys.stdout.flush()
                
            except json.JSONDecodeError:
                logger.error(f"Falha ao analisar mensagem: {line}")
                continue
    except KeyboardInterrupt:
        logger.info("Desligando Servidor MCP Serper")
        sys.exit(0)


if __name__ == "__main__":
    main() 