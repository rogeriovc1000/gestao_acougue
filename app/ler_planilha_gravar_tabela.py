import pandas as pd
import sqlite3
import streamlit as st

# Caminho para o arquivo Excel
excel_path = "relatorio_fluxo_caixa.xlsx"

# Lê o arquivo Excel
df = pd.read_excel(excel_path)
st.write(df)

# Conecta ao banco de dados SQLite
conn = sqlite3.connect('bancodedados/acougue_db.db')  # Ajuste o caminho conforme necessário
cursor = conn.cursor()

def get_id_categoria(nome_categoria, cursor):
    cursor.execute("SELECT ID_CATEGORIA FROM TB_CATEGORIAS WHERE NOME_CATEGORIA = ?", (nome_categoria,))
    resultado = cursor.fetchone()
    if resultado is None:
        print(f"Categoria '{nome_categoria}' não encontrada.")
        return -1  # Retorna um valor que indica erro
    return resultado[0]

# Insere os dados na tabela TB_FLUXO_DE_CAIXA
for index, row in df.iterrows():
    # Obtém o ID da categoria
    id_categoria = get_id_categoria(row['Nome Categoria'], cursor)

    cursor.execute('''
        INSERT INTO TB_FLUXO_DE_CAIXA (DESCRICAO_FLUXO_DE_CAIXA, VALOR_FLUXO_DE_CAIXA, DATA_FLUXO_DE_CAIXA, ID_FORNECEDOR, ID_CATEGORIA)
        VALUES (?, ?, ?, ?, ?)
    ''', (row['Descrição'], row['Valor'], row['Data'], row.get('ID_FORNECEDOR', None), id_categoria))

# Commit as mudanças
conn.commit()

# Fecha a conexão
conn.close()

print("Dados inseridos com sucesso na tabela TB_FLUXO_DE_CAIXA.")