import time
import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

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
        
        # Tabela de Contas a Receber
        cursor.execute('''CREATE TABLE IF NOT EXISTS TB_CONTAS_A_RECEBER (
                    ID_CONTA_A_RECEBER INTEGER PRIMARY KEY AUTOINCREMENT,
                    ID_CLIENTE INTEGER,
                    DATA_VENCIMENTO DATE NOT NULL,
                    VALOR_CONTA DECIMAL(10, 2) NOT NULL,
                    VALOR_RECEBIDO DECIMAL(10, 2) DEFAULT NULL,
                    STATUS_CONTA VARCHAR(50) NOT NULL,
                    DATA_RECEBIMENTO DATE,
                    VALOR_DEBITO DECIMAL(10, 2) DEFAULT NULL,
                    FOREIGN KEY(ID_CLIENTE) REFERENCES TB_CLIENTE(ID_CLIENTE))''')

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

def listar_contas_a_receber():
    """Lista todas as contas a receber"""
    query = '''
    SELECT 
        c.ID_CONTA_A_RECEBER, 
        cl.NOME_CLIENTE, 
        c.DATA_VENCIMENTO, 
        c.VALOR_CONTA, 
        c.VALOR_RECEBIDO,
        c.DATA_RECEBIMENTO, 
        c.STATUS_CONTA, 
        c.VALOR_DEBITO
    FROM 
        TB_CONTAS_A_RECEBER c
    LEFT JOIN 
        TB_CLIENTE cl ON c.ID_CLIENTE = cl.ID_CLIENTE
    '''
    resultado = executar_query(query, fetch=True)
    
    if resultado:
        df = pd.DataFrame(resultado, columns=[
            'ID', 'Cliente', 'Vencimento', 
            'Valor', 'Recebido', 'Recebimento', 'Status', 'Debito'
        ])

        # Convertendo a coluna de data de recebimento para datetime
        df['Recebimento'] = pd.to_datetime(df['Recebimento'], errors='coerce')

        return df
    return None

def listar_clientes():
    """Lista todos os clientes"""
    query = "SELECT * FROM TB_CLIENTE"  # Supondo que a tabela de clientes se chama TB_CLIENTE
    resultado = executar_query(query, fetch=True)
    
    if resultado:
        # Cria um DataFrame com os resultados
        df = pd.DataFrame(resultado, columns=['ID', 'Nome', 'Endereço', 'Telefone', 'Email'])  # Ajuste os nomes das colunas conforme necessário
        return df
    return None

def incluir_conta_receber(id_cliente, data_vencimento, valor_conta, valor_recebido, data_recebimento, status_conta, debito):
    """Inclui uma nova conta a receber"""
    try:
        status_conta = "Pendente"
        query = '''
        INSERT INTO TB_CONTAS_A_RECEBER 
        (ID_CLIENTE, DATA_VENCIMENTO, VALOR_CONTA, VALOR_RECEBIDO, DATA_RECEBIMENTO, STATUS_CONTA, VALOR_DEBITO)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        '''
        
        executar_query(query, (
            id_cliente, 
            data_vencimento, 
            valor_conta, 
            valor_recebido, 
            data_recebimento, 
            status_conta,
            debito
        ))
        
        st.success("Conta a receber incluída com sucesso!")
        return True
    except Exception as e:
        st.error(f"Erro ao incluir conta a receber: {e}")
        return False

def atualizar_conta_receber(id_conta, valor_conta, valor_recebido, data_recebimento, debito):
    """Atualiza uma conta a receber existente"""
    try:
        # Determina o status da conta
        status_conta = "Recebido" if data_recebimento and valor_recebido >= valor_conta else "Pendente"
        
        query = '''
        UPDATE TB_CONTAS_A_RECEBER 
        SET VALOR_CONTA = ?, VALOR_RECEBIDO = ?, 
            DATA_RECEBIMENTO = ?, STATUS_CONTA = ?, VALOR_DEBITO = ? 
        WHERE ID_CONTA_A_RECEBER = ?
        '''
        
        executar_query(query, (
            valor_conta, 
            valor_recebido, 
            data_recebimento, 
            status_conta, 
            debito,
            id_conta
        ))
        
        st.success("Conta a receber atualizada com sucesso!")
        return True
    except Exception as e:
        st.error(f"Erro ao atualizar conta a receber: {e}")
        return False

def excluir_conta_receber(id_conta):
    """Exclui uma conta a receber"""
    try:
        query = "DELETE FROM TB_CONTAS_A_RECEBER WHERE ID_CONTA_A_RECEBER = ?"
        executar_query(query, (id_conta,))
        st.success("Conta a receber excluída com sucesso!")
        return True
    except Exception as e:
        st.error(f"Erro ao excluir conta a receber: {e}")
        return False

def contas_vencidas_receber():
    """Retorna contas a receber vencidas"""
    query = '''
    SELECT * FROM TB_CONTAS_A_RECEBER 
    WHERE DATA_VENCIMENTO < ? AND STATUS_CONTA != 'Recebido'
    '''
    resultado = executar_query(query, (datetime.now().strftime('%Y-%m-%d'),), fetch=True)
    return pd.DataFrame(resultado, columns=[
        'ID', 'ID_Cliente', 'Vencimento', 
        'Valor', 'Recebido', 'Recebimento', 'Status', 'Debito'
    ]) if resultado else None

def main():
    # Cria as tabelas se não existirem
    criar_tabela()
    
    st.title("Gerenciamento contas a Receber")
    
    # Menu de opções
    opcao = st.sidebar.selectbox("Selecione uma opção", [
        "Listar Contas a Receber", 
        "Incluir Conta a Receber", 
        "Atualizar Conta a Receber", 
        "Excluir Conta a Receber", 
        "Contas Vencidas a Receber"
    ])
    
    if opcao == "Listar Contas a Receber":
        st.subheader("Contas a Receber Cadastradas")
        df_contas = listar_contas_a_receber()
        if df_contas is not None and not df_contas.empty:
            st.dataframe(df_contas, key="editor", hide_index=True)
        else:
            st.warning("Nenhuma conta a receber encontrada.")

    elif opcao == "Incluir Conta a Receber":
        st.subheader("Incluir Nova Conta a Receber")
        df_clientes = listar_clientes()

        if df_clientes is not None and not df_clientes.empty:
            clientes_dict = dict(zip(df_clientes['Nome'], df_clientes['ID']))
            selected_cliente_nome = st.selectbox("Selecione o Cliente", list(clientes_dict.keys()))
            id_cliente = clientes_dict[selected_cliente_nome] 
            
            data_vencimento = st.date_input("Data de Vencimento")
            valor_conta = st.number_input("Valor da Conta", min_value=0.0)
            valor_recebido = st.number_input("Valor Recebido", min_value=0.0)
            data_recebimento = st.date_input("Data de Recebimento", value=None)
            valor_debito = int(valor_conta) - int(valor_recebido)
            status_conta = "Pendente"
            if st.button("Incluir Conta"):
                if not data_vencimento or valor_conta <= 0:
                    st.error("Por favor, preencha todos os campos obrigatórios corretamente.")
                else:
                    incluir_conta_receber(id_cliente, data_vencimento, valor_conta, valor_recebido, data_recebimento, status_conta, valor_debito)
        else:
            st.error("Não há clientes cadastrados para incluir uma conta.")

    elif opcao == "Atualizar Conta a Receber":
        st.subheader("Atualizar Conta a Receber")
        df_contas = listar_contas_a_receber()

        if df_contas is not None and not df_contas.empty:
            col1, col2 = st.columns(2)
            with col1:
                st.dataframe(df_contas, hide_index=True)
            with col2:
                id_conta_input = st.text_input("Digite o ID da Conta para Atualização", "")
            
                if id_conta_input:
                    conta = df_contas[df_contas['ID'] == int(id_conta_input)]
                    if not conta.empty:
                        
                            valor_conta = st.number_input("Valor da Conta", value=float(conta['Valor'].iloc[0]), min_value=0.0)
                            valor_recebido = st.number_input("Valor Recebido", value=float(conta['Recebido'].iloc[0]), min_value=0.0)
                            valor_debito = int(valor_conta) - int(valor_recebido)
                            
                            if valor_debito > 0:
                                st.markdown(f"<h2 style='color: red;'>Valor Débito: R$ {round(valor_debito, 2)}</h2>", unsafe_allow_html=True)
                            else:
                                st.markdown(f"<h2 style='color: green;'>Valor Débito: R$ {round(valor_debito, 2)}</h2>", unsafe_allow_html=True)

                            data_recebimento_value = conta['Recebimento'].iloc[0]
                            if pd.notnull(data_recebimento_value):
                                data_recebimento = pd.to_datetime(data_recebimento_value).date()
                            else:
                                data_recebimento = None

                            data_recebimento = st.date_input("Data de Recebimento", value=data_recebimento)

                            if st.button("Salvar Alterações"):
                                atualizar_conta_receber(int(id_conta_input), valor_conta, valor_recebido, data_recebimento, valor_debito)
                                st.success("Contas atualizadas com sucesso!")
                                time.sleep(3)
                                st.rerun()
                    else:
                        st.error("Conta não encontrada.")
                else:
                    with col2:
                        st.error("Por favor, insira um ID válido.")
        else:
            st.error("Não há contas cadastradas para atualização.")

    elif opcao == "Excluir Conta a Receber":
        st.subheader("Excluir Conta a Receber")
        df_contas = listar_contas_a_receber()

        if df_contas is not None and not df_contas.empty:
            st.dataframe(df_contas[['ID', 'Cliente', 'Valor', 'Vencimento', 'Recebido', 'Recebimento', 'Status', 'Debito']])
            id_conta_input = st.text_input("Digite o ID da Conta para Exclusão", "")

            if id_conta_input:
                conta_existe = df_contas[df_contas['ID'] == int(id_conta_input)]
                if not conta_existe.empty:
                    if st.button("Confirmar Exclusão"):
                        excluir_conta_receber(int(id_conta_input))
                else:
                    st.error("Conta não encontrada. Por favor, verifique o ID.")
            else:
                st.warning("Por favor, selecione um ID válido.")
        else:
            st.error("Não há contas cadastradas para exclusão.")

    elif opcao == "Contas Vencidas a Receber":
        st.subheader("Contas Vencidas a Receber")
        df_vencidas = contas_vencidas_receber()
        if df_vencidas is not None:
            st.dataframe(df_vencidas, hide_index=True)
        else:
            st.warning("Nenhuma conta vencida encontrada.")

if __name__ == "__main__":
    main()