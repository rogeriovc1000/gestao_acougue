import streamlit as st
import sqlite3
import os, re
import pandas as pd
from validar_cadastros_modulo import validar_cadastros_main

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
def criar_tabela_cliente(conn):
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

# Função para cadastrar cliente
def cadastrar_cliente(conn, nome_cliente, endereco_cliente, telefone_cliente, email_cliente):
    try:
        # Validação do telefone
        if not re.match(r'^\d{10,11}$', telefone_cliente):
            st.error("Telefone inválido. Use apenas números (10-11 dígitos).")
            return False  # Retorna False se o telefone for inválido

        # Verifica se o cliente já existe
        cursor = conn.cursor()
        cursor.execute("""
            SELECT COUNT(*) FROM TB_CLIENTE
            WHERE NOME_CLIENTE = ?
        """, (nome_cliente,))
        count = cursor.fetchone()[0]
        
        if count > 0:
            st.error("Erro: Cliente já cadastrado.")
            return False  # Retorna False se o cliente já existir

        cursor.execute("""
            INSERT INTO TB_CLIENTE (NOME_CLIENTE, ENDERECO_CLIENTE, TELEFONE_CLIENTE, EMAIL_CLIENTE)
            VALUES (?, ?, ?, ?)
        """, (nome_cliente, endereco_cliente, telefone_cliente, email_cliente))
        conn.commit()
        cursor.close()
        st.success("Cliente cadastrado com sucesso!")
        return True
    except sqlite3.Error as e:
        st.error(f"Erro ao cadastrar cliente: {e}")
        return False

# Função para carregar todos os clientes em um DataFrame
def carregar_clientes(conn):
    query = "SELECT * FROM TB_CLIENTE"
    return pd.read_sql(query, conn)

# Função para excluir cliente com confirmação
def excluir_cliente(id_cliente_excluir):
    conn = conectar_banco()
    
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM TB_CLIENTE WHERE ID_CLIENTE = ?", (id_cliente_excluir,))
        conn.commit()
        st.success(f"Cliente com ID {id_cliente_excluir} excluído com sucesso!")
    except sqlite3.Error as e:
        st.error(f"Erro ao excluir cliente: {e}")
    finally:
        if conn:
            conn.close()

# Função para conectar ao banco de dados
def conectar_banco():
    conn = sqlite3.connect('bancodedados/acougue_db.db')
    return conn

def buscar_cliente():
    # Interface para buscar cliente
    st.header("Buscar Cliente")
    nome_cliente = st.text_input("Digite o nome do cliente")
    
    if st.button("Buscar"):
        if nome_cliente:
            try:
                conn = conectar_banco()  # Conectar ao banco de dados
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT * FROM TB_CLIENTE
                    WHERE NOME_CLIENTE LIKE ?
                """, (f"%{nome_cliente}%",))
                clientes = cursor.fetchall()
                cursor.close()
                conn.close()  # Fechar a conexão após a consulta
                
                if clientes:
                    st.write("Clientes encontrados:")
                    for cliente in clientes:
                        st.write(f"ID: {cliente[0]}")
                        st.write(f"Nome: {cliente[1]}")
                        st.write(f"Endereço: {cliente[2]}")
                        st.write(f"Telefone: {cliente[3]}")
                        st.write(f"Email: {cliente[4]}")
                        st.write("---")
                else:
                    st.warning("Nenhum cliente encontrado.")
            except sqlite3.Error as e:
                st.error(f"Erro ao buscar cliente: {e}")
        else:
            st.warning("Por favor, digite um nome para buscar.")

# Função principal
def main():
    st.title("Cadastro e Manutenção de Clientes")

    # Barra lateral esquerda
    sidebar = st.sidebar
    sidebar.title("Opções")
    opcoes = ["Listar Clientes", "Cadastrar Cliente", "Buscar Cliente", "Excluir Cliente"]
    opcao_selecionada = sidebar.selectbox("Selecione uma opção", opcoes)

    conn = conectar_banco()
    if conn is None:
        st.error("Erro ao conectar ao banco de dados")
        return

    # Criar a tabela se não existir
    criar_tabela_cliente(conn)

    if opcao_selecionada == "Cadastrar Cliente":
        # Esconde o selectbox
        sidebar.empty()
        # Chame a função de cadastro de cliente
        validar_cadastros_main()

    elif opcao_selecionada == "Buscar Cliente":
        # Interface para buscar cliente
        sidebar.empty()
        buscar_cliente()
    # Modificação na parte de exclusão do cliente
    elif opcao_selecionada == "Excluir Cliente":
        clientes_df = carregar_clientes(conn)
        if not clientes_df.empty:
            st.write(clientes_df)
        else:
            st.warning("Nenhum cliente cadastrado.")

        id_cliente_excluir = st.text_input("Digite o ID do Cliente a ser excluído")
        
        if id_cliente_excluir:
            if st.button("Confirmar Exclusão"):
                try:
                    excluir_cliente(int(id_cliente_excluir))
                except ValueError:
                    st.error("Por favor, digite um ID válido.")
        else:
            st.warning("Por favor, digite um ID para excluir.")
            
    elif opcao_selecionada == "Listar Clientes":
        # Interface para listar todos os clientes
        st.header("Listar Clientes")
        clientes_df = carregar_clientes(conn)
        
        if not clientes_df.empty:
            # Torna o DataFrame editável
            edited_df = st.data_editor(
                clientes_df, 
                num_rows="dynamic",  # Permite adicionar/remover linhas
                column_config={
                    "ID_CLIENTE": st.column_config.NumberColumn("ID", disabled=True),
                    "NOME_CLIENTE": st.column_config.TextColumn("Nome"),
                    "ENDERECO_CLIENTE": st.column_config.TextColumn("Endereço"),
                    "TELEFONE_CLIENTE": st.column_config.TextColumn("Telefone"),
                    "EMAIL_CLIENTE": st.column_config.TextColumn("Email")
                },
                hide_index=True
            )
            
            # Botão para salvar alterações
            if st.button("Salvar Alterações"):
                try:
                    # Lógica para atualizar no banco de dados
                    for index, row in edited_df.iterrows():
                        conn.execute("""
                            UPDATE TB_CLIENTE 
                            SET NOME_CLIENTE = ?, 
                                ENDERECO_CLIENTE = ?, 
                                TELEFONE_CLIENTE = ?, 
                                EMAIL_CLIENTE = ? 
                            WHERE ID_CLIENTE = ?
                        """, (
                            row['NOME_CLIENTE'], 
                            row['ENDERECO_CLIENTE'], 
                            row['TELEFONE_CLIENTE'], 
                            row['EMAIL_CLIENTE'], 
                            row['ID_CLIENTE']
                        ))
                    
                    conn.commit()
                    st.success("Alterações salvas com sucesso!")
                
                except Exception as e:
                    st.error(f"Erro ao salvar alterações: {e}")
                    conn.rollback()
        
        else:
            st.warning("Nenhum cliente cadastrado.")

        # Fechar conexão
        conn.commit()
        conn.close()

# Verifica se o script está sendo executado diretamente
if __name__ == "__main__":
    main()