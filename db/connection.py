import mysql.connector

def connect_database(MYSQL_PW):
    return mysql.connector.connect(
        host = "localhost",
        user = "root",
        password = MYSQL_PW,
        database = "music_bot"
    )


def create_tables(MYSQL_PW):
    connection = connect_database(MYSQL_PW)
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INT AUTO_INCREMENT PRIMARY KEY,
            telegram_user_id BIGINT NOT NULL UNIQUE,
            username VARCHAR(255),
            chat_id BIGINT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS interactions (
            id INT AUTO_INCREMENT PRIMARY KEY,
            interaction_id BIGINT,
            telegram_user_id BIGINT,
            chat_id BIGINT,
            sender_type VARCHAR(20) NOT NULL,
            message_text TEXT,
            message_link TEXT,
            state_type VARCHAR(50),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (telegram_user_id)
                REFERENCES users(telegram_user_id)
        )
    """)

    connection.commit()
    cursor.close()
    connection.close()