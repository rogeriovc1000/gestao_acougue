#!/bin/bash
# Script para automatizar o pull, add, commit e push no Git

# Defina a mensagem de commit
COMMIT_MESSAGE="Atualizações automáticas"

# Faça pull das mudanças remotas
git pull origin main

# Adicione todas as mudanças
git add .

# Faça commit das mudanças
git commit -m "$COMMIT_MESSAGE"

# Empurre as mudanças para o repositório remoto
git push origin main
