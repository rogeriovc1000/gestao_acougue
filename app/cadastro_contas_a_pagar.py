import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import time

# Configurações de banco de dados
DB_PATH = 'bancodedados/acougue_db.db'

def criar_tabela():
    """Cria as tabelas necessárias no banco de dados"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        
        # Tabela de Fornecedores
        cursor.execute('''CREATE TABLE IF NOT EXISTS TB_FORNECEDOR (
                    ID_FORNECEDOR INTEGER PRIMARY KEY AUTOINCREMENT,
                    NOME_FORNECEDOR VARCHAR(50) NOT NULL,
                    ENDERECO_FORNECEDOR VARCHAR(100),
                    TELEFONE_FORNECEDOR VARCHAR(10),
                    EMAIL_FORNECEDOR VARCHAR(40))''')
        
        # Tabela de Contas a Pagar
        cursor.execute('''CREATE TABLE IF NOT EXISTS TB_CONTAS_A_PAGAR (
                    ID_CONTA_A_PAGAR INTEGER PRIMARY KEY AUTOINCREMENT,
                    ID_FORNECEDOR INTEGER,
                    DATA_VENCIMENTO DATE NOT NULL,
                    VALOR_CONTA DECIMAL(10, 2) NOT NULL,
                    VALOR_PAGO DECIMAL(10, 2) DEFAULT NULL,
                    STATUS_CONTA VARCHAR(50) NOT NULL,
                    DATA_PAGAMENTO DATE,
                    FOREIGN KEY(ID_FORNECEDOR) REFERENCES TB_FORNECEDOR(ID_FORNECEDOR))''')
        
        conn.commit()
        print("Tabelas criadas com sucesso!")
    except sqlite3.Error as e:
        st.error(f"Erro ao criar tabelas: {e}")
    finally:
        if conn:
            conn.close()

def executar_query(query, params=(), fetch=False):
    """Executa uma query no banco de dados"""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute(query, params)
        
        if fetch:
            resultado = cursor.fetchall()
        else:
            resultado = None
        
        conn.commit()
        return resultado
    except sqlite3.Error as e:
        st.error(f"Erro no banco de dados: {e}")
        return None
    finally:
        if conn:
            conn.close()

def listar_fornecedores():
    """Lista todos os fornecedores"""
    query = "SELECT * FROM TB_FORNECEDOR"
    resultado = executar_query(query, fetch=True)
    return pd.DataFrame(resultado, columns=['ID', 'Nome', 'Endereço', 'Telefone', 'Email']) if resultado else None

def listar_contas_a_pagar():
    """Lista todas as contas a pagar"""
    query = '''
    SELECT 
        c.ID_CONTA_A_PAGAR, 
        f.NOME_FORNECEDOR, 
        c.DATA_VENCIMENTO, 
        c.VALOR_CONTA, 
        c.VALOR_PAGO,
        c.DATA_PAGAMENTO, 
        c.STATUS_CONTA, 
        c.VALOR_DEBITO
    FROM 
        TB_CONTAS_A_PAGAR c
    LEFT JOIN 
        TB_FORNECEDOR f ON c.ID_FORNECEDOR = f.ID_FORNECEDOR
    '''
    resultado = executar_query(query, fetch=True)
    
    if resultado:
        df = pd.DataFrame(resultado, columns=[
            'ID', 'Fornecedor', 'Vencimento', 
            'Valor', 'Pago', 'Pagamento', 'Status', 'Debito'
        ])

        # Convertendo a coluna de data de pagamento para datetime
        df['Pagamento'] = pd.to_datetime(df['Pagamento'], errors='coerce')

        return df
    return None

def incluir_conta(id_fornecedor, data_vencimento, valor_conta, valor_pago, data_pagamento, status_conta, debito):
    """Inclui uma nova conta a pagar"""
    try:
        
        status_conta = "Pendente"
        query = '''
        INSERT INTO TB_CONTAS_A_PAGAR 
        (ID_FORNECEDOR, DATA_VENCIMENTO, VALOR_CONTA, VALOR_PAGO, DATA_PAGAMENTO, STATUS_CONTA, VALOR_DEBITO)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        '''
        
        executar_query(query, (
            id_fornecedor, 
            data_vencimento, 
            valor_conta, 
            valor_pago, 
            data_pagamento, 
            status_conta,
            debito
        ))
        
        st.success("Conta incluída com sucesso!")
        return True
    except Exception as e:
        st.error(f"Erro ao incluir conta: {e}")
        return False

def atualizar_conta(id_conta, valor_conta, valor_pago, data_pagamento, debito):
    """Atualiza uma conta existente"""
    try:
        # Determina o status da conta
        status_conta = "Pago" if data_pagamento and valor_pago >= valor_conta else "Pendente"
        
        query = '''
        UPDATE TB_CONTAS_A_PAGAR 
        SET VALOR_CONTA = ?, VALOR_PAGO = ?, 
            DATA_PAGAMENTO = ?, STATUS_CONTA = ?, VALOR_DEBITO = ? 
        WHERE ID_CONTA_A_PAGAR = ?
        '''
        
        executar_query(query, (
            valor_conta, 
            valor_pago, 
            data_pagamento, 
            status_conta, 
            debito,
            id_conta
        ))
        return True
    except Exception as e:
        st.error(f"Erro ao atualizar conta: {e}")
        return False

def excluir_conta(id_conta):
    """Exclui uma conta"""
    try:
        query = "DELETE FROM TB_CONTAS_A_PAGAR WHERE ID_CONTA_A_PAGAR = ?"
        executar_query(query, (id_conta,))
        st.success("Conta excluída com sucesso!")
        return True
    except Exception as e:
        st.error(f"Erro ao excluir conta: {e}")
        return False

def contas_vencidas():
    """Retorna contas vencidas"""
    query = '''
    SELECT * FROM TB_CONTAS_A_PAGAR 
    WHERE DATA_VENCIMENTO < ? AND STATUS_CONTA != 'Pago'
    '''
    resultado = executar_query(query, (datetime.now().strftime('%Y-%m-%d'),), fetch=True)
    return pd.DataFrame(resultado, columns=[
        'ID', 'ID_Fornecedor', 'Vencimento', 
        'Valor', 'Pago', 'Pagamento', 'Status', 'Debito'
    ]) if resultado else None

def main():
    # Cria as tabelas se não existirem
    criar_tabela()
    
    st.title("Gerenciamento de Contas a Pagar")
    
    # Menu de opções
    opcao = st.sidebar.selectbox("Selecione uma opção", [
        "Listar Contas", 
        "Incluir Conta", 
        "Atualizar Conta", 
        "Excluir Conta", 
        "Contas Vencidas"
    ])
    
    if opcao == "Listar Contas":
        st.subheader("Contas Cadastradas")
        df_contas = listar_contas_a_pagar()
        if df_contas is not None and not df_contas.empty:
            # Exibir o DataFrame em um formato editável
            df_editado = st.dataframe(df_contas, key="editor", hide_index=True)

        else:
            st.warning("Nenhuma conta encontrada.")
    
    elif opcao == "Incluir Conta":
        st.subheader("Incluir Nova Conta")
        df_fornecedores = listar_fornecedores()
        
        if df_fornecedores is not None and not df_fornecedores.empty:
            fornecedores_dict = dict(zip(df_fornecedores['Nome'], df_fornecedores['ID']))
            selected_fornecedor_nome = st.selectbox("Selecione o Fornecedor", list(fornecedores_dict.keys()))
            id_fornecedor = fornecedores_dict[selected_fornecedor_nome] 
            
            data_vencimento = st.date_input("Data de Vencimento")
            valor_conta = st.number_input("Valor da Conta", min_value=0.0)
            valor_pago = st.number_input("Valor Pago", min_value=0.0)
            data_pagamento = st.date_input("Data de Pagamento", value=None)
            valor_debito = int(valor_conta)-int(valor_pago)
            status_conta = "Pendente"
            if st.button(" Incluir Conta"):
                if not data_vencimento or valor_conta <= 0:
                    st.error("Por favor, preencha todos os campos obrigatórios corretamente.")
                else:
                    incluir_conta(id_fornecedor, data_vencimento, valor_conta, valor_pago, data_pagamento, status_conta, valor_debito)
        else:
            st.error("Não há fornecedores cadastrados para incluir uma conta.")
    
    elif opcao == "Atualizar Conta":
        st.subheader("Atualizar Conta")
        
        # Exibe todas as contas cadastradas
        df_contas = listar_contas_a_pagar()
        
        if df_contas is not None and not df_contas.empty:
            # Cria duas colunas
            col1, col2 = st.columns(2)

            with col1:
                st.dataframe(df_contas, hide_index=True)
                
            with col2:
                # Campo para inserir o ID da conta a ser atualizada
                id_conta_input = st.text_input("Digite o ID da Conta para Atualização", "")
            
                if id_conta_input:
                    conta = df_contas[df_contas['ID'] == int(id_conta_input)]
                    if not conta.empty:
                        valor_conta = st.number_input("Valor da Conta", value=float(conta['Valor'].iloc[0]), min_value=0.0)
                        valor_pago = st.number_input("Valor Pago", value=float(conta['Pago'].iloc[0]), min_value=0.0)
                        valor_debito = int(valor_conta) - int(valor_pago)
                        
                        # Exibe o valor do débito
                        if valor_debito > 0:
                            st.markdown(f"<h2 style='color: red;'>Valor Débito: R$ {round(valor_debito, 2)}</h2>", unsafe_allow_html=True)
                        else:
                            st.markdown(f"<h2 style='color: green;'>Valor Débito: R$ {round(valor_debito, 2)}</h2>", unsafe_allow_html=True)

                        # Verifica se a data de pagamento é válida e converte
                        data_pagamento_value = conta['Pagamento'].iloc[0]
                        if pd.notnull(data_pagamento_value):
                            data_pagamento = pd.to_datetime(data_pagamento_value).date()  # Converte para objeto date
                        else:
                            data_pagamento = None  # Ou você pode definir uma data padrão, como datetime.now().date()

                        data_pagamento = st.date_input("Data de Pagamento", value=data_pagamento)

                        if st.button("Salvar Alterações"):
                            atualizar_conta(int(id_conta_input), valor_conta, valor_pago, data_pagamento, valor_debito)
                            st.success("Contas atualizadas com sucesso!")
                            time.sleep(3)
                            st.rerun()
                    else:
                        st.error("Conta não encontrada.")
                else:
                    st.error("Por favor, insira um ID válido.")
        else:
            st.error("Não há contas cadastradas para atualização.")
                
    elif opcao == "Excluir Conta":
        st.subheader("Excluir Conta")
        df_contas = listar_contas_a_pagar()
        
        if df_contas is not None and not df_contas.empty:
            st.dataframe(df_contas[['ID', 'Fornecedor', 'Valor', 'Vencimento', 'Pago', 'Pagamento', 'Status', 'Debito']])
            id_conta_input = st.text_input("Digite o ID da Conta para Exclusão", "")

            if id_conta_input:
                # Verifica se a conta existe
                conta_existe = df_contas[df_contas['ID'] == int(id_conta_input)]
                if not conta_existe.empty:
                    if st.button("Confirmar Exclusão"):
                        excluir_conta(int(id_conta_input))
                else:
                    st.error("Conta não encontrada. Por favor, verifique o ID.")
            else:
                st.warning("Por favor, selecione um ID válido.")
        else:
            st.error("Não há contas cadastradas para exclusão.")

    elif opcao == "Contas Vencidas":
        st.subheader("Contas Vencidas")
        df_vencidas = contas_vencidas()
        if df_vencidas is not None:
            st.dataframe(df_vencidas, hide_index=True)
        else:
            st.warning("Nenhuma conta vencida encontrada.")

if __name__ == "__main__":
    main() 