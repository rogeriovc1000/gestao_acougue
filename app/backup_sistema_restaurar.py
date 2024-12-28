import os
import shutil
import streamlit as st
import time  # Importa o módulo time para simular o tempo de processamento

# Função para listar arquivos de backup
def listar_backups(diretorio):
    try:
        arquivos = [f for f in os.listdir(diretorio) if f.endswith('.db')]  # Filtra apenas arquivos .db
        return arquivos
    except Exception as e:
        st.error(f"Ocorreu um erro ao listar os arquivos de backup: {e}")
        return []

# Função para restaurar um arquivo de backup
def restaurar_backup(arquivo_backup, destino):
    try:
        # Define o caminho do arquivo de destino com o novo nome
        novo_nome = "acougue_db.db"
        caminho_destino = os.path.join(destino, novo_nome)
        
        # Inicializa a barra de progresso
        progress_bar = st.progress(0)
        
        # Simula o tempo de processamento da restauração
        for i in range(100):
            time.sleep(0.03)  # Simula o tempo de processamento
            progress_bar.progress(i + 1)  # Atualiza a barra de progresso
        
        # Copia o arquivo de backup para o destino com o novo nome
        shutil.copy(arquivo_backup, caminho_destino)
        st.success(f"Backup restaurado com sucesso: {arquivo_backup} para {caminho_destino}")
    except Exception as e:
        st.error(f"Ocorreu um erro ao restaurar o backup: {e}")

def main():
    st.title("Restauração de Backup")

    # Diretório onde os backups estão armazenados
    diretorio_backups = "G:/xampp/htdocs/projeto_controle_administrativo/acougue/app/backups"  # Caminho correto

    # Listar arquivos de backup
    arquivos_backups = listar_backups(diretorio_backups)

    if arquivos_backups:
        st.subheader("Selecione um arquivo de backup para restaurar:")
        arquivo_selecionado = st.selectbox("Arquivos de Backup", arquivos_backups)

        # Botão para restaurar o backup
        if st.button("Restaurar Backup"):
            destino = "G:/xampp/htdocs/projeto_controle_administrativo/acougue/app/bancodedados"  # Altere para o caminho real de restauração
            caminho_backup = os.path.join(diretorio_backups, arquivo_selecionado)
            restaurar_backup(caminho_backup, destino)

            # Aguarda o usuário pressionar um botão para continuar
            if st.button("OK, voltar ao menu"):
                st.session_state.senha_correta = False  # Reseta o estado da senha
                st.experimental_rerun()  # Reinicia o aplicativo para voltar ao menu
    else:
        st.warning("Nenhum arquivo de backup encontrado.")

if __name__ == "__main__":
    main()