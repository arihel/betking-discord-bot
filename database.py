import sqlite3

# Conexão com o Banco de Dados SQLite
conexao = sqlite3.connect('cassino.db')
cursor = conexao.cursor()

# Cria as tabelas estruturadas caso não existam
cursor.execute('''CREATE TABLE IF NOT EXISTS usuarios (id INTEGER PRIMARY KEY, saldo INTEGER)''')
cursor.execute('''CREATE TABLE IF NOT EXISTS eventos (id INTEGER PRIMARY KEY AUTOINCREMENT, titulo TEXT, opcao_a TEXT, opcao_b TEXT, status TEXT)''')
cursor.execute('''CREATE TABLE IF NOT EXISTS apostas (id INTEGER PRIMARY KEY AUTOINCREMENT, evento_id INTEGER, usuario_id INTEGER, opcao TEXT, valor INTEGER)''')
conexao.commit()