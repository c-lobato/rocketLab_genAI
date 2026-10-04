import sqlite3

#EXTRAÇÃO DOS SCHEMAS DO BANCO DE DADOS
conn = sqlite3.connect("cinerocket_database.db")
cursor = conn.cursor()
cursor.execute("SELECT sql FROM sqlite_master WHERE type='table';") #query bara buscar todas as tabelas presente no banco 
schemas = cursor.fetchall()

#loop for para imprimir a quantidade de schemas encontrados
for schema in schemas:
    print(schema[0] + "\n")