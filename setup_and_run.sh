#!/bin/bash

# Script para configurar e executar o servidor MCP Serper em Python

# Verificar se Python 3 está instalado
if ! command -v python3 &> /dev/null; then
    echo "Python 3 não está instalado. Por favor, instale-o antes de continuar."
    exit 1
fi

# Verificar se a variável de ambiente SERPER_API_KEY está definida
if [ -z "$SERPER_API_KEY" ]; then
    # Tentar carregar do arquivo .env se existir
    if [ -f .env ]; then
        export $(grep -v '^#' .env | xargs)
    fi
    
    # Verificar novamente se a chave foi carregada
    if [ -z "$SERPER_API_KEY" ]; then
        echo "SERPER_API_KEY não está definida. Por favor, defina essa variável de ambiente ou adicione-a a um arquivo .env."
        echo "Exemplo: echo 'SERPER_API_KEY=sua_chave_aqui' > .env"
        exit 1
    fi
fi

# Tornar executável se ainda não for
chmod +x mcp_serper_server.py

# Executar o servidor
echo "Iniciando o servidor MCP Serper em Python..."
./mcp_serper_server.py