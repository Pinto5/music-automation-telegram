import mysql.connector

def create_database(MYSQL_PW):
    connection = mysql.connector.connect(
        host = "localhost",
        user = "root",
        password = MYSQL_PW
    )

    cursor = connection.cursor()

    cursor.execute("""
        CREATE DATABASE IF NOT EXISTS music_bot
        CHARACTER SET utf8mb4
        COLLATE utf8mb4_unicode_ci
    """ 
    # CHARACTER SET utf8mb4 : necessário para a db aceitar vários caracteres
    # COLLATE utf8mb4_unicode_ci : para não diferenciar letras maiúsculas e minúsculas
    )

    cursor.close()
    connection.close()
