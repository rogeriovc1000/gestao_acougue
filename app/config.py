# config.py

import streamlit as st
import os

# Configurações do Banco de Dados
DB_NAME = 'acougue_db.db'
DB_PATH = os.path.join(os.getcwd(), 'bancodedados', DB_NAME)

# Configurações de Conexão
DB_CONNECTION_TIMEOUT = 5  # Tempo limite de conexão em segundos

# Configurações do Relatório
REPORT_TITLE = "Relatório de Contas"
REPORT_PAGE_SIZE = "letter"  # Tamanho da página do relatório
REPORT_FONT_SIZE = 12  # Tamanho da fonte para o relatório

# Configurações de Logging
LOGGING_LEVEL = 'DEBUG'  # Níveis: DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_FILE_PATH = os.path.join(os.getcwd(), 'logs', 'app.log')

# Outras configurações
MAX_RECORDS_PER_PAGE = 40  # Número máximo de registros por página

# Definindo as variáveis
NOME_EMPRESA = "ACOUGUE GOURMET S - RUBENS E SEIR"
ENDEREÇO_EMPRESA = "Rua tal, n. 00 - Rio Marinho - Cariacica - ES"
TELEFONE_EMPRESA = "27-99999-9999"

def rodape():
        
        st.sidebar.markdown(f"""
            <footer style="position: fixed; left: 0; bottom: 0; width: 100%; text-align: center; padding: 5px; background-color: #f1f1f1; color: #000;">
                <p>
                    <strong></strong> {NOME_EMPRESA}<br>
                    <strong></strong> {ENDEREÇO_EMPRESA}<br>
                    <strong></strong> {TELEFONE_EMPRESA}
                </p>
            </footer>
        """, unsafe_allow_html=True)

def main():
      pass

if __name__ == "__main__":
    main()  