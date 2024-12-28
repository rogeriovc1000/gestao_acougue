# calculos.py
import locale
import pandas as pd
# Defina a localidade para o Brasil
locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')

def formatar_moeda(valor):
    """Formata um valor monetário para o padrão brasileiro."""
    return locale.currency(valor, grouping=True, symbol=True)

def calcular_totais(contas):
    total_entrada = 0
    total_saida = 0
    saldo = 0
    for conta in contas:
        # Converte o valor para numérico
        valor_FLUXO_DE_CAIXA = pd.to_numeric(conta['VALOR_FLUXO_DE_CAIXA'], errors='coerce')  # Converte para numérico
        if pd.isna(valor_FLUXO_DE_CAIXA):  # Se o valor for NaN, trate como zero
            valor_FLUXO_DE_CAIXA = 0

        # Verifica o tipo de fluxo e acumula os totais
        if conta['ID_CATEGORIA'] == 1:
            total_entrada += valor_FLUXO_DE_CAIXA
        else:
            total_saida += valor_FLUXO_DE_CAIXA
    saldo = int(total_entrada) - int(total_saida)
    return abs(total_entrada), abs(total_saida), int(saldo)



