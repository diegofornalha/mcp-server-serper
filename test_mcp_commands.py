#!/usr/bin/env python3

"""
Script para testar os comandos youtube_search e instagram_search do MCP.
"""

import json
import sys
import uuid

def create_call_tool_message(tool_name, arguments):
    """
    Cria uma mensagem para chamar uma ferramenta MCP.
    
    Args:
        tool_name: Nome da ferramenta a ser chamada
        arguments: Argumentos para a ferramenta
        
    Returns:
        Mensagem formatada como JSON
    """
    message_id = str(uuid.uuid4())
    message = {
        "id": message_id,
        "method": "mcp.CallTool",
        "params": {
            "name": tool_name,
            "arguments": arguments
        }
    }
    return json.dumps(message)

def main():
    """Função principal para testar os comandos MCP."""
    # Testar youtube_search
    youtube_message = create_call_tool_message("youtube_search", {
        "q": "inteligência artificial",
        "gl": "br",
        "hl": "pt-br",
        "num": 5,
        "location": "Brazil"
    })
    
    print("\n--- Mensagem para youtube_search ---")
    print(youtube_message)
    print("\nEnvie a mensagem acima para o servidor MCP (através de stdin).")
    print("Para testar, execute: python main.py < youtube_message.json")
    
    # Salvar mensagem em um arquivo para uso posterior
    with open("youtube_message.json", "w") as f:
        f.write(youtube_message)
    
    # Testar instagram_search
    instagram_message = create_call_tool_message("instagram_search", {
        "q": "viagens brasil",
        "gl": "br",
        "hl": "pt-br",
        "num": 5,
        "location": "Brazil"
    })
    
    print("\n--- Mensagem para instagram_search ---")
    print(instagram_message)
    print("\nEnvie a mensagem acima para o servidor MCP (através de stdin).")
    print("Para testar, execute: python main.py < instagram_message.json")
    
    # Salvar mensagem em um arquivo para uso posterior
    with open("instagram_message.json", "w") as f:
        f.write(instagram_message)
    
    print("\n--- Instruções ---")
    print("1. Certifique-se de que o servidor MCP esteja em execução (python main.py)")
    print("2. Execute os comandos acima para testar os comandos youtube_search e instagram_search")

if __name__ == "__main__":
    main() 