import sqlite3


class SQLiteManager(object):
    def __init__(self, db_name):
        self.db = sqlite3.connect(db_name)
        self.cursor = self.db.cursor()

    def create_or_drop_table(self, command):
        self.cursor.execute(command)
        self.db.commit()

    def insert_data(self, command):
        self.cursor.execute(command)

    def select_data(self, db_name, arg1, arg2):
        query = "SELECT * FROM {} WHERE username = ? AND password =?".format(db_name)
        self.cursor.execute(query, [ (arg1), (arg2)])
        results = self.cursor.fetchall()
        return results

    def close_connection_to_db(self):
        self.db.close()



if __name__ == "__main__":
    sql_object = SQLiteManager("users.db")
    sql_object.create_or_drop_table("CREATE TABLE users(id INTEGER PRIMARY KEY, name TEXT, password TEXT)")
    sql_object.close_connection_to_db()