import os
import sqlite3

dir_path = os.path.dirname(os.path.realpath(__file__))

def add_entry(name, os, packages, date):
    conn = sqlite3.connect('{}/database.db'.format(dir_path))
    c = conn.cursor()
    c.execute('''INSERT INTO images
                 VALUES (?, ?, ?, ?)''', (name, os, packages, date))
    conn.commit()
    conn.close()

def remove_entry(name):
    conn = sqlite3.connect('{}/database.db'.format(dir_path))
    c = conn.cursor()
    c.execute('''DELETE FROM images
                 WHERE name = ?''', (name,))
    conn.commit()
    conn.close()

def read_entry(name):
    conn = sqlite3.connect('{}/database.db'.format(dir_path))
    c = conn.cursor()
    c.execute('''SELECT * FROM Images
                 WHERE name = ?''', (name,))
    result = c.fetchone()
    conn.close()
    return result

def read_all_entries():
    conn = sqlite3.connect('{}/database.db'.format(dir_path))
    c = conn.cursor()
    c.execute('''SELECT * FROM Images''')
    result = c.fetchall()
    conn.close()
    return result

def modify_entry(name, os, packages, date):
    conn = sqlite3.connect('{}/database.db'.format(dir_path))
    c = conn.cursor()
    c.execute('''UPDATE Images
                 SET os = ?, packages = ?, date = ?
                 WHERE name = ?''', (os, packages, date, name))
    conn.commit()
    conn.close()
