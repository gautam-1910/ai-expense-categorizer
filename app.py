import sqlite3
import re
from flask import Flask, render_template, request
from datetime import datetime

app = Flask(__name__)
DB_NAME = "expenses.db"
def init_db():
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            description TEXT NOT NULL,
            amount REAL NOT NULL,
            category TEXT NOT NULL,
            date_created DATETIME DEFAULT CURRENT_TIMESTAMP
        )
        """
    )
    conn.commit()
    conn.close()
def extract_amount(text):
    match = re.search(r"[\d,]+\.?\d*", text)
    if not match:
        return 0.0
    value = match.group(0).replace(",", "")
    return float(value)
CATEGORIES = {
    "Food": ["food", "biriyani", "biryani", "pizza", "chicken", "restaurant"],
    "Shopping": ["jersey", "shirt", "dress", "amazon", "flipkart", "mall"],
    "Travel": ["bus", "train", "uber", "ola", "taxi", "flight", "fuel"],
    "Bills": ["bill", "electricity", "rent", "internet", "recharge"],
    "Entertainment": ["movie", "netflix", "spotify", "game", "cinema"],
}

def infer_category(text):
    t = text.lower()
    for cat, keywords in CATEGORIES.items():
        if any(k in t for k in keywords):
            return cat
    return "Others"


@app.route("/", methods=["GET", "POST"])
def index():
    message = ""

    if request.method == "POST":
        desc = request.form["description"]
        amount = extract_amount(desc)
        category = infer_category(desc)

        conn = sqlite3.connect(DB_NAME)
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO expenses (description, amount, category) VALUES (?, ?, ?)",
            (desc, amount, category),
        )
        conn.commit()
        conn.close()
        message = "Expense saved!"

    # fetch recent expenses
    conn = sqlite3.connect(DB_NAME)
    cur = conn.cursor()
    cur.execute(
        "SELECT description, amount, category, date_created "
        "FROM expenses ORDER BY id DESC LIMIT 10"
    )
    recent = cur.fetchall()
    conn.close()

    return render_template("index.html", message=message, recent=recent)
if __name__ == "__main__":
    init_db()
    app.run(debug=True)
