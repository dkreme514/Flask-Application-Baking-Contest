import sqlite3
import os

# Define database path
db_path = './sql_db/Datab.db'

# Remove the database if it already exists to create a fresh one (for setup purposes)
if os.path.exists(db_path):
    os.remove(db_path)

# Connect to the database
conn = sqlite3.connect(db_path)
cur = conn.cursor()

# Enable foreign key support
cur.execute('PRAGMA foreign_keys = ON;')

# Create People table
try:
    cur.execute('''CREATE TABLE People (
                    User_ID INTEGER PRIMARY KEY AUTOINCREMENT,
                    Name TEXT NOT NULL,
                    Age INTEGER NOT NULL,
                    PhoneNumber TEXT NOT NULL,
                    SecurityLevel INTEGER NOT NULL,
                    Password TEXT NOT NULL
                );''')
    print("People table created successfully.")
except sqlite3.Error as e:
    print(f"Error creating People table: {e}")

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
    print(f"Error creating Entry table: {e}")

# Insert sample data into People table
contestants = [
    ('DNukem', 32, '556-564-4415', 2, 'test123'),
    ('TDoe', 26, '598-587-3249', 1, 'test123'),
    ('GRamsey', 29, '994-264-8851', 3, 'test123'),
    ('DSmith', 40, '614-581-3496', 1, 'test123')
]

try:
    cur.executemany('''INSERT INTO People (Name, Age, PhoneNumber, SecurityLevel, Password) 
                       VALUES (?, ?, ?, ?, ?);''', contestants)
    conn.commit()
    print("Sample data inserted into People table.")
except sqlite3.Error as e:
    print(f"Error inserting data into People table: {e}")

# Insert sample data into Entry table
entries = [
    (1, 'Sugar Cookies', 1, 3, 2),
    (2, 'Chocolate Cake', 1, 2, 4),
    (3, 'Brownies', 4, 3, 1),
    (1, 'Apple Pie', 3, 3, 1)
]

try:
    cur.executemany('''INSERT INTO Entry (User_ID, NameOfBakingItem, NumExcellentVotes, NumOkVotes, NumBadVotes) 
                       VALUES (?, ?, ?, ?, ?);''', entries)
    conn.commit()
    print("Sample data inserted into Entry table.")
except sqlite3.Error as e:
    print(f"Error inserting data into Entry table: {e}")

# Display the inserted data for verification
try:
    cur.execute('''
        SELECT People.Name, Entry.NameOfBakingItem, Entry.NumExcellentVotes, Entry.NumOkVotes, Entry.NumBadVotes
        FROM Entry
        INNER JOIN People ON Entry.User_ID = People.User_ID;
    ''')
    rows = cur.fetchall()
    for row in rows:
        print(row)
except sqlite3.Error as e:
    print(f"Error displaying data: {e}")

# Close the connection
conn.close()
print("Database connection closed.")
