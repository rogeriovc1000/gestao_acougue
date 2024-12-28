import streamlit as st
import sqlite3
import os

# Função para atualizar os dados da empresa
nome = "Banca do Ruber e Seir - Carnes Suinas"
endereco = "Rua do Ruber, sn"
telefone = "+55 27 99717-4297"
   

# Interface Streamlit
def main():
    st.markdown(
    f"""
    <style>
        .footer {{
            position: fixed;
            left: 0;
            bottom: 0;
            width: 100vw;  /* Largura da viewport */
            background-color: #f1f1f1;
            text-align: center;
            padding: 10px;
            font-size: 12px;
            color: #333;
            z-index: 1000;  /* Garante que o rodapé fique acima de outros elementos */
        }}
    </style>
    <div class="footer">
        <p>{nome} | {endereco} | {telefone}</p>
    </div>
    """,
    unsafe_allow_html=True
)
    
if __name__ == "__main__":
    main()