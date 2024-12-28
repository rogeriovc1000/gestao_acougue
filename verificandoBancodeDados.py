import os
import stat
import streamlit as st
# Verificação de permissões
def verificar_permissoes_banco():
    db_path = 'bancodedados/acougue_db.db'
    try:
        # Verifica se o arquivo existe
        if not os.path.exists(db_path):
            st.error(f"Arquivo de banco de dados não encontrado: {db_path}")
            return False
        
        # Verifica permissões de leitura e escrita
        st.write(f"Permissões do arquivo: {oct(os.stat(db_path).st_mode)}")
        
        # Tenta abrir o arquivo para verificar permissões
        with open(db_path, 'r+') as f:
            pass
        return True
    except PermissionError:
        st.error("Sem permissão para acessar o banco de dados")
        return False
    except Exception as e:
        st.error(f"Erro ao verificar permissões: {e}")
        return False