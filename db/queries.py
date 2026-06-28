from db.connection import connect_database

def insert_data_users(MYSQL_PW, telegram_user_id, username, chat_id):
    connection = connect_database(MYSQL_PW)
    cursor = connection.cursor()

    sql = """
    INSERT INTO users (telegram_user_id, username, chat_id)
    VALUES (%s, %s, %s)
    ON DUPLICATE KEY UPDATE
        username = VALUES(username),
        chat_id = VALUES(chat_id)
    """
    cursor.execute(sql, (telegram_user_id, username, chat_id))
    connection.commit()

    cursor.close()
    connection.close()

def insert_data_interactions(MYSQL_PW, interaction_id, telegram_user_id, chat_id, sender_type, message_text, message_link, state_type):
    connection = connect_database(MYSQL_PW)
    cursor = connection.cursor()

    sql = """
    INSERT INTO interactions (interaction_id, telegram_user_id, chat_id, sender_type, message_text, message_link, state_type)
    VALUES (%s, %s, %s, %s, %s, %s, %s)
    """

    cursor.execute(sql, (interaction_id, telegram_user_id, chat_id, sender_type, message_text, message_link, state_type))
    connection.commit()

    cursor.close()
    connection.close()

def user_exists(MYSQL_PW, telegram_user_id):
    connection = connect_database(MYSQL_PW)
    cursor = connection.cursor()

    sql = "SELECT 1 FROM users WHERE telegram_user_id = %s LIMIT 1"

    cursor.execute(sql, (telegram_user_id, ))

    exists = cursor.fetchone() is not None # Procura apenas 1 linha (True or False)

    cursor.close()
    connection.close()

    return exists