import streamlit as st
import sqlite3
import pandas as pd

# Função para conectar ao banco de dados
def get_db_connection():
    conn = sqlite3.connect('bancodedados/acougue_db.db')
    return conn

# Função para carregar categorias em um DataFrame
def load_categories():
    conn = get_db_connection()
    df = pd.read_sql_query("SELECT ID_CATEGORIA, NOME_CATEGORIA FROM TB_CATEGORIAS", conn)  # Modifique aqui
    conn.close()
    return df

# Título da aplicação
st.title("Gerenciamento de Categorias")

# Instruções para o usuário
st.write("Adicione, edite ou exclua categorias do seu banco de dados.")

def main():
    # Formulário para adicionar nova categoria
    new_category = st.text_input("Digite o nome da nova categoria:")

    if st.button("Adicionar Categoria"):
        if new_category:
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Inserir nova categoria na tabela
            cursor.execute("INSERT INTO TB_CATEGORIAS (NOME_CATEGORIA) VALUES (?)", (new_category,))
            conn.commit()
            conn.close()
            
            st.success(f"Categoria '{new_category}' adicionada com sucesso!")
            st.rerun()  # Recarregar a página para mostrar a nova categoria
        else:
            st.error("Por favor, insira um nome para a categoria.")

    # Exibir categorias existentes
    st.subheader("Categorias Existentes")

    # Carregar categorias em um DataFrame
    df_categorias = load_categories()

    # Exibir DataFrame com opção de edição
    if not df_categorias.empty:
        df_categorias.set_index('ID_CATEGORIA', inplace=True)  # Modifique aqui
        edited_df = st.data_editor(df_categorias, num_rows="dynamic", key="data_editor")

        # Botão para salvar alterações
        if st.button("Salvar Alterações"):
            conn = get_db_connection()
            cursor = conn.cursor()
            
            # Atualizar as categorias no banco de dados
            for index, row in edited_df.iterrows():
                cursor.execute("UPDATE TB_CATEGORIAS SET NOME_CATEGORIA = ? WHERE ID_CATEGORIA = ?", (row['NOME_CATEGORIA'], index))  # Modifique aqui
            
            conn.commit()
            conn.close()
            
            st.success("Alterações salvas com sucesso!")
            st.rerun()  # Recarregar a página para mostrar as atualizações

        # Seletor para excluir categorias
        selected_rows = st.multiselect("Selecione as categorias a serem excluídas:", df_categorias.index)

        # Botão para excluir categorias
        if st.button("Excluir Categorias Selecionadas"):
            if selected_rows:
                conn = get_db_connection()
                cursor = conn.cursor()
                
                # Excluir as categorias selecionadas
                for ID_CATEGORIA in selected_rows:
                    cursor.execute("DELETE FROM TB_CATEGORIAS WHERE ID_CATEGORIA = ?", (ID_CATEGORIA,))  # Modifique aqui
                
                conn.commit()
                conn.close()
                st.success("Categorias excluídas com sucesso!")
                st.rerun()  # Recarregar a página para mostrar as atualizações
            else:
                st.error("Por favor, selecione pelo menos uma categoria para excluir.")
    else:
        st.write("Nenhuma categoria encontrada.")

if __name__ == "__main__":  # Correção aqui
    main()