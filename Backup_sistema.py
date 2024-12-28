import sqlite3
import shutil
import os
from datetime import datetime
import streamlit as st
import time
import backup_sistema_restaurar 

# Defina o caminho e o nome do arquivo do banco de dados
db_file = os.path.join(os.getcwd(), 'bancodedados/acougue_db.db')

def gerar_backup():
    # Cria um nome de arquivo para o backup com timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = os.path.join(os.getcwd(), f"backup/acougue_db_backup_{timestamp}.db")
    
    # Cria o diretório de backup se não existir
    os.makedirs(os.path.dirname(backup_file), exist_ok=True)
    
    # Copia o arquivo do banco de dados para o novo arquivo de backup
    shutil.copy2(db_file, backup_file)
    return backup_file

def main():
    st.title("Sistema de Gerenciamento de Banco de Dados")

    # Menu lateral
    menu = st.sidebar.selectbox("Selecione uma opção", ["Home", "Gerar Backup", "Restaurar Backup"])

    if menu == "Gerar Backup":
            
        if st.button("Gerar Backup"):
                # Inicializa a barra de progresso
                progress_bar = st.progress(0)
                for i in range(100):
                    time.sleep(0.03)  # Simula o tempo de processamento
                    progress_bar.progress(i + 1)  # Atualiza a barra de progresso
                
                # Gera o backup
                backup_file = gerar_backup()
                
                # Exibe a mensagem de sucesso
                st.success(f"Backup gerado com sucesso: {backup_file}")
                
                # Aguarda o usuário pressionar um botão para continuar
                if st.button("OK, voltar ao menu"):
                    st.session_state.senha_correta = False  # Reseta o estado da senha
                    st.experimental_rerun()  # Reinicia o aplicativo para voltar ao menu

    elif menu == "Restaurar Backup":
        backup_sistema_restaurar.main()     
    
    elif menu == "Home":
        st.write("Bem-vindo ao Sistema de Gerenciamento de Banco de Dados!")

    

if __name__ == "__main__":
    main()