# database.py

import sqlite3

def init_db():
    conn = sqlite3.connect('library.db')
    cur = conn.cursor()

    cur.execute('''CREATE TABLE IF NOT EXISTS books (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    author TEXT NOT NULL,
                    year INTEGER,
                    inventory_number TEXT UNIQUE NOT NULL,
                    quantity INTEGER NOT NULL DEFAULT 1)''')

    cur.execute('''CREATE TABLE IF NOT EXISTS readers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    telegram_id INTEGER UNIQUE NOT NULL,
                    name TEXT NOT NULL,
                    group_department TEXT NOT NULL)''')

    cur.execute('''CREATE TABLE IF NOT EXISTS loans (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    book_id INTEGER,
                    reader_id INTEGER,
                    issue_date TEXT NOT NULL,
                    return_date TEXT,
                    FOREIGN KEY(book_id) REFERENCES books(id),
                    FOREIGN KEY(reader_id) REFERENCES readers(id))''')

    conn.commit()
    conn.close()

init_db()
#конец