import sqlite3

connection = sqlite3.connect('trade_information.db', check_same_thread=False)
cursor = connection.cursor()

cursor.execute(
    """INSERT INTO user(
        username,
        password,
        current_balance
        ) VALUES(
        "cen",
        "06",
        "1000.00"
    );"""
)

connection.commit()
cursor.close()
connection.close()
