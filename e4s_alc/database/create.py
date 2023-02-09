import os
import sqlite3

# Connect to the database 
dir_path = os.path.dirname(os.path.realpath(__file__))
conn = sqlite3.connect('{}/database.db'.format(dir_path))

# Create a cursor 
cursor = conn.cursor()

# Create the table
cursor.execute('''
    CREATE TABLE IF NOT EXISTS images (
        name TEXT, 
        OS TEXT,
        packages TEXT, 
        date TEXT
    )'''
)

# Commit the changes 
conn.commit()

# Close the connection
conn.close()
