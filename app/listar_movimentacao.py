from datetime import datetime
import streamlit as st
import sqlite3
import os
import pandas as pd
import locale

# Configuração da página
st.header("Movimentações do Caixa")

# Conecta ao banco de dados
db_file = os.path.join(os.getcwd(), 'bancodedados', 'acougue_db.db')

def conectar_banco():
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except sqlite3.Error as e:
        st.error(f"Erro ao conectar ao banco de dados: {e}")
        return None

# Função para recuperar as descrições
def get_descriptions():
    conn = conectar_banco()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT DESCRICAO_FLUXO_DE_CAIXA FROM TB_FLUXO_DE_CAIXA")
            descriptions = [row[0] for row in cursor.fetchall()]
            return descriptions
        except sqlite3.Error as e:
            st.error(f"Erro ao recuperar descrições: {e}")
            return []
        finally:
            cursor.close()
            conn.close()
    return []

def listar_fornecedores():
    conn = conectar_banco()
    if conn:
        query = "SELECT ID_FORNECEDOR, NOME_FORNECEDOR FROM TB_FORNECEDOR"
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df.to_dict(orient='records')  # Retorna uma lista de dicionários
    return []

def listar_movimentos_por_categoria(categoria):
    conn = conectar_banco()
    if conn:
        query = """
        SELECT 
            ID_FLUXO_DE_CAIXA, 
            DATA_FLUXO_DE_CAIXA, 
            VALOR_FLUXO_DE_CAIXA, 
            DESCRICAO_FLUXO_DE_CAIXA, 
            ID_CATEGORIA
        FROM TB_FLUXO_DE_CAIXA
        WHERE ID_CATEGORIA = (SELECT ID_CATEGORIA FROM TB_CATEGORIAS WHERE NOME_CATEGORIA = ?)
        """
        df = pd.read_sql_query(query, conn, params=(categoria,))
        conn.close()
        return df.to_dict(orient='records')  # Retorna uma lista de dicionários
    return []

def exibir_movimentacoes():
    try:
        conn = conectar_banco()
        cursor = conn.cursor()
        cursor.execute("""
        SELECT 
            f.ID_FLUXO_DE_CAIXA AS ID,
            f.DATA_FLUXO_DE_CAIXA AS DATA,
            c.NOME_CATEGORIA AS CATEGORIA,
            p.NOME_FORNECEDOR AS FORNECEDOR,
            f.VALOR_FLUXO_DE_CAIXA AS VALOR,
            f.DESCRICAO_FLUXO_DE_CAIXA AS DESCRICAO
        FROM 
            TB_FLUXO_DE_CAIXA AS f
        JOIN 
            TB_CATEGORIAS AS c ON f.ID_CATEGORIA = c.ID_CATEGORIA
        LEFT JOIN 
            TB_FORNECEDOR AS p ON f.ID_FORNECEDOR = p.ID_FORNECEDOR;
        """)
        
        # Construa o DataFrame a partir da consulta
        movements = cursor.fetchall()
        column_names = [desc[0] for desc in cursor.description]
        df = pd.DataFrame(movements, columns=column_names)

        # Se o DataFrame estiver vazio, inicialize um DataFrame vazio com as colunas
        if df.empty:
            df = pd.DataFrame(columns=column_names)
            st.warning("Não há dados disponíveis para exibir.")

        # Converte a coluna VALOR para float, se necessário
        df['VALOR'] = pd.to_numeric(df['VALOR'], errors='coerce').fillna(0)

        # Exibe o DataFrame editável sem o índice
        edited_df = st.data_editor(df, use_container_width=True, key="editable_dataframe")

        # Exibe o total das movimentações
        try:
            locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
        except locale.Error:
            st.error("Configuração de localidade não suportada. Verifique se a localidade 'pt_BR.UTF-8' está instalada no sistema.")
            return

        total_entradas = df[df['CATEGORIA'].isin(["Entradas e Receitas"])]['VALOR'].sum()
        total_saidas = df[~df['CATEGORIA'].isin(["Entradas e Receitas"])]["VALOR"].sum()
        diferenca = total_entradas - total_saidas  

        st.write(f"**Total de Entradas:** {locale.currency(abs(total_entradas), grouping=True)}")
        st.write(f"**Total de Saídas:** {locale.currency(abs(total_saidas), grouping=True)}")
        st.write(f"**Diferença (Entradas - Saídas):** {locale.currency(diferenca, grouping=True)}")
       
        if st.button("Salvar Alterações"):
            df['ID'] = [row[0] for row in movements]  # Armazena os IDs em uma nova coluna
            df = df.drop(columns=['ID'])  # Remove a coluna ID_FLUXO_DE_CAIXA

            for index, row in edited_df.iterrows():
                id_fluxo_de_caixa = movements[index][0]  # Supondo que o ID seja a primeira coluna
                cursor.execute("SELECT COUNT(*) FROM TB_CATEGORIAS WHERE NOME_CATEGORIA = ?", (row['CATEGORIA'],))
                categoria_existente = cursor.fetchone()[0]

                if categoria_existente > 0:  # A categoria existe
                    # Verifica se o fornecedor é nulo e ajusta a inserção
                    id_fornecedor = (cursor.execute("SELECT ID_FORNECEDOR FROM TB_FORNECEDOR WHERE NOME_FORNECEDOR = ?", (row['FORNECEDOR'],)).fetchone() or [None])[0]
                    
                    # Se o fornecedor for nulo, use None
                    if id_fornecedor is None:
                        id_fornecedor = None
                    
                    cursor.execute("""
                        UPDATE TB_FLUXO_DE_CAIXA
                        SET VALOR_FLUXO_DE_CAIXA = ?, 
                            DATA_FLUXO_DE_CAIXA = ?, 
                            ID_CATEGORIA = (SELECT ID_CATEGORIA FROM TB_CATEGORIAS WHERE NOME_CATEGORIA = ?), 
                            DESCRICAO_FLUXO_DE_CAIXA = ?, 
                            ID_FORNECEDOR = ?
                        WHERE ID_FLUXO_DE_CAIXA = ?
                    """, (row['VALOR'], row['DATA'], row['CATEGORIA'], row['DESCRICAO'], id_fornecedor, id_fluxo_de_caixa))
                else:   
                    st.warning(f"A categoria '{row['CATEGORIA']}' não existe no banco de dados. As alterações para este registro não serão salvas.")
            
            conn.commit()  # Mova o commit para fora do loop
            st.success("Alterações salvas com sucesso!")
            
    except Exception as e:
        st.error(f"Ocorreu um erro: {e}")
    finally:
        cursor.close()
        conn.close()

def adicionar_registro():
    st.subheader("Adicionar Novo Registro")
    try:
        conn = conectar_banco()
        cursor = conn.cursor()

        # Carregar categorias do banco de dados
        cursor.execute("SELECT NOME_CATEGORIA FROM TB_CATEGORIAS")
        categorias = [row[0] for row in cursor.fetchall()]

        # Carregar fornecedores do banco de dados
        cursor.execute("SELECT ID_FORNECEDOR, NOME_FORNECEDOR FROM TB_FORNECEDOR")
        fornecedores = cursor.fetchall()
        fornecedores_dict = {nome: id for id, nome in fornecedores}  # Dicionário para mapear nome para ID
        
        # Recupera as opções de descrição
        descricao_options = get_descriptions()
        
        # Cria o formulário de entrada
        new_data = {
            'DATA': st.date_input("Data"),
            'CATEGORIA': st.selectbox("CATEGORIA", options=categorias, key="CATEGORIA_movimentacao"),
            'VALOR': st.number_input("Valor", min_value=0.0),
            'DESCRICAO_EXISTENTE': st.selectbox("Descrição Existente", options=descricao_options, key="descricao_existente"),
            'NOVA_DESCRICAO': st.text_input("Nova Descrição", key="nova_descricao")
        }

        # Verifica se o CATEGORIA selecionado é "Fornecedor" e atualiza o estado
        if new_data['CATEGORIA'] == "Fornecedores":
            st.session_state.fornecedor_enabled = True
        else:
            st.session_state.fornecedor_enabled = False

        # Atualiza o campo "Fornecedor com base no estado
        fornecedor_disabled = not st.session_state.fornecedor_enabled

        selected_fornecedor = st.selectbox("Fornecedor", options=list(fornecedores_dict.keys()), disabled=fornecedor_disabled, key="fornecedor")

        if st.button("Adicionar Registro"):
            descricao_final = new_data['NOVA_DESCRICAO'] if new_data['NOVA_DESCRICAO'] else new_data['DESCRICAO_EXISTENTE']
            id_fornecedor = fornecedores_dict.get(selected_fornecedor, None)  # Permite que o fornecedor seja nulo
            cursor.execute("""
                INSERT INTO TB_FLUXO_DE_CAIXA 
                (DATA_FLUXO_DE_CAIXA, ID_CATEGORIA, ID_FORNECEDOR, VALOR_FLUXO_DE_CAIXA, DESCRICAO_FLUXO_DE_CAIXA)
                VALUES (?, (SELECT ID_CATEGORIA FROM TB_CATEGORIAS WHERE NOME_CATEGORIA = ?), ?, ?, ?)
            """, (new_data['DATA'], new_data['CATEGORIA'], id_fornecedor, new_data['VALOR'], descricao_final))  
            conn.commit()
            st.success("Registro adicionado com sucesso!")

    except Exception as e:
        st.error(f"Ocorreu um erro: {e}")
    finally:
        cursor.close()
        conn.close()

def excluir_registro():
    st.subheader("Excluir Registro")
    id_to_delete = st.text_input("Digite o ID para excluir", key="id_excluir_input")

    if st.button("Buscar Registro"):
        try:
            conn = conectar_banco()
            cursor = conn.cursor()

            if id_to_delete.isdigit():
                cursor.execute("SELECT * FROM TB_FLUXO_DE_CAIXA WHERE ID_FLUXO_DE_CAIXA = ?", (id_to_delete,))
                registro = cursor.fetchone()

                if registro:
                    st.markdown(f"<span style='color: white;'>ID:</span> <span style='color: red;'>{registro[0]}</span>  "
                                f"<span style='color: white;'>Descrição:</span> <span style='color: red;'>{registro[1]}</span>  "
                                f"<span style='color: white;'>Valor:</span> <span style='color: red;'>{registro[2]}</span>  "
                                f"<span style='color: white;'>Data:</span> <span style='color: red;'>{registro[3]}</span>  "
                                f"<span style='color: white;'>Fornecedor:</span> <span style='color: red;'>{registro[4]}</span>",
                                unsafe_allow_html=True)

                    cursor.execute("DELETE FROM TB_FLUXO_DE_CAIXA WHERE ID_FLUXO_DE_CAIXA = ?", (id_to_delete,))
                    conn.commit()
                    st.success("Registro excluído com sucesso!")
                else:
                    st.error("Registro não encontrado.")
            else:
                st.error("Por favor, insira um ID válido.")
        except sqlite3.Error as e:
            st.error(f"Ocorreu um erro ao acessar o banco de dados: {e}")
        except Exception as e:
            st.error(f"Ocorreu um erro inesperado: {e}")
        finally:
            if cursor:
                cursor.close()
            if conn:
                conn.close()

# Função principal
def main():
    st.sidebar.title("Menu")
    menu = st.sidebar.radio("Escolha uma opção:", ("Visualizar","Incluir", "Deletar",))

    if menu == "Incluir":
        adicionar_registro()
    elif menu == "Deletar":
        excluir_registro()
        exibir_movimentacoes()
    elif menu == "Visualizar":
        exibir_movimentacoes()

if __name__ == "__main__":
    main()