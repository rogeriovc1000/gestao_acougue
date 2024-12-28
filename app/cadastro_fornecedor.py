import streamlit as st
import os
import sqlite3
import pandas as pd

# Define the path and name of the database file
db_file = os.path.join(os.getcwd(), 'bancodedados/acougue_db.db')

def conectar_banco():
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except sqlite3.Error as e:
        st.error(f"Erro ao conectar ao banco de dados: {e}")
        return None

def desconectar_banco(conn):
    conn.close()

def criar_tabela():
    conn = conectar_banco()
    if conn:
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS TB_FORNECEDOR
                        (ID_FORNECEDOR INTEGER PRIMARY KEY AUTOINCREMENT, NOME_FORNECEDOR VARCHAR(50), ENDERECO_FORNECEDOR VARCHAR(100), TELEFONE_FORNECEDOR VARCHAR(20), EMAIL_FORNECEDOR VARCHAR(50))''')
        conn.commit()
        desconectar_banco(conn)

def listar_fornecedores():
    conn = conectar_banco()
    if conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM TB_FORNECEDOR")
        fornecedores = cursor.fetchall()
        desconectar_banco(conn)

        if fornecedores:
            df = pd.DataFrame(fornecedores, columns=['ID', 'Nome', 'Endereço', 'Telefone', 'Email'])
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.write("Nenhum fornecedor cadastrado.")

def criar_fornecedor(nome, endereco, telefone, email):
    conn = conectar_banco()
    if conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO TB_FORNECEDOR (NOME_FORNECEDOR, ENDERECO_FORNECEDOR, TELEFONE_FORNECEDOR, EMAIL_FORNECEDOR) VALUES (?, ?, ?, ?)",
                       (nome, endereco, telefone, email))
        conn.commit()
        desconectar_banco(conn)

def atualizar_fornecedor(id_fornecedor_atualizar, nome, endereco, telefone, email):
    conn = conectar_banco()
    if conn:
        cursor = conn.cursor()
        cursor.execute("UPDATE TB_FORNECEDOR SET NOME_FORNECEDOR = ?, ENDERECO_FORNECEDOR = ?, TELEFONE_FORNECEDOR = ?, EMAIL_FORNECEDOR = ? WHERE ID_FORNECEDOR = ?",
                       (nome, endereco, telefone, email, id_fornecedor_atualizar))
        conn.commit()
        desconectar_banco(conn)

def excluir_fornecedor(id_fornecedor_excluir):
    conn = conectar_banco()
    if conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM TB_FORNECEDOR WHERE ID_FORNECEDOR = ?", (id_fornecedor_excluir,))
        conn.commit()
        desconectar_banco(conn)

def criar_fornecedor_form():
    with st.form(key='form_criar_fornecedor'):
        nome_fornecedor = st.text_input("Nome Fornecedor")
        endereco = st.text_input("Endereço")
        telefone = st.text_input("Telefone")
        email = st.text_input("Email")

        if st.form_submit_button("Criar Fornecedor"):
            criar_fornecedor(nome_fornecedor, endereco, telefone, email)
            st.success("Fornecedor criado com sucesso!")

def atualizar_fornecedor_form(id_fornecedor_atualizar):
    conn = conectar_banco()
    if conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM TB_FORNECEDOR WHERE ID_FORNECEDOR = ?", (id_fornecedor_atualizar,))
        fornecedor = cursor.fetchone()
        desconectar_banco(conn)

        if fornecedor:
            with st.form(key=f'form_atualizar_fornecedor_{id_fornecedor_atualizar}'):
                nome_fornecedor = st.text_input("Nome Fornecedor", value=fornecedor[1])
                endereco = st.text_input("Endereço", value=fornecedor[2])
                telefone = st.text_input("Telefone", value=fornecedor[3])
                email = st.text_input("Email", value=fornecedor[4])

                if st.form_submit_button("Salvar Alterações"):
                    atualizar_fornecedor(id_fornecedor_atualizar, nome_fornecedor, endereco, telefone, email)
                    st.success("Fornecedor atualizado com sucesso!")
        else:
            st.error("Fornecedor não encontrado.")

def main():
    st.sidebar.caption("Robust - Sistema de Gestão")
    
    if 'menu_counter' not in st.session_state:
        st.session_state.menu_counter = 0

    menu = st.sidebar.selectbox("Menu", 
                                 ["Listar Fornecedores", 
                                  "Criar Fornecedor", 
                                  "Atualizar Fornecedor", 
                                  "Excluir Fornecedor"], 
                                 key=f'menu_unique_{st.session_state.menu_counter}')

    if st.sidebar.button(f"Voltar_{st.session_state.menu_counter}"):
        st.session_state.current_page = 'tela_entrada'
        st.rerun()

    st.title("Manutenção de Fornecedores")
    criar_tabela()

    if menu == "Listar Fornecedores":
        listar_fornecedores()

    elif menu == "Criar Fornecedor":
        criar_fornecedor_form()

    elif menu == "Atualizar Fornecedor":
        id_fornecedor_atualizar = st.text_input("Digite o ID do fornecedor a ser atualizado", key=f'id_fornecedor_atualizar_{st.session_state.menu_counter}')
        if id_fornecedor_atualizar:
            atualizar_fornecedor_form(int(id_fornecedor_atualizar))

    elif menu == "Excluir Fornecedor":
        id_fornecedor_excluir = st.text_input("Digite o ID do fornecedor a ser excluído", key=f'id_fornecedor_excluir_{st.session_state.menu_counter}')
        if id_fornecedor_excluir:
            excluir_fornecedor(int(id_fornecedor_excluir))
            st.success(f"Fornecedor com ID {id_fornecedor_excluir} excluído com sucesso!")

def show_screen(screen_name):
    if screen_name == "tela_entrada":
        st.title("Tela de Entrada")
        # Adicione aqui os componentes da tela de entrada
    elif screen_name == "manutencao_fornecedores":
        main()

def render_page():
    if 'current_screen' not in st.session_state:
        st.session_state.current_screen = "tela_entrada"  # Inicializa a tela atual

    show_screen(st.session_state.current_screen)

    # Exemplo de como mudar a tela com um botão
    if st.button("Ir para Manutenção de Fornecedores"):
        st.session_state.current_screen = "manutencao_fornecedores"
        st.experimental_rerun()  # Rerun para atualizar a tela

if __name__ == "__main__":
    render_page()