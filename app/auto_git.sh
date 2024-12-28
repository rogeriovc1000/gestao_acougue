#!/bin/bash
# Script para automatizar o pull, add, commit, push e uso do Git LFS

# Defina a mensagem de commit
COMMIT_MESSAGE="Atualizações automáticas"

# Instale o Git LFS, se necessário
git lfs install

# Rastreie tipos de arquivos grandes com o Git LFS
git lfs track "*.so"
git lfs track "*.py"

# Faça pull das mudanças remotas e mescle automaticamente
git pull origin main --rebase

# Adicione todas as mudanças
git add .

# Faça commit das mudanças
git commit -m "$COMMIT_MESSAGE"

# Adicione e faça commit dos arquivos rastreados pelo Git LFS
git add .gitattributes
git commit -m "Usando Git LFS para arquivos grandes"

# Empurre as mudanças para o repositório remoto

gut push origin main --force
