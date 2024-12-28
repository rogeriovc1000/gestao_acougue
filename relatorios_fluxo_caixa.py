import streamlit as st
import sqlite3
import pandas as pd
from reportlab.lib.units import inch
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
import os, config
from config import rodape, main
import Calculos 
from datetime import datetime

# Defina o caminho e o nome do arquivo do banco de dados
db_file = os.path.join(os.getcwd(), 'bancodedados/acougue_db.db')

def conectar_banco():
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except sqlite3.Error as e:
        st.error(f"Erro ao conectar ao banco de dados: {e}")
        return None

def listar_fluxo_caixa():
    conn = conectar_banco()
    if conn:
        query = """
        SELECT 
            ID_FLUXO_DE_CAIXA, 
            DATA_FLUXO_DE_CAIXA, 
            ID_CATEGORIA,
            DESCRICAO_FLUXO_DE_CAIXA, 
            ID_FORNECEDOR,
            VALOR_FLUXO_DE_CAIXA
        FROM TB_FLUXO_DE_CAIXA
        """
        contas = pd.read_sql_query(query, conn)
        conn.close()
        return contas.to_dict(orient='records')  # Retorna uma lista de dicionários
    return []

def listar_fluxo_caixa_por_categoria(categoria_id):
    conn = conectar_banco()
    if conn:
        query = """
        SELECT 
            f.ID_FLUXO_DE_CAIXA, 
            f.DATA_FLUXO_DE_CAIXA, 
            f.VALOR_FLUXO_DE_CAIXA, 
            f.DESCRICAO_FLUXO_DE_CAIXA,
            f.ID_CATEGORIA,
            p.NOME_FORNECEDOR  
        FROM TB_FLUXO_DE_CAIXA f
        LEFT JOIN TB_FORNECEDOR p ON f.ID_FORNECEDOR = p.ID_FORNECEDOR
        WHERE f.ID_CATEGORIA = ?
        """
        contas = pd.read_sql_query(query, conn, params=(categoria_id,))
        conn.close()
        return contas.to_dict(orient='records')
    return []

def listar_fluxo_caixa_por_data(data_inicial, data_final):
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
        WHERE DATA_FLUXO_DE_CAIXA BETWEEN ? AND ?
        """
        contas = pd.read_sql_query(query, conn, params=(data_inicial, data_final))
        conn.close()
        return contas.to_dict(orient='records')
    return []

def listar_totais_por_categoria():
    conn = conectar_banco()
    if conn:
        query = """
        SELECT 
            c.NOME_CATEGORIA,
            SUM(f.VALOR_FLUXO_DE_CAIXA) AS TOTAL
        FROM TB_FLUXO_DE_CAIXA f
        JOIN TB_CATEGORIAS c ON f.ID_CATEGORIA = c.ID_CATEGORIA
        GROUP BY c.NOME_CATEGORIA
        """
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df.to_dict(orient='records')  # Retorna uma lista de dicionários
    return []

def obter_nome_categoria(categoria_id):
    conn = conectar_banco()
    if conn:
        query = "SELECT NOME_CATEGORIA FROM TB_CATEGORIAS WHERE ID_CATEGORIA = ?"
        contas = pd.read_sql_query(query, conn, params=(categoria_id,))
        conn.close()
        return contas['NOME_CATEGORIA'].iloc[0] if not contas.empty else "Categoria Desconhecida"
    return "Categoria Desconhecida"

def gerar_relatorio_pdf_total(contas, filename, titulo, nome_empresa):
    # Obter os totais por categoria
    totais = listar_fluxo_caixa()  # Chamada para obter os totais

    styles = getSampleStyleSheet()
    doc = SimpleDocTemplate(filename, pagesize=letter)
    story = []

    # Cabeçalho
    nome_empresa = config.NOME_EMPRESA
    story.append(Paragraph(titulo, styles['Title']))
    story.append(Paragraph(f"Emitido em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}", styles['Normal']))
    story.append(Paragraph(f"Nome da Empresa: {nome_empresa}", styles['Normal']))
    story.append(Paragraph(" ", styles['Normal']))  # Espaço em branco

    # Calcular totais usando a função do módulo
    saldo = 0
    try:
        total_entrada, total_saida, saldo = Calculos.calcular_totais(contas)  # Chama a função corretamente
    except ValueError as e:
        print(f"Erro ao calcular totais: {e}")
        return  # Retorna se houver erro

    # Agrupar contas por categoria
    contas_por_categoria = {}
    for conta in contas:
        categoria_id = conta['ID_CATEGORIA']
        if categoria_id not in contas_por_categoria:
            contas_por_categoria[categoria_id] = []
        contas_por_categoria[categoria_id].append(conta)

    # Criar tabela detalhada por categoria
    for categoria_id, contas_categoria in contas_por_categoria.items():
        nome_categoria = obter_nome_categoria(categoria_id)
        story.append(Paragraph(f"Categoria: {nome_categoria}", styles['Heading2']))

        # Tabela de dados para a categoria
        data = [["ID", "Data", "Descrição", "Valor"]]  # Cabeçalho da tabela
        total_categoria = 0

        for conta in contas_categoria:
            valor_FLUXO_DE_CAIXA = pd.to_numeric(conta['VALOR_FLUXO_DE_CAIXA'], errors='coerce')
            if pd.isna(valor_FLUXO_DE_CAIXA):
                valor_FLUXO_DE_CAIXA = 0
            
            total_categoria += valor_FLUXO_DE_CAIXA

            data.append([
                conta['ID_FLUXO_DE_CAIXA'],
                conta['DATA_FLUXO_DE_CAIXA'],
                conta['DESCRICAO_FLUXO_DE_CAIXA'],
                Calculos.formatar_moeda(valor_FLUXO_DE_CAIXA)  # Formatação do valor
            ])

        # Adiciona a linha de total da categoria
        data.append(["", "", "Total da Categoria:", Calculos.formatar_moeda(total_categoria)])

        # Criar tabela detalhada por categoria
        tabela_categoria = Table(data)

        # Definindo o estilo da tabela
        tabela_categoria.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),  # Cabeçalho
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),  # Linhas de dados
            ('GRID', (0, 0), (-1, -1), 1, colors.black),  # Grade

        ]))

        # Adiciona a tabela ao story
        story.append(tabela_categoria)
        
    # Adiciona os totais de entrada, saída e o saldo de caixa ao relatório
    story.append(Paragraph("Totais Gerais:", styles['Heading2']))
    totals_data = [
        ["Descrição", "Valor"],
        ["Total Entrada", Calculos.formatar_moeda(abs(int(total_entrada)))],
        
        ["Total Saída", Calculos.formatar_moeda(abs(total_saida))],
        
        ["Saldo", Calculos.formatar_moeda(int(saldo))]
    ]

    totals_table = Table(totals_data)
    totals_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    story.append(totals_table)

    # Gerar o PDF
    doc.build(story)

def gerar_relatorio_pdf_categoria(contas, filename, titulo, nome_empresa, categoria_id):
    styles = getSampleStyleSheet()
    doc = SimpleDocTemplate(filename, pagesize=letter)
    story = []

    # Cabeçalho
    nome_empresa = config.NOME_EMPRESA
    story.append(Paragraph(titulo, styles['Title']))
    story.append(Paragraph(f"Emitido em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}", styles['Normal']))
    story.append(Paragraph(f"Nome da Empresa: {nome_empresa}", styles['Normal']))
    story.append(Paragraph(" ", styles['Normal']))  # Espaço em branco

    # Tabela de dados
    data = [["ID", "Data", "Descrição", "Valor"]]  # Alterado para colocar Valor como última coluna
    total_categoria = 0

    for conta in contas:
        valor_FLUXO_DE_CAIXA = pd.to_numeric(conta['VALOR_FLUXO_DE_CAIXA'], errors='coerce')
        if pd.isna(valor_FLUXO_DE_CAIXA):
            valor_FLUXO_DE_CAIXA = 0
        
        total_categoria += valor_FLUXO_DE_CAIXA

        data.append([
            conta['ID_FLUXO_DE_CAIXA'],
            conta['DATA_FLUXO_DE_CAIXA'],
            conta['DESCRICAO_FLUXO_DE_CAIXA'],
            Calculos.formatar_moeda(valor_FLUXO_DE_CAIXA)  # Formatação do valor
        ])

    # Adiciona a linha de total da categoria
    data.append(["", "", "Total da Categoria:", Calculos.formatar_moeda(total_categoria)])

    tabela_categoria = Table(data)
    tabela_categoria.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTNAME', (2, -1), 'Helvetica-Bold'),  # Negrito para a linha de total
        ('BACKGROUND', (0, -1), (-1, -1), colors.lightgrey),  # Fundo cinza para a linha de total
    ]))
    story.append(tabela_categoria)

    # Gerar o PDF
    doc.build(story)
    
def listar_categorias():
    conn = conectar_banco()
    if conn:
        query = "SELECT ID_CATEGORIA, NOME_CATEGORIA FROM TB_CATEGORIAS"
        categorias = pd.read_sql_query(query, conn)
        conn.close()
        return categorias
    return pd.DataFrame(columns=["ID_CATEGORIA", "NOME_CATEGORIA"])
    
def main():
    rodape()
    st.title("Relatórios de Fluxo de Caixa")

    option = st.selectbox("Escolha o Tipo de relatório", ["Fluxo de Caixa Total", "Fluxo de Caixa por Categoria", "Fluxo de Caixa por Data"])

    contas = []  # Inicializa a variável contas
    titulo = ""  # Inicializa a variável titulo

    if option == "Fluxo de Caixa Total":
        contas = listar_fluxo_caixa()
        
        titulo = "Relatório de Fluxo de Caixa Total"

    elif option == "Fluxo de Caixa por Categoria":
        # Listar categorias e preencher o selectbox
        categorias = listar_categorias()

        if not categorias.empty:
            categoria_options = categorias.set_index('ID_CATEGORIA')['NOME_CATEGORIA'].to_dict()
            categoria_id = st.selectbox("Escolha a Categoria", options=list(categoria_options.keys()), format_func=lambda x: categoria_options[x])
            
            if categoria_id:  # Verifica se categoria_id foi selecionado
                contas = listar_fluxo_caixa_por_categoria(categoria_id)
                titulo = f"Relatório de Fluxo de Caixa para a Categoria ID: {categoria_id}"
            else:
                st.warning("Nenhuma categoria selecionada.")
        else:
            st.warning("Nenhuma categoria encontrada.")
    
    elif option == "Fluxo de Caixa por Data":
        data_inicial = st.date_input("Data Inicial")
        data_final = st.date_input("Data Final")
        
        if data_inicial and data_final:
            contas = listar_fluxo_caixa_por_data(data_inicial, data_final)
            titulo = f"Relatório de Fluxo de Caixa entre {data_inicial} e {data_final}"
        else:
            st.warning("Por favor, selecione ambas as datas.")

   # Botão para gerar o relatório PDF
    if st.button("Gerar Relatório PDF"):
        if contas:
            nome_empresa = "Acougue Gourmet"  # Defina o nome da empresa aqui
            filename = "relatorio_fluxo_caixa.pdf"
            gerar_relatorio_pdf_total(contas, filename, titulo, nome_empresa)  # Chamada corrigida
            
            with open(filename, "rb") as f:
                st.download_button("Baixar Relatório", f, file_name=filename)
        else:
            st.warning("Nenhum FLUXO_DE_CAIXA encontrado para o relatório selecionado.")

if __name__ == "__main__":
    main()