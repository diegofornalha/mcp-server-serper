#!/usr/bin/env python3

"""
MCP server implementation that provides web search capabilities via Serper API in Python.
This is a migration from the TypeScript version.
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
            # Outros parâmetros omitidos por brevidade
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