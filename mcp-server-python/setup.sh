#!/bin/bash

# Script para instalação e execução do servidor MCP Python

# Configurações
VENV_DIR=".venv"
PYTHON="python3"
SERPER_API_KEY=${SERPER_API_KEY:-"sua_chave_api_serper"}

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Função para imprimir cabeçalho
print_header() {
    echo -e "\n${BLUE}=== $1 ===${NC}\n"
}

# Função para imprimir mensagem de sucesso
print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

# Função para imprimir mensagem de erro
print_error() {
    echo -e "${RED}✗ $1${NC}"
    exit 1
}

# Função para imprimir mensagem de aviso
print_warning() {
    echo -e "${YELLOW}! $1${NC}"
}

# Verifica se Python está instalado
check_python() {
    print_header "Verificando Python"
    if ! command -v $PYTHON &> /dev/null; then
        print_error "Python não encontrado. Por favor, instale Python 3.8 ou superior."
    else
        PYTHON_VERSION=$($PYTHON --version | cut -d' ' -f2)
        print_success "Python $PYTHON_VERSION encontrado."
    fi
}

# Cria ambiente virtual
create_venv() {
    print_header "Configurando ambiente virtual"
    if [ -d "$VENV_DIR" ]; then
        print_warning "Ambiente virtual já existe. Utilizando existente."
    else
        $PYTHON -m venv $VENV_DIR || print_error "Falha ao criar ambiente virtual."
        print_success "Ambiente virtual criado em $VENV_DIR."
    fi
    
    # Ativa o ambiente virtual
    source $VENV_DIR/bin/activate || print_error "Falha ao ativar ambiente virtual."
    print_success "Ambiente virtual ativado."
}

# Instala as dependências
install_deps() {
    print_header "Instalando dependências"
    pip install --upgrade pip || print_warning "Falha ao atualizar pip."
    pip install -e . || print_error "Falha ao instalar pacote."
    print_success "Dependências instaladas com sucesso."
}

# Cria arquivo .env
create_env_file() {
    print_header "Configurando variáveis de ambiente"
    if [ -f ".env" ]; then
        print_warning "Arquivo .env já existe. Mantendo existente."
    else
        cat > .env << EOF
# Configurações da API Serper
SERPER_API_KEY=$SERPER_API_KEY

# Configurações do servidor MCP
MCP_TOKEN=mcp-serper-token
HOST=127.0.0.1
PORT=3001
DEBUG=False

# Configurações de logging
LOG_LEVEL=INFO
EOF
        print_success "Arquivo .env criado."
        print_warning "Edite o arquivo .env para configurar sua chave API Serper e outras configurações."
    fi
}

# Executa o servidor
run_server() {
    print_header "Iniciando servidor MCP"
    if [ "$SERPER_API_KEY" == "sua_chave_api_serper" ]; then
        print_warning "Você está usando uma chave de API Serper de exemplo."
        print_warning "Edite o arquivo .env ou defina a variável de ambiente SERPER_API_KEY."
    fi
    
    print_success "Servidor iniciando..."
    mcp-server-serper
}

# Menu principal
main() {
    print_header "MCP Server Serper - Instalação"
    
    check_python
    create_venv
    install_deps
    create_env_file
    
    print_header "Instalação concluída com sucesso!"
    echo -e "Para iniciar o servidor manualmente:"
    echo -e "  1. Ative o ambiente virtual: ${YELLOW}source $VENV_DIR/bin/activate${NC}"
    echo -e "  2. Inicie o servidor: ${YELLOW}mcp-server-serper${NC}"
    echo
    
    # Pergunta se deseja iniciar o servidor agora
    read -p "Deseja iniciar o servidor agora? (s/n): " START_SERVER
    if [[ $START_SERVER == "s" || $START_SERVER == "S" || $START_SERVER == "y" || $START_SERVER == "Y" ]]; then
        run_server
    else
        print_success "Instalação concluída. Execute 'mcp-server-serper' para iniciar o servidor."
    fi
}

# Executa o programa principal
main 