import os
import sqlite3
from sqlite3 import Error


# Initial DB check/create statement. Creates the DB if it's not there. If exist does not touch.
def check_create_db():
    data_path = './database/'
    filename = 'member-db'
    if os.path.isdir("./database") is not True:
        os.makedirs(data_path)
    db = sqlite3.connect(data_path + filename + '.sqlite3')
    db.execute('CREATE TABLE IF NOT EXISTS members (id INTEGER PRIMARY KEY, cus_id VARCHAR, name VARCHAR, '
               'phone INT, email VARCHAR UNIQUE)')
    db.close()


# Create a database connection to the SQLite database specified by the db_file
def create_connection(db_file):
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Error as e:
        print(e)

    return None


# SQL query to check if the unique user email exist in the DB or not
def select_all_members(conn, member_email):
    cur = conn.cursor()
    cur.execute(('SELECT * FROM members WHERE email=?'), (member_email,))
    rows = cur.fetchall()
    if len(rows) == 0:
        return False
    else:
        return rows[0][1]


# DB query to save the newly created Stripe customer ID in to the DB for future charges so that charges can be tracked
def cus_id_save(conn, members):
    sql = ''' INSERT INTO members(cus_id, email) VALUES (?, ?)'''
    cur = conn.cursor()
    cur.execute(sql, members)
    return cur.lastrowid


# SQL query to save a new member in to the newsletter table
def cus_comm_save(conn, members):
    sql = ''' INSERT INTO members(name, phone, email) VALUES (?, ?, ?)'''
    cur = conn.cursor()
    cur.execute(sql, members)
    return cur.lastrowid


# SQL query to save new newsletter signup into existing donating customer's row
def cus_name_phone_save(conn, members):
    cur = conn.cursor()
    cur.execute('UPDATE members SET name =?, phone =?  WHERE email =?', members)
    return cur.lastrowid


# SQL query that adds stripe ID into existing customer with same email
def cus_id_add(conn, member):
    cur = conn.cursor()
    cur.execute('UPDATE members SET cus_id =? WHERE email =?', member)
    return cur.lastrowid


# SQL query to pull phone numbers for SMS
def get_member_phones(conn):
    cur = conn.cursor()
    cur.execute('SELECT phone FROM members WHERE phone IS NOT NULL')
    rows = cur.fetchall()
    if len(rows) == 0:
        return False
    else:
        return rows


# SQL query to pull all the members to display in SMS panel
def get_members(conn):
    cur = conn.cursor()
    cur.execute('SELECT * FROM members WHERE phone IS NOT NULL')
    rows = cur.fetchall()
    if len(rows) == 0:
        return False
    else:
        return rows