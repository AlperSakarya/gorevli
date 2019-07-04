import os
import sqlite3
from sqlite3 import Error
import boto3
from boto3.dynamodb.conditions import Key, Attr
from auth import AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY

# Creating DynamoDB table as a resource
dynamodb = boto3.resource('dynamodb', aws_access_key_id=AWS_ACCESS_KEY_ID, aws_secret_access_key=AWS_SECRET_ACCESS_KEY)
table = dynamodb.Table('gorevli') # Pass your Dynamo table name here


# DB Functions will be listed here. Moving local mysqli file to Dynamo
# SQL query to save a new member in to the newsletter table


def dynamo_cus_comm_save(members):
    table.put_item(
        Item={
            'name': members[0],
            'phone': members[1],
            'email': members[2],
            'state': members[3]
        }
    )


def dynamo_select_all_members(member_email):
    response = table.query(
        KeyConditionExpression=Key('email').eq(member_email)
    )
    items = response['Items']
    if not items:
        result = False
    else:
        result = True
    return result


# SQL query to save new newsletter signup into existing donating customer's row
def dynamo_cus_name_phone_save(members):
    response = table.update_item(
        Key={
            'email': members[2]
        },
        UpdateExpression='set #nm = :val1, phone = :val2, #st = :val3',
        ExpressionAttributeValues={
            ':val1': (members[0]),
            ':val2': (members[1]),
            ':val3': (members[3])
        },
        ExpressionAttributeNames={
            "#nm": "name",
            "#st": "state"
            }
    )


# SQL query to pull all the members to display in SMS panel
def dynamo_get_members():
    response = table.scan()
    return response


# SQL query to delete selected member from the SMS DB
def dynamo_delete_comm_member(email):
    response = table.delete_item(
        Key={'email': email}
    )

#######################################################


# OLD mysqli DB FUNCTIONS


# Initial DB check/create statement. Creates the DB if it's not there. If exist does not touch.
def check_create_db():
    data_path = './database/'
    filename = 'member-db'
    if os.path.isdir("./database") is not True:
        os.makedirs(data_path)
    db = sqlite3.connect(data_path + filename + '.sqlite3')
    db.execute('CREATE TABLE IF NOT EXISTS members (id INTEGER PRIMARY KEY, cus_id VARCHAR, name VARCHAR, '
               'phone INT, email VARCHAR UNIQUE, state VARCHAR)')
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
    cur.execute(('SELECT * FROM members WHERE email=? and cus_id is not NULL '), (member_email,))
    rows = cur.fetchall()
    if len(rows) == 0:
        return False
    else:
        return rows[0][1]


# DB query to save the newly created Stripe customer ID in to the DB for future charges so that charges can be tracked
def cus_id_save(conn, members):
    sql = ''' INSERT INTO members(cus_id, name, phone, email, state) VALUES (?, ?, ?, ?, ?)'''
    cur = conn.cursor()
    cur.execute(sql, members)
    return cur.lastrowid


# SQL query to save a new member in to the newsletter table
def cus_comm_save(conn, members):
    sql = ''' INSERT INTO members(name, phone, email, state) VALUES (?, ?, ?, ?)'''
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


# SQL query to delete selected member from the SMS DB
def delete_comm_member(conn, email):
    cur = conn.cursor()
    cur.execute(('DELETE FROM members WHERE email=?'), (email,))

