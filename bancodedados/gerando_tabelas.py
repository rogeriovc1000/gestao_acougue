import os
import sqlite3

# Defina o caminho e o nome do arquivo do banco de dados
db_file = os.path.join(os.getcwd(), 'bancodedados/acougue_db.db')

# Crie o arquivo do banco de dados se não existir
if not os.path.exists(db_file):
    open(db_file, 'w').close()

# Conecte-se ao banco de dados
conn = sqlite3.connect(db_file)
cursor = conn.cursor()

# Criar tabelas
print('criando tabela usuarios...')
cursor.execute('''
    CREATE TABLE IF NOT EXISTS TB_USUARIO (
        ID_USUARIO INTEGER PRIMARY KEY AUTOINCREMENT,
        NOME_USUARIO VARCHAR(50) NOT NULL,
        SENHA VARCHAR(50) NOT NULL,
        TIPO_USUARIO VARCHAR(50) NOT NULL,
        EMAIL VARCHAR(50) NOT NULL
    )
''')

print('criando tabela clientes...')
cursor.execute('''
    CREATE TABLE IF NOT EXISTS TB_CLIENTE (
        ID_CLIENTE INTEGER PRIMARY KEY AUTOINCREMENT,
        NOME_CLIENTE VARCHAR(50) NOT NULL,
        ENDERECO_CLIENTE VARCHAR(100) NOT NULL,
        TELEFONE_CLIENTE VARCHAR(20) NOT NULL,
        EMAIL_CLIENTE VARCHAR(50) NOT NULL
    )
''')

print('criando tabela fornecedores...')
cursor.execute('''
    CREATE TABLE IF NOT EXISTS TB_FORNECEDOR (
        ID_FORNECEDOR INTEGER PRIMARY KEY AUTOINCREMENT,
        NOME_FORNECEDOR VARCHAR(50) NOT NULL,
        ENDERECO_FORNECEDOR VARCHAR(100) NOT NULL,
        TELEFONE_FORNECEDOR VARCHAR(20) NOT NULL,
        EMAIL_FORNECEDOR VARCHAR(50) NOT NULL
    )
''')

print('criando tabela categorias...')
cursor.execute('''
    CREATE TABLE IF NOT EXISTS TB_CATEGORIAS (
        ID_CATEGORIA INTEGER PRIMARY KEY AUTOINCREMENT,
        NOME_CATEGORIA VARCHAR(50) NOT NULL
    )
''')

print('criando tabela produtos...')
cursor.execute('''
    CREATE TABLE IF NOT EXISTS TB_PRODUTO (
        ID_PRODUTO INTEGER PRIMARY KEY AUTOINCREMENT,
        NOME_PRODUTO VARCHAR(50) NOT NULL,
        DESCRICAO_PRODUTO VARCHAR(100) NOT NULL,
        PRECO_PRODUTO DECIMAL(10,2) NOT NULL,
        QUANTIDADE_ESTOQUE INTEGER NOT NULL
    )
''')

print('criando tabela contas a pagar...')
cursor.execute('''
    CREATE TABLE IF NOT EXISTS TB_CONTA_A_PAGAR (
        ID_CONTA_A_PAGAR INTEGER PRIMARY KEY AUTOINCREMENT,
        ID_FORNECEDOR INTEGER NOT NULL,
        DATA_VENCIMENTO DATE NOT NULL,
        VALOR_CONTA DECIMAL(10,2) NOT NULL,
        STATUS_CONTA VARCHAR(50) NOT NULL,
        FOREIGN KEY (ID_FORNECEDOR) REFERENCES TB_FORNECEDOR(ID_FORNECEDOR)
    )
''')

print('criando tabela contas a receber...')
cursor.execute('''
    CREATE TABLE IF NOT EXISTS TB_CONTA_A_RECEBER (
        ID_CONTA_A_RECEBER INTEGER PRIMARY KEY AUTOINCREMENT,
        ID_CLIENTE INTEGER NOT NULL,
        DATA_VENCIMENTO DATE NOT NULL,
        VALOR_CONTA DECIMAL(10, 2) NOT NULL,
        STATUS_CONTA VARCHAR(50) NOT NULL,
        FOREIGN KEY (ID_CLIENTE) REFERENCES TB_CLIENTE(ID_CLIENTE)
    )
''')

print('criando tabela fluxo de caixa...')
cursor.execute('''
    CREATE TABLE IF NOT EXISTS TB_FLUXO_DE_CAIXA (
        ID_FLUXO_DE_CAIXA INTEGER PRIMARY KEY AUTOINCREMENT,
        ID_CATEGORIA INTEGER NOT NULL,
        DESCRICAO_FLUXO_DE_CAIXA VARCHAR(100) NOT NULL,
        VALOR_FLUXO_DE_CAIXA DECIMAL(10,2) NOT NULL,
        DATA_FLUXO_DE_CAIXA DATE NOT NULL,
        FOREIGN KEY (ID_CATEGORIA) REFERENCES TB_CATEGORIAS(ID_CATEGORIA)
    )
''')

print('criando tabela funcionarios...')
cursor.execute('''
    CREATE TABLE IF NOT EXISTS TB_FUNCIONARIO (
        ID_FUNCIONARIO INTEGER PRIMARY KEY AUTOINCREMENT,
        NOME_FUNCIONARIO VARCHAR(50) NOT NULL,
        CARGO VARCHAR(50) NOT NULL,
        SALARIO DECIMAL(10,2) NOT NULL,
        TELEFONE_FUNCIONARIO VARCHAR(20) NOT NULL
    )
''')

# Criar índices para as tabelas
print('criando indices das tabelas...')
# Índices para TB_USUARIO
cursor.execute('''
    CREATE INDEX IF NOT EXISTS idx_nome_usuario ON TB_USUARIO (NOME_USUARIO)
''')

# Índices para TB_CLIENTE
cursor.execute('''
    CREATE INDEX IF NOT EXISTS idx_nome_cliente ON TB_CLIENTE (NOME_CLIENTE)
''')
cursor.execute('''
    CREATE INDEX IF NOT EXISTS idx_email_cliente ON TB_CLIENTE (EMAIL_CLIENTE)
''')

# Índices para TB_FORNECEDOR
cursor.execute('''
    CREATE INDEX IF NOT EXISTS idx_nome_fornecedor ON TB_FORNECEDOR (NOME_FORNECEDOR)
''')
cursor.execute('''
    CREATE INDEX IF NOT EXISTS idx_email_fornecedor ON TB_FORNECEDOR (EMAIL_FORNECEDOR)
''')

# Índices para TB_CATEGORIAS
cursor.execute('''
    CREATE INDEX IF NOT EXISTS idx_nome_categoria ON TB_CATEGORIAS (NOME_CATEGORIA)
''')

# Índices para TB_PRODUTO
cursor.execute('''
    CREATE INDEX IF NOT EXISTS idx_nome_produto ON TB_PRODUTO (NOME_PRODUTO)
''')

# Índices para TB_CONTA_A_PAGAR
cursor.execute('''
    CREATE INDEX IF NOT EXISTS idx_id_fornecedor_conta_pagar ON TB_CONTA_A_PAGAR (ID_FORNECEDOR)
''')

# Índices para TB_CONTA_A_RECEBER
cursor.execute('''
    CREATE INDEX IF NOT EXISTS idx_id_cliente_conta_receber ON TB_CONTA_A_RECEBER (ID_CLIENTE)
''')

# Índices para TB_FLUXO_DE_CAIXA
cursor.execute('''
    CREATE INDEX IF NOT EXISTS idx_data_movimento_fluxo ON TB_FLUXO_DE_CAIXA (DATA_FLUXO_DE_CAIXA)
''')

# Índices para TB_FUNCIONARIO
cursor.execute('''
    CREATE INDEX IF NOT EXISTS idx_nome_funcionario ON TB_FUNCIONARIO (NOME_FUNCIONARIO)
''')
print("sucesso...")
# Commit as mudanças
conn.commit()

# Fechar a conexão
conn.close()