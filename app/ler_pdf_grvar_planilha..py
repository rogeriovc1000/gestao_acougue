import pdfplumber
import pandas as pd

def ler_pdf_para_xls(pdf_path, xls_path):
    # Lista para armazenar os DataFrames
    dados = []

    # Lê o PDF
    with pdfplumber.open(pdf_path) as pdf:
        for pagina in pdf.pages:
            # Extrai tabelas da página
            tabelas = pagina.extract_tables()
            for tabela in tabelas:
                # Converte a tabela em um DataFrame do pandas
                df_tabela = pd.DataFrame(tabela[1:], columns=tabela[0])
                dados.append(df_tabela)

    # Concatena todos os DataFrames em um único DataFrame
    if dados:
        df_final = pd.concat(dados, ignore_index=True)
        # Grava o DataFrame em um arquivo Excel
        df_final.to_excel(xls_path, index=False)
        print(f"Arquivo Excel gerado: {xls_path}")
    else:
        print("Nenhuma tabela encontrada no PDF.")

# Exemplo de uso
print("Gerando arquivo...")
pdf_path = 'relatorio_fluxo_caixa (3).pdf'  # Substitua pelo caminho do seu PDF
xls_path = 'relatorio_fluxo_caixa.xlsx'  # Substitua pelo caminho onde deseja salvar o XLS
ler_pdf_para_xls(pdf_path, xls_path)