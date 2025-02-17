import sqlite3

class Database:
    # init is called when an object is created

    def __init__(self, db):
        self.connection = sqlite3.connect(db)
        self.cursor = self.connection.cursor()
        self.cursor.execute("CREATE TABLE IF NOT EXISTS keys (chain_key text, chain_name text)")
        self.connection.commit()

    def insert(self, chain_key, chain_name):
        self.cursor.execute("INSERT INTO keys VALUES (?,?)", (chain_key, chain_name))
        self.connection.commit()

    # def getData(self):
    #     self.cursor.execute("SELECT * FROM wallet")

    def getData(self):
        self.cursor.execute("SELECT * FROM keys")
        rows = self.cursor.fetchall()
        return rows

    def __del__(self):
        self.connection.close()

if __name__ == '__main__':
    database = Database("wallet.db")
    database.insert("priv", "key")
    print(database.getData())

