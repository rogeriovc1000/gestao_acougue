import streamlit as st
import sqlite3
import os
import pandas as pd
import re
from datetime import datetime

def validar_cadastros_main():
    # Funções de validação
    def validar_email(email):
        padrao_email = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(padrao_email, email) is not None

    def validar_telefone(telefone):
        telefone_limpo = re.sub(r'\D', '', telefone)
        return len(telefone_limpo) >= 10 and len(telefone_limpo) <= 11

    def validar_nome(nome):
        return re.match(r'^[A-Za-zÀ-ÿ\s]+$', nome) is not None

    def validar_endereco(endereco):
        return len(endereco.strip()) >= 5

    # Função para conectar ao banco de dados
    def conectar_banco():
        db_file = 'bancodedados/acougue_db.db'
        if not os.path.exists('bancodedados'):
            os.makedirs('bancodedados')
        
        try:
            conn = sqlite3.connect(db_file)
            return conn
        except sqlite3.Error as e:
            st.error(f"Erro ao conectar ao banco de dados: {e}")
            return None

    # Função para criar a tabela TB_CLIENTE
    def criar_tabela(conn):
        try:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS TB_CLIENTE (
                    ID_CLIENTE INTEGER PRIMARY KEY AUTOINCREMENT,
                    NOME_CLIENTE TEXT NOT NULL,
                    ENDERECO_CLIENTE TEXT NOT NULL,
                    TELEFONE_CLIENTE TEXT NOT NULL,
                    EMAIL_CLIENTE TEXT NOT NULL
                )
            """)
            conn.commit()
            cursor.close()
        except sqlite3.Error as e:
            st.error(f"Erro ao criar tabela: {e}")

    # Função para cadastrar cliente com validações
    def cadastrar_cliente(conn, nome_cliente, endereco_cliente, telefone_cliente, email_cliente):
        erros = []

        if not nome_cliente:
            erros.append("Nome é obrigatório.")
        elif not validar_nome(nome_cliente):
            erros.append("Nome inválido. Use apenas letras e espaços.")
        
        if not endereco_cliente:
            erros.append("Endereço é obrigatório.")
        elif not validar_endereco(endereco_cliente):
            erros.append("Endereço inválido. Deve ter pelo menos 5 caracteres.")
        
        if not telefone_cliente:
            erros.append("Telefone é obrigatório.")
        elif not validar_telefone(telefone_cliente):
            erros.append("Telefone inválido. Use apenas números (10-11 dígitos).")
        
        if not email_cliente:
            erros.append("Email é obrigatório.")
        elif not validar_email(email_cliente):
            erros.append("Email inválido. Use um formato de email válido.")

        if erros:
            for erro in erros:
                st.error(erro)
            return False

        try:
            telefone_limpo = re.sub(r'\D', '', telefone_cliente)

            cursor = conn.cursor()
            cursor.execute("""
                SELECT COUNT(*) FROM TB_CLIENTE
                WHERE NOME_CLIENTE = ? OR EMAIL_CLIENTE = ?
            """, (nome_cliente, email_cliente))
            count = cursor.fetchone()[0]
            
            if count > 0:
                st.error("Erro: Cliente já cadastrado com este nome ou email.")
                return False

            cursor.execute("""
                INSERT INTO TB_CLIENTE (NOME_CLIENTE, ENDERECO_CLIENTE, TELEFONE_CLIENTE, EMAIL_CLIENTE)
                VALUES (?, ?, ?, ?)
            """, (nome_cliente, endereco_cliente, telefone_limpo, email_cliente))
            conn.commit()
            cursor.close()
            st.success("Cliente cadastrado com sucesso!")
            return True
        except sqlite3.Error as e:
            st.error(f"Erro ao cadastrar cliente: {e}")
            return False

    # Função para buscar clientes
    def buscar_clientes(conn, nome_cliente):
        try:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM TB_CLIENTE
                WHERE NOME_CLIENTE LIKE ?
            """, (f"% {nome_cliente}%",))
            clientes = cursor.fetchall()
            cursor.close()
            
            return clientes
        except sqlite3.Error as e:
            st.error(f"Erro ao buscar cliente: {e}")
            return []

    # Conectar ao banco de dados
    conn = conectar_banco()
    if conn is None:
        st.error("Erro ao conectar ao banco de dados")
        return

    # Criar tabela se não existir
    criar_tabela(conn)

    with st.form(key='formulario_cliente'):
        col1, col2 = st.columns(2)
        
        with col1:
            nome_cliente = st.text_input("Nome Completo", 
                help="Digite seu nome completo usando apenas letras")
        
        with col2:
            email_cliente = st.text_input("Email", 
                help="Digite um email válido (exemplo@dominio.com)")
        
        col3, col4 = st.columns(2)
        
        with col3:
            telefone_cliente = st.text_input("Telefone", 
                help="Digite apenas números (DDD + número)")
        
        with col4:
            endereco_cliente = st.text_input("Endereço", 
                help="Digite seu endereço completo")
        
        submit_button = st.form_submit_button(label="Cadastrar Cliente")
        
        if submit_button:
            if cadastrar_cliente(conn, nome_cliente, endereco_cliente, telefone_cliente, email_cliente):
                # Limpar os campos após o cadastro bem-sucedido
                nome_cliente = ""
                email_cliente = ""
                telefone_cliente = ""
                endereco_cliente = ""

# Executar o script
if __name__ == "__main__":
    validar_cadastros_main()