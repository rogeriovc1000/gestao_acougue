import streamlit as st

# Inicializa o estado da sessão se não existir
if 'current_page' not in st.session_state:
    st.session_state.current_page = 'login'  # Página inicial

# Função para renderizar a página de login
def render_login_page():
    st.title("Página de Login")  # Título da tela de login
    username = st.text_input("Usuário", key="username")  # Adicionando um key único
    password = st.text_input("Senha", type="password", key="password")  # Adicionando um key único
    if st.button("Entrar"):
            # Aqui você pode adicionar a lógica de autenticação
            if username == "rogerio" and password == "2401":  # Substitua por sua lógica real
                st.session_state.current_page = "tela_entrada"  # Muda para a página principal
                st.rerun()  # Reinicia o aplicativo para renderizar a nova página
            else:
                st.error("Usuário ou senha incorretos!")

# Função para renderizar a página com base no estado
def render_page():
    if st.session_state.current_page == 'login':
        render_login_page()  # Renderiza a página de login
    elif st.session_state.current_page == 'tela_entrada':
        from tela_entrada import show_screen  # Importa a função aqui
        show_screen()  # Renderiza a tela de entrada

# Chama a função de renderização da página
render_page()