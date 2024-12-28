import streamlit as st
import os
import sqlite3
import pandas as pd

# Defina o caminho e o nome do arquivo do banco de dados
db_file = os.path.join(os.getcwd(), 'bancodedados/acougue_db.db')

def conectar_banco():
    try:
        conn = sqlite3.connect(db_file)
        cursor = conn.cursor()  # Cria o cursor aqui
        return conn, cursor  # Retorna tanto a conexão quanto o cursor
    except sqlite3.Error as e:
        st.error(f"Erro ao conectar ao banco de dados: {e}")
        return None, None  # Retorna None para ambos se houver erro
    
def desconectar_banco(conn, cursor):
    cursor.close()
    conn.close()

def criar_tabela_usuario():
    conn, cursor = conectar_banco()
    if conn is not None and cursor is not None:  # Verifica se a conexão e o cursor foram criados
        cursor.execute('''CREATE TABLE IF NOT EXISTS TB_USUARIO
                        (ID_USUARIO INTEGER PRIMARY KEY AUTOINCREMENT, 
                         NOME_USUARIO VARCHAR(50), 
                         EMAIL_USUARIO VARCHAR(50), 
                         SENHA VARCHAR(50),
                         TIPO_USUARIO VARCHAR(50))''')
        conn.commit()
        desconectar_banco(conn, cursor)

def listar_usuarios():
    conn, cursor = conectar_banco()
    if conn is not None and cursor is not None:  # Verifica se a conexão e o cursor foram criados
        cursor.execute("SELECT * FROM TB_USUARIO")
        usuarios = cursor.fetchall()
        desconectar_banco(conn, cursor)

        if usuarios:
            df = pd.DataFrame(usuarios, columns=['ID', 'Nome', 'Email', 'Senha', 'Cargo'])
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.write("Nenhum usuário cadastrado.")

def criar_usuario_form():
    with st.form(key='form_criar_usuario'):
        nome_usuario = st.text_input("Nome do Usuário")
        email = st.text_input("Email")
        senha = st.text_input("Senha", type='password')

        # Definindo as opções de cargo
        opcoes_cargo = ["Administrador", "Usuário"]

        # Usando radio para escolher o cargo
        tipo_usuario = st.radio("Cargo:", opcoes_cargo)

        if st.form_submit_button("Criar Usuário"):
            criar_usuario(nome_usuario, senha, tipo_usuario, email)
            st.success("Usuário criado com sucesso!")

def criar_usuario(nome, senha, tipo_usuario, email):
    conn, cursor = conectar_banco()
    if conn is not None and cursor is not None:  # Verifica se a conexão e o cursor foram criados
        cursor.execute("INSERT INTO TB_USUARIO (NOME_USUARIO, SENHA, TIPO_USUARIO, EMAIL_USUARIO) VALUES (?, ?, ?, ?)",
                       (nome, senha, tipo_usuario, email))
        conn.commit()
        desconectar_banco(conn, cursor)

def atualizar_usuario_form(id_usuario_atualizar):
    conn, cursor = conectar_banco()
    if conn is not None and cursor is not None:  # Verifica se a conexão e o cursor foram criados
        cursor.execute("SELECT * FROM TB_USUARIO WHERE ID_USUARIO = ?", (id_usuario_atualizar,))
        usuario = cursor.fetchone()
        desconectar_banco(conn, cursor)

        if usuario:
            with st.form(key=f'form_atualizar_usuario_{id_usuario_atualizar}'):
                nome_usuario = st.text_input("Nome do Usuário", value=usuario[1])
                email = st.text_input("Email", value=usuario[3])  # Corrigido para acessar o email correto
                senha = st.text_input("Senha", value=usuario[2], type='password')  # Corrigido para acessar a senha correta
                
                # Definindo as opções de cargo
                opcoes_cargo = ["Administrador", "Usuário"]

                # Usando radio para escolher o cargo
                tipo_usuario = st.radio("Cargo:", opcoes_cargo, index= opcoes_cargo.index(usuario[4]) if usuario[4] in opcoes_cargo else 0)  # Corrigido para selecionar o cargo correto
                
                if st.form_submit_button("Salvar Alterações"):
                    atualizar_usuario(nome_usuario, email, senha, tipo_usuario, id_usuario_atualizar)
                    st.success("Usuário atualizado com sucesso!")
        else:
            st.error("Usuário não encontrado.")

def atualizar_usuario(nome_usuario, EMAIL_USUARIO, senha, tipo_usuario, id_usuario_atualizar):
    conn, cursor = conectar_banco()
    if conn is not None and cursor is not None:
        try:
            query = """
                UPDATE TB_USUARIO
                SET NOME_USUARIO = ?, EMAIL_USUARIO = ?, SENHA = ?, TIPO_USUARIO = ?
                WHERE ID_USUARIO = ?;
            """
            params = (nome_usuario, EMAIL_USUARIO, senha, tipo_usuario, id_usuario_atualizar)
            cursor.execute(query, params)
            conn.commit()  # Não esqueça de confirmar a transação
            st.success("Usuário atualizado com sucesso!")
        except Exception as e:
            st.error(f"Ocorreu um erro ao atualizar o usuário: {e}")
        finally:
            desconectar_banco(conn, cursor)

def excluir_usuario(id_usuario_excluir):
    conn, cursor = conectar_banco()
    if conn is not None and cursor is not None:  # Verifica se a conexão e o cursor foram criados
        cursor.execute("DELETE FROM TB_USUARIO WHERE ID_USUARIO = ?", (id_usuario_excluir,))
        conn.commit()
        desconectar_banco(conn, cursor)

def main():
    st.sidebar.caption("Robust - Sistema de Gestão")
    
    menu = st.sidebar.selectbox("Menu", 
                                 ["Listar Usuários", 
                                  "Criar Usuário", 
                                  "Atualizar Usuário", 
                                  "Excluir Usuário"])

    st.title("Manutenção de Usuários")
    criar_tabela_usuario()

    if menu == "Listar Usuários":
        listar_usuarios()

    elif menu == "Criar Usuário":
        criar_usuario_form()

    elif menu == "Atualizar Usuário":
        listar_usuarios()
        id_usuario_atualizar = st.text_input("Digite o ID do usuário a ser atualizado")
        if id_usuario_atualizar:
            atualizar_usuario_form(int(id_usuario_atualizar))

    elif menu == "Excluir Usuário":
        id_usuario_excluir = st.text_input("Digite o ID do usuário a ser excluído")
        if id_usuario_excluir:
            excluir_usuario(int(id_usuario_excluir))
            st.success(f"Usuário com ID {id_usuario_excluir} excluído com sucesso!")

if __name__ == "__main__":
    main()