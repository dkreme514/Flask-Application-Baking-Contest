import sqlite3
import os

# Define database path
db_path = './sql_db/ContestantsDB.db'

# Remove the database if it already exists to create a fresh one (for setup purposes)
if os.path.exists(db_path):
    os.remove(db_path)

# Connect to the database
conn = sqlite3.connect(db_path)
cur = conn.cursor()

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
    print(f"Error creating table: {e}")

# Sample data to insert into the People table
contestants = [
    ('DNukem', 32, '556-564-4415', 2, 'test123'),
    ('TDoe', 26, '598-587-3249', 1, 'test123'),
    ('GRamsey', 29, '994-264-8851', 3, 'test123'),
    ('DSmith', 40, '614-581-3496', 1, 'test123')
]

# Insert sample data
try:
    cur.executemany('''INSERT INTO People (Name, Age, PhoneNumber, SecurityLevel, Password) 
                       VALUES (?, ?, ?, ?, ?);''', contestants)
    conn.commit()
    print("Sample data inserted into People table.")
except sqlite3.Error as e:
    print(f"Error inserting data: {e}")
finally:
    # Display the inserted data
    cur.execute('SELECT * FROM People;')
    rows = cur.fetchall()
    for row in rows:
        print(row)

# Close the connection
conn.close()
print("Database connection closed.")
