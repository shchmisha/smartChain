import sqlite3


class Database:
    # init is called when an object is created

    def __init__(self, db):
        self.connection = sqlite3.connect(db)
        self.cursor = self.connection.cursor()
        self.cursor.execute("CREATE TABLE IF NOT EXISTS wallet (privateKey text, cipherKey text)")
        self.connection.commit()

    def insert(self, privateKey, cipherKey):
        self.cursor.execute("INSERT INTO wallet VALUES (?, ?)", (privateKey, cipherKey))
        self.connection.commit()

    # def getData(self):
    #     self.cursor.execute("SELECT * FROM wallet")

    def getData(self):
        self.cursor.execute("SELECT * FROM wallet")
        rows = self.cursor.fetchall()
        return rows

    def __del__(self):
        self.connection.close()


if __name__ == '__main__':
    database = Database("wallet.db")
    database.insert("priv", "key")
    print(database.getData())
