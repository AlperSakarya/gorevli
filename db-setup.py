import os, sqlite3
def check_create_db():
    data_path = './database/'
    filename = 'member-db'
    if os.path.isdir("./database") != True:
        os.makedirs(data_path)
    db = sqlite3.connect(data_path + filename + '.sqlite3')
    db.execute('CREATE TABLE IF NOT EXISTS members (id INTEGER PRIMARY KEY, cus_id VARCHAR, name VARCHAR, phone INT, email VARCHAR)')
    db.close()
check_create_db()