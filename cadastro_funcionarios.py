import streamlit as st
import sqlite3
import os
import pandas as pd
import re
from validar_cadastros_modulo import validar_cadastros_main  # Supondo que você tenha essa função para validação

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

# Função para criar a tabela TB_FUNCIONARIO
def criar_tabela_funcionario(conn):
    try:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS TB_FUNCIONARIOS (
                ID_FUNCIONARIOS INTEGER PRIMARY KEY AUTOINCREMENT,
                NOME_FUNCIONARIOS TEXT NOT NULL,
                CARGO TEXT NOT NULL,
                SALARIO DECIMAL(10, 2),
                TELEFONE_FUNCIONARIOS TEXT NOT NULL,
                EMAIL_FUNCIONARIOS TEXT NOT NULL
            )
        """)
        conn.commit()
        cursor.close()
    except sqlite3.Error as e:
        st.error(f"Erro ao criar tabela: {e}")

# Função para cadastrar funcionário
def cadastrar_FUNCIONARIOS(conn, nome_funcionario, cargo, salario, telefone_funcionario, email_funcionario):
    try:
        # Verifica se o funcionário já existe
        cursor = conn.cursor()
        cursor.execute("""
            SELECT COUNT(*) FROM TB_FUNCIONARIOS
            WHERE NOME_FUNCIONARIO = ?
        """, (nome_funcionario,))
        count = cursor.fetchone()[0]
        
        if count > 0:
            st.error("Erro: Funcionário já cadastrado.")
            return False  # Retorna False se o funcionário já existir

        cursor.execute("""
            INSERT INTO TB_FUNCIONARIOS (NOME_FUNCIONARIO, CARGO, SALARIO, TELEFONE_FUNCIONARIO, EMAIL_FUNCIONARIO)
            VALUES (?, ?, ?, ?, ?)
        """, (nome_funcionario, cargo, salario, telefone_funcionario, email_funcionario))
        conn.commit()
        cursor.close()
        st.success("Funcionário cadastrado com sucesso!")
        return True
    except sqlite3.Error as e:
        st.error(f"Erro ao cadastrar funcionário: {e}")
        return False

# Função para carregar todos os funcionários em um DataFrame
def carregar_funcionarios(conn):
    
    query = "SELECT * FROM TB_FUNCIONARIOS"
    return pd.read_sql(query, conn)

def excluir_funcionario(id_funcionario_excluir):
    conn = conectar_banco()
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM TB_FUNCIONARIOS WHERE ID_FUNCIONARIO = ?", (id_funcionario_excluir,))
        conn.commit()
        st.success(f"Funcionário com ID {id_funcionario_excluir} excluído com sucesso!")
    except sqlite3.Error as e:
        st.error(f"Erro ao excluir funcionário: {e}")
    finally:
        if conn:
            conn.close()

def buscar_funcionario():
    # Interface para buscar funcionário
    st.header("Buscar Funcionário")
    nome_funcionario = st.text_input("Digite o nome do funcionário")
    
    if st.button("Buscar"):
        if nome_funcionario:
            try:
                conn = conectar_banco()  # Conectar ao banco de dados
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT * FROM TB_FUNCIONARIOS
                    WHERE NOME_FUNCIONARIO LIKE ?
                """, (f"%{nome_funcionario}%",))
                funcionarios = cursor.fetchall()
                cursor.close()
                conn.close()  # Fechar a conexão após a consulta
                
                if funcionarios:
                    st.write("Funcionários encontrados:")
                    for funcionario in funcionarios:
                        st.write(f"ID: {funcionario[0]}")
                        st.write(f"Nome: {funcionario[1]}")
                        st.write(f"Cargo: {funcionario[2]}")
                        st.write(f"Salário.: {funcionario[3]}")
                        st.write(f"Telefone: {funcionario[4]}")
                        st.write(f"Email: {funcionario[5]}")
                        st.write("---")
                else:
                    st.warning("Nenhum funcionário encontrado.")
            except sqlite3.Error as e:
                st.error(f"Erro ao buscar funcionário: {e}")
        else:
            st.warning("Por favor, digite um nome para buscar.")

# Função principal
def main():
    st.title("Cadastro e Manutenção de Funcionários")

    # Barra lateral esquerda
    sidebar = st.sidebar
    
    opcoes = ["Listar Funcionários", "Cadastrar Funcionário", "Buscar Funcionário", "Excluir Funcionário"]
    opcao_selecionada = sidebar.selectbox("Selecione uma opção", opcoes)

    conn = conectar_banco()
    if conn is None:
        st.error("Erro ao conectar ao banco de dados")
        return

    # Criar a tabela se não existir
    criar_tabela_funcionario(conn)

    if opcao_selecionada == "Cadastrar Funcionário":
        # Esconde o selectbox
        sidebar.empty()
        # Campos para cadastro de funcionário
        with st.form(key='formulario_funcionario'):
            nome_funcionario = st.text_input("Nome Completo", help="Digite o nome completo do funcionário")
            cargo = st.text_input("Cargo", help="Digite o cargo do funcionário")
            salario = st.number_input("Salário", help="Digite o salário do funcionário")
            telefone_funcionario = st.text_input("Telefone", help="Digite apenas números (DDD + número)")
            email_funcionario = st.text_input("Email", help="Digite um email válido (exemplo@dominio.com)")

            submit_button = st.form_submit_button(label="Cadastrar Funcionário")
            
            if submit_button:
                cadastrar_FUNCIONARIOS(conn, nome_funcionario, cargo, salario, telefone_funcionario, email_funcionario)

    elif opcao_selecionada == "Buscar Funcionário":
        # Interface para buscar funcionário
        sidebar.empty()
        buscar_funcionario()

    elif opcao_selecionada == "Excluir Funcionário":
        funcionarios_df = carregar_funcionarios(conn)
        if not funcionarios_df.empty:
            st.write(funcionarios_df)
        else:
            st.warning("Nenhum funcionário cadastrado.")
        id_funcionario_excluir = st.text_input("Digite o ID do Funcionário a ser excluído")
        if st.button("Excluir"):
            if id_funcionario_excluir:
                try:
                    excluir_funcionario(int(id_funcionario_excluir))
                except ValueError:
                    st.error("Por favor, digite um ID válido.")

    elif opcao_selecionada == "Listar Funcionários":
        st.header("Listar Funcionários")
        
        # Verifica a conexão
        if conn is None:
            st.error("Erro ao conectar ao banco de dados")
            return
        
        # Verifica se a tabela existe
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='TB_FUNCIONARIOS';")
        table_exists = cursor.fetchone()
        if not table_exists:
            st.error("Tabela TB_FUNCIONARIOS não existe.")
            return
        
        # Verifica o número de registros
        cursor.execute("SELECT COUNT(*) FROM TB_FUNCIONARIOS;")
        count = cursor.fetchone()[0]
        st.write(f"Número de registros na tabela: {count}")
        
        # Carrega os funcionários
        funcionarios_df = carregar_funcionarios(conn)
        
        if not funcionarios_df.empty:
            # Torna o DataFrame editável
            edited_df = st.data_editor(
                funcionarios_df, 
                num_rows="dynamic",  
                column_config={
                    "ID_FUNCIONARIO": st.column_config.NumberColumn("ID", disabled=True),
                    "NOME_FUNCIONARIO": st.column_config.TextColumn("Nome"),
                    "CARGO": st.column_config.TextColumn("Cargo"),
                    "SALARIO": st.column_config.NumberColumn("Salário"),
                    "TELEFONE_FUNCIONARIO": st.column_config.TextColumn("Telefone"),
                    "EMAIL_FUNCIONARIO": st.column_config.TextColumn("Email")
                },
                hide_index=True
            )
            
            # Botão para salvar alterações
            if st.button("Salvar Alterações"):
                try:
                    for index, row in edited_df.iterrows():
                        conn.execute("""
                            UPDATE TB_FUNCIONARIOS 
                            SET NOME_FUNCIONARIO = ?, 
                                CARGO = ?,
                                SALARIO = ?,
                                TELEFONE_FUNCIONARIO = ?, 
                                EMAIL_FUNCIONARIO = ? 
                            WHERE ID_FUNC
                            WHERE ID_FUNCIONARIO = ?
                        """, (
                            row['NOME_FUNCIONARIO'], 
                            row['CARGO'],
                            row['SALARIO'],
                            row['TELEFONE_FUNCIONARIO'],
                            row['EMAIL_FUNCIONARIO'],
                            row['ID_FUNCIONARIO']
                        ))
                    
                    conn.commit()
                    st.success("Alterações salvas com sucesso!")
                
                except Exception as e:
                    st.error(f"Erro ao salvar alterações: {e}")
                    conn.rollback()
        
        else:
            st.warning("Nenhum funcionário cadastrado.")

        # Fechar conexão
        conn.commit()
        conn.close()

# Verifica se o script está sendo executado diretamente
if __name__ == "__main__":
    main()