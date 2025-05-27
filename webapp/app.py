from flask import Flask, render_template, request, jsonify
import sqlite3
import os

app = Flask(__name__, template_folder="templates", static_folder="static")

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/books")
def get_books():
    conn = sqlite3.connect('../library.db')
    cur = conn.cursor()
    cur.execute("SELECT id, title, author, year, inventory_number FROM books WHERE quantity > 0")
    books = cur.fetchall()
    return jsonify([{
        "id": b[0],
        "title": b[1],
        "author": b[2],
        "year": b[3],
        "inventory": b[4]
    } for b in books])

@app.route("/search")
def search_books():
    query = request.args.get("q", "").strip().lower()
    conn = sqlite3.connect('../library.db')
    cur = conn.cursor()
    cur.execute("SELECT id, title, author, year, inventory_number FROM books WHERE LOWER(title) LIKE ? OR LOWER(author) LIKE ?",
                (f"%{query}%", f"%{query}%"))
    books = cur.fetchall()
    return jsonify([{
        "id": b[0],
        "title": b[1],
        "author": b[2],
        "year": b[3],
        "inventory": b[4]
    } for b in books])

if __name__ == "__main__":
    os.makedirs("static", exist_ok=True)
    app.run(port=5000)