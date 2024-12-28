import streamlit as st
st.set_page_config(page_title="Minha Aplicação", layout="wide")
import sqlite3
import pandas as pd
import os
from config import rodape, main
import importlib
import cadastro_usuarios as usu
# Importa o módulo de backup
import Backup_sistema  # Certifique-se de que o arquivo Backup_sistema.py está no mesmo diretório
from configuracoes import *

# Verifica se o diretório do banco de dados existe
if not os.path.exists('bancodedados'):
    os.makedirs('bancodedados')

# Função para conectar ao banco de dados
def conectar_banco():
    conn = sqlite3.connect('bancodedados/acougue_db.db')  # Substitua pelo caminho do seu banco de dados
    return conn

# Função para verificar se o usuário está logado
def verificar_login():
    if 'usuario_logado' not in st.session_state:
        st.session_state.usuario_logado = False
    if 'usuario_atual' not in st.session_state:
        st.session_state.usuario_atual = None  # Inicializa a variável

# Função de login
def tela_login():
    st.title("Login")
    usuario = st.text_input("Usuário")
    senha = st.text_input("Senha", type="password")

    if st.button("Entrar"):
        conn = conectar_banco()  # Conectar ao banco de dados
        query = "SELECT * FROM TB_USUARIO WHERE NOME_USUARIO = ? AND SENHA = ?"
        df = pd.read_sql_query(query, conn, params=(usuario, senha))

        if not df.empty:
            st.session_state.usuario_logado = True
            st.session_state.usuario_atual = usuario  # Armazena o usuário atual
            st.success("Login realizado com sucesso!")
            st.rerun()  # Rerun para atualizar a tela
        else:
            st.error("Nome de usuário ou senha incorretos.")
        
        conn.close()  # Fechar a conexão
    if st.button("Cadastrar Usuario"):
         usu.tela_cadastro()

def renderizar_paginas():
    # Definindo as páginas com títulos únicos
    pages = {
        "Clientes": "cadastro_clientes",
        "Contas a Pagar": "cadastro_contas_a_pagar",
        "Contas a Receber": "cadastro_contas_a_receber",
        "Fornecedor": "cadastro_fornecedor",
        "Categorias": "cadastro_categorias",
        "Funcionários": "cadastro_funcionarios",
        "Usuários": "cadastro_usuarios",
        "Movimentação": "listar_movimentacao",
        "Relatórios": "relatorios",
        "Relatórios Fluxo de Caixa": "relatorios_fluxo_caixa",
        "Fazer Backups/Restauração do Sistema": "backup_sistema",  # Adiciona a opção de backup
        "Configurações": "configuracoes",  # Adiciona a opção de configurações
    }

    # Configurando a navegação
    page_selection = st.sidebar.selectbox("Escolha uma página", list(pages.keys()))

    # Carregar a página selecionada
    if page_selection:
        if page_selection == "Fazer Backups/Restauração do Sistema":
            Backup_sistema.main()  # Chama a função principal do módulo de backup
        else:
            module = importlib.import_module(pages[page_selection])  # Importa o módulo
            module.main()  # Chama a função main do módulo importado

# Verificação de login
verificar_login()

# Se o usuário não estiver logado, exibe a tela de login
if not st.session_state.usuario_logado:
    tela_login()
else:
    # Se o usuário estiver logado, renderiza as outras páginas
    renderizar_paginas()