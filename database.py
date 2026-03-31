import sqlite3

# O timeout=20 impede o erro "database is locked" em momentos de pico
conexao = sqlite3.connect('cassino.db', timeout=20)
cursor = conexao.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS usuarios (
        id INTEGER PRIMARY KEY,
        saldo INTEGER DEFAULT 1000,
        last_daily INTEGER DEFAULT 0
    )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS eventos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        titulo TEXT,
        opcao_a TEXT,
        opcao_b TEXT,
        status TEXT DEFAULT 'aberto',
        resultado TEXT,
        api_id INTEGER UNIQUE,
        data_hora INTEGER 
    )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS apostas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        usuario_id INTEGER,
        evento_id INTEGER,
        escolha TEXT,
        valor INTEGER
    )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS configuracoes (
        guild_id INTEGER PRIMARY KEY, 
        canal_id INTEGER
    )
''')

conexao.commit()