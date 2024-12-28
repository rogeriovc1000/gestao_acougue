#!/bin/bash

# Verifique se um nome de ambiente foi fornecido
if [ -z "$1" ]; then
    echo "Uso: $0 nome_do_ambiente"
    exit 1
fi

# Defina o nome do ambiente virtual a partir do argumento
ENV_NAME=$1

# Verifique se o Python está instalado
if ! command -v python3 &> /dev/null; then
    echo "Python não está instalado. Por favor, instale o Python antes de continuar."
    exit 1
fi

# Crie o ambiente virtual
if [ ! -d "$ENV_NAME" ]; then
    echo "Criando o ambiente virtual \"$ENV_NAME\"..."
    python3 -m venv $ENV_NAME
    echo "Ambiente virtual \"$ENV_NAME\" criado com sucesso."
else
    echo "O ambiente virtual \"$ENV_NAME\" já existe."
fi

# Ativar o ambiente virtual
echo "Ativando o ambiente virtual \"$ENV_NAME\"..."
source $ENV_NAME/bin/activate

# Instalar dependências do requirements.txt, se existir
if [ -f requirements.txt ]; then
    echo "Instalando dependências do requirements.txt..."
    pip install -r requirements.txt
fi

echo "Ambiente virtual \"$ENV_NAME\" está pronto e ativado."