import sqlite3
import os

# Define database path
db_path = './sql_db/Entry.db'

# Remove the database if it already exists to create a fresh one (for setup purposes)
if os.path.exists(db_path):
    os.remove(db_path)

# Connect to the database
conn = sqlite3.connect(db_path)
cur = conn.cursor()

# Create Entry table
try:
    cur.execute('''CREATE TABLE Entry (
                    EntryId INTEGER PRIMARY KEY AUTOINCREMENT,
                    User_ID INTEGER NOT NULL,
                    NameOfBakingItem TEXT NOT NULL,
                    NumExcellentVotes INTEGER NOT NULL,
                    NumOkVotes INTEGER NOT NULL,
                    NumBadVotes INTEGER NOT NULL,
                    FOREIGN KEY(User_ID) REFERENCES People(User_ID)
                );''')
    print("Entry table created successfully.")
except sqlite3.Error as e:
    print(f"Error creating table: {e}")

# Sample data to insert into the Entry table
entries = [
    (1, 'Sugar Cookies', 1, 3, 2),
    (2, 'Chocolate Cake', 1, 2, 4),
    (3, 'Brownies', 4, 3, 1),
    (1, 'Apple Pie', 3, 3, 1)
]

# Insert sample data
try:
    cur.executemany('''INSERT INTO Entry (User_ID, NameOfBakingItem, NumExcellentVotes, NumOkVotes, NumBadVotes) 
                       VALUES (?, ?, ?, ?, ?);''', entries)
    conn.commit()
    print("Sample data inserted into Entry table.")
except sqlite3.Error as e:
    print(f"Error inserting data: {e}")
finally:
    # Display the inserted data
    cur.execute('SELECT * FROM Entry;')
    rows = cur.fetchall()
    for row in rows:
        print(row)

# Close the connection
conn.close()
print("Database connection closed.")
