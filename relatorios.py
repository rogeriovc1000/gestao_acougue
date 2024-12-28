import streamlit as st
import sqlite3, os
import pandas as pd
from io import BytesIO
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, PageTemplate, Frame
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet

def conectar_banco():
    # Defina o caminho e o nome do arquivo do banco de dados
    db_file = os.path.join(os.getcwd(), 'bancodedados/acougue_db.db')
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except sqlite3.Error as e:
        st.error(f"Erro ao conectar ao banco de dados: {e}")
        return None

def listar_contas_vencidas():
    conn = conectar_banco()
    if conn:
        query = """
        SELECT 
            ID_CONTA_A_PAGAR, 
            DATA_VENCIMENTO, 
            VALOR_CONTA, 
            VALOR_PAGO, 
            STATUS_CONTA,
            ID_FORNECEDOR,
            DATA_PAGAMENTO
        FROM TB_CONTAS_A_PAGAR
        WHERE DATA_VENCIMENTO <= ? AND STATUS_CONTA = "Pendente"
        """
        today = datetime.now().date()
        df = pd.read_sql_query(query, conn, params=(today,))
        conn.close()
        return df.to_dict(orient='records')  # Retorna uma lista de dicionários
    return []

def listar_contas_pagas():
    conn = conectar_banco()
    if conn:
        query = """
        SELECT 
            ID_CONTA_A_PAGAR, 
            DATA_VENCIMENTO, 
            VALOR_CONTA, 
            VALOR_PAGO, 
            DATA_PAGAMENTO,
            STATUS_CONTA,
            ID_FORNECEDOR
        FROM TB_CONTAS_A_PAGAR
        WHERE STATUS_CONTA = "Pago"
        """
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df.to_dict(orient='records')  # Retorna uma lista de dicionários
    return []

def listar_contas_a_vencer():
    conn = conectar_banco()
    if conn:
        query = """
        SELECT 
            ID_CONTA_A_PAGAR, 
            DATA_VENCIMENTO, 
            VALOR_CONTA, 
            VALOR_PAGO, 
            STATUS_CONTA,
            ID_FORNECEDOR,
            DATA_PAGAMENTO
        FROM TB_CONTAS_A_PAGAR
        WHERE DATA_VENCIMENTO > ? AND STATUS_CONTA = "Pendente"
        """
        today = datetime.now().date()
        df = pd.read_sql_query(query, conn, params=(today,))
        conn.close()
        return df.to_dict(orient='records')  # Retorna uma lista de dicionários
    return []

def listar_contas_por_fornecedor(fornecedor_id):
    conn = conectar_banco()
    if conn:
        query = """
        SELECT 
            ID_CONTA_A_PAGAR, 
            DATA_VENCIMENTO, 
            VALOR_CONTA, 
            VALOR_PAGO, 
            STATUS_CONTA,
            ID_FORNECEDOR,
            DATA_PAGAMENTO
        FROM TB_CONTAS_A_PAGAR
        WHERE ID_FORNECEDOR = ?
        """
        df = pd.read_sql_query(query, conn, params=(fornecedor_id,))
        conn.close()
        return df.to_dict(orient='records')
    return []

def listar_contas_por_status(status):
    conn = conectar_banco()
    if conn:
        query = """
        SELECT 
            ID_CONTA_A_PAGAR, 
            DATA_VENCIMENTO, 
            DATA_PAGAMENTO,
            VALOR_CONTA, 
            VALOR_PAGO, 
            STATUS_CONTA,
            ID_FORNECEDOR
        FROM TB_CONTAS_A_PAGAR
        WHERE STATUS_CONTA = ?
        """
        df = pd.read_sql_query(query, conn, params=(status,))
        conn.close()
        return df.to_dict(orient='records')
    return []

def listar_contas_por_data(data_inicial, data_final):
    conn = conectar_banco()
    if conn:
        query = """
        SELECT 
            ID_CONTA_A_PAGAR, 
            DATA_VENCIMENTO, 
            VALOR_CONTA, 
            VALOR_PAGO, 
            STATUS_CONTA,
            ID_FORNECEDOR,
            DATA_PAGAMENTO
        FROM TB_CONTAS_A_PAGAR
        WHERE DATA_VENCIMENTO BETWEEN ? AND ?
        """
        df = pd.read_sql_query(query, conn, params=(data_inicial, data_final))
        conn.close()
        return df.to_dict(orient='records')
    return []


def calcular_total(contas):
    """Calcula o total das contas."""
    return sum(conta['VALOR_CONTA'] for conta in contas)

def obter_nome_fornecedor(fornecedor_id):
    conn = conectar_banco()  # Conectar ao banco de dados
    if conn:
        query = "SELECT NOME_FORNECEDOR FROM TB_FORNECEDOR WHERE ID_FORNECEDOR = ?"
        df = pd.read_sql_query(query, conn, params=(fornecedor_id,))
        conn.close()
        if not df.empty:
            return df.iloc[0]['NOME_FORNECEDOR']  # Retorna o nome do fornecedor
    return "Fornecedor não encontrado"

def gerar_relatorio_pdf(contas, filename, titulo, nome_empresa):
    # Diagnóstico: Verifique se os dados estão sendo retornados
    print("Dados retornados:", contas)  # Adicione esta linha para depuração

    if not contas:
        print("Nenhum dado encontrado para gerar o relatório.")
        return  # Retorna se não houver dados

    buffer = BytesIO()  # Cria um buffer em memória para o PDF
    doc = SimpleDocTemplate(buffer, pagesize=letter)  # Define o documento PDF
    
    styles = getSampleStyleSheet()
    story = []

    # Adiciona o título com o nome da empresa
    story.append(Paragraph(f"{titulo} - {nome_empresa}", styles['Title']))
    story.append(Paragraph(" ", styles['Normal']))  # Espaço em branco

    # Cria a tabela de dados
    data = [["ID", "Fornecedor", "Data Vencimento", "Valor Conta", "Valor Pago", "Data Pagamento", "Status"]]  # Cabeçalho da tabela
    total_valor_conta = 0  # Inicializa o total
    total_valor_pago = 0

    for conta in contas:
      # Obter o nome do fornecedor usando o ID_FORNECEDOR da conta
        id_fornecedor = conta.get('ID_FORNECEDOR', 0)  # Obtém o ID do fornecedor
        nome_fornecedor = obter_nome_fornecedor(id_fornecedor)  # Busca o nome do fornecedor
        print(id_fornecedor, nome_fornecedor)
        # Usando os dados retornados pela função
        data.append([
            conta.get('ID_CONTA_A_PAGAR', 'N/A'),        # ID da conta a pagar
            nome_fornecedor,
            conta.get('DATA_VENCIMENTO', 'N/A'),          # Data de vencimento
            f"R$ {conta.get('VALOR_CONTA', 0):,.2f}".replace('.', ',').replace(',', '.', 1),  # Valor da conta formatado
            f"R$ {conta.get('VALOR_PAGO', 0):,.2f}".replace('.', ',').replace(',', '.', 1), # Valor pago formatado
            conta.get('DATA_PAGAMENTO', 'N/A'),  # Data de pagamento
            conta.get('STATUS_CONTA', 'N/A'),  # Status da conta
        ])
        
        # Atualiza o total
        total_valor_conta += conta.get('VALOR_CONTA', 0)
        total_valor_pago += conta.get('VALOR_PAGO', 0)
    
    # Adiciona a linha de totais
    total_row = ["", "", "Totais", 
                 f"R$ {total_valor_conta:,.2f}".replace('.', ',').replace(',', '.', 1), 
                 f"R$ {total_valor_pago:,.2f}".replace('.', ',').replace(',', '.', 1), 
                 "", ""]
    data.append(total_row)  # Adiciona a linha de totais aos dados

    # Cria a tabela e aplica estilo
    table = Table(data)
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),  # Cor de fundo do cabeçalho
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),  # Cor do texto do cabeçalho
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),  # Alinhamento do texto
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),  # Fonte do cabeçalho
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),  # Padding do cabeçalho
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),  # Cor de fundo das linhas
        ('BACKGROUND', (0, len(data)-1), (-1, len(data)-1), colors.lightgrey),  # Fundo cinza claro para a linha de total
        ('TEXTCOLOR', (0, len(data)-1), (-1, len(data)-1), colors.black),  # Texto preto para a linha de total
        ('FONTNAME', (0, len(data)-1), (-1, len(data)-1), 'Helvetica-Bold'),  # Fonte em negrito para a linha de total
        ('FONTSIZE', (0, len(data)-1), (-1, len(data)-1), 12),  # Tamanho da fonte para a linha de total
        ('GRID', (0, 0), (-1, -1), 1, colors.black),  # Grade preta
    ]))

    story.append(table)  # Adiciona a tabela ao relatório

    # Adiciona o rodapé
    story.append(Paragraph(" ", styles['Normal']))  # Espaço em branco

    # Define o template da página
    def add_header_footer(canvas, doc):
        canvas.saveState()
        canvas.setFont('Helvetica', 10)
        # Adiciona o nome do arquivo no rodapé
        canvas.drawString(30, 30, f"sistema de controle administrativo: {filename}")
        canvas.drawString(30, 20, "Controle de Contas")
        canvas.drawString(30, 10, f"Data: {datetime.now().strftime('%d/%m/%Y')} - Página {doc.page}")
        canvas.restoreState()

    # Adiciona o template da página
    doc.addPageTemplates([PageTemplate(id='normal', frames=[Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height, id='normal')], onPage=add_header_footer)])

    # Constrói o PDF
    doc.build(story)

    # Retorna o buffer para que o PDF possa ser salvo ou enviado
    buffer.seek(0)
    return buffer.getvalue()

def main():
    st.header("Relatórios Gerais")

    # Inicializa a variável contas como uma lista vazia
    contas = []
      # Título padrão para o fluxo de caixa
    nome_empresa = "Acougue Gourmet"  # Defina o nome da empresa aqui

    option = st.selectbox("Escolha o tipo de relatório", [
        "Contas Vencidas", 
        "Contas Pagas", 
        "Contas a Vencer", 
        "Contas por Fornecedor", 
        "Contas por Status", 
        "Contas por Data", 
    ])
    titulo = f"Relatório de Fluxo de Caixa - {option}"
    # Lógica para selecionar o tipo de relatório
    if option == "Contas Vencidas":
        contas = listar_contas_vencidas()
        filename = "relatorio_contas_vencidas.pdf"
    
    elif option == "Contas Pagas":
        contas = listar_contas_pagas()
        filename = "relatorio_contas_pagas.pdf"
    
    elif option == "Contas a Vencer":
        contas = listar_contas_a_vencer()
        filename = "relatorio_contas_a_vencer.pdf"
    
    elif option == "Contas por Fornecedor":
        fornecedor_id = st.text_input("Digite o ID do Fornecedor")
        if fornecedor_id:
            contas = listar_contas_por_fornecedor(fornecedor_id)
            titulo = titulo + fornecedor_id
            filename = f"relatorio_contas_fornecedor_{fornecedor_id}.pdf"

    elif option == "Contas por Status":
        status = st.selectbox("Escolha o Status", ["Pendente", "Pago"])
        contas = listar_contas_por_status(status)
        titulo = f"Relatório de Contas com Status: {status}"
        filename = "relatorio_contas_por_status.pdf"

    elif option == "Contas por Data":
        data_inicial = st.date_input("Data Inicial")
        data_final = st.date_input("Data Final")
        if data_inicial and data_final:
            contas = listar_contas_por_data(data_inicial, data_final)
            titulo = f"Relatório de Contas entre {data_inicial} e {data_final}"
            filename = "relatorio_contas_por_data.pdf"
    
    if contas:  # Verifica se contas não está vazia
        total = calcular_total(contas)  # Calcula o total das contas
        st.write(f"**Total:** R$ {total:.2f}")  # Exibe o total

    if st.button("Gerar Relatório PDF"):
        if contas:  # Verifica se contas não está vazia
            # Gera o relatório de contas e obtém o conteúdo do PDF
            pdf_data = gerar_relatorio_pdf(contas, filename, titulo, nome_empresa)  
        
            # Oferece o PDF para download
            st.download_button("Baixar Relatório", pdf_data, filename, "application/pdf")
        else:
            st.warning("Nenhuma conta encontrada para o relatório selecionado.")

# Chame a função main para executar o aplicativo
if __name__ == "__main__":
    main()