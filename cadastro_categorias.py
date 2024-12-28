import streamlit as st
import sqlite3
import os
import pandas as pd

# Configuração do banco de dados
db_file = os.path.join(os.getcwd(), 'bancodedados', 'acougue_db.db')

def conectar_banco():
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except sqlite3.Error as e:
        st.error(f"Erro ao conectar ao banco de dados: {e}")
        return None

# Função para criar uma nova categoria
def criar_categoria(nome_categoria):
    if not nome_categoria:
        st.error("O nome da categoria não pode ser vazio.")
        return

    conn = conectar_banco()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO TB_CATEGORIAS (NOME_CATEGORIA) VALUES (?)", (nome_categoria,))
            conn.commit()
            st.success("Categoria adicionada com sucesso!")
        except sqlite3.Error as e:
            st.error(f"Erro ao adicionar categoria: {e}")
        finally:
            cursor.close()
            conn.close()

# Função para listar todas as categorias
def listar_categorias():
    conn = conectar_banco()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM TB_CATEGORIAS")
            categorias = cursor.fetchall()
            return categorias
        except sqlite3.Error as e:
            st.error(f"Erro ao listar categorias: {e}")
            return []
        finally:
            cursor.close()
            conn.close()
    return []

# Função para atualizar uma categoria
def atualizar_categoria(id_categoria, novo_nome):
    if not novo_nome:
        st.error("O novo nome da categoria não pode ser vazio.")
        return

    conn = conectar_banco()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("UPDATE TB_CATEGORIAS SET NOME_CATEGORIA = ? WHERE ID_CATEGORIA = ?", (novo_nome, id_categoria))
            conn.commit()
            st.success("Categoria atualizada com sucesso!")
        except sqlite3.Error as e:
            st.error(f"Erro ao atualizar categoria: {e}")
        finally:
            cursor.close()
            conn.close()

# Função para excluir uma categoria
def excluir_categoria(id_categoria):
    conn = conectar_banco()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM TB_CATEGORIAS WHERE ID_CATEGORIA = ?", (id_categoria,))
            conn.commit()
            st.success("Categoria excluída com sucesso!")
        except sqlite3.Error as e:
            st.error(f"Erro ao excluir categoria: {e}")
        finally:
            cursor.close()
            conn.close()

# Interface do Streamlit
def main():
    st.title("Gerenciamento de Categorias")

    # Formulário para adicionar nova categoria
    st.subheader("Adicionar Nova Categoria")
    nova_categoria = st.text_input("Nome da Categoria")
    if st.button("Adicionar"):
        criar_categoria(nova_categoria)

    # Listar categorias existentes em um DataFrame
    st.subheader("Categorias Existentes")
    categorias = listar_categorias()
    if categorias:
        # Cria um DataFrame a partir das categorias
        df_categorias = pd.DataFrame(categorias, columns=["ID", "Nome"])
        
        # Exibe o DataFrame com a opção de edição
        edited_df = st.data_editor(df_categorias, key="categorias_editor", num_rows="dynamic")

        # Atualiza as categorias no banco de dados
        if st.button("Salvar Alterações"):
            for index, row in edited_df.iterrows():
                if row["Nome"] != df_categorias.at[index, "Nome"]:  # Verifica se houve alteração
                    atualizar_categoria(row["ID"], row["Nome"])
            st.success("Alterações salvas com sucesso!")

    else:
        st.write("Nenhuma categoria encontrada.")

    # Formulário para excluir uma categoria
    st.subheader("Excluir Categoria")
    id_categoria_excluir = st.number_input("Digite o ID da Categoria a ser excluída", min_value=1, step=1)
    if st.button("Excluir"):
        excluir_categoria(id_categoria_excluir)

if __name__ == "__main__":
    main()