import sqlite3
from datetime import datetime
from flask import Flask, render_template, request, redirect

DB_PATH = "expenses.db"

app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True


def init_db():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            description TEXT NOT NULL,
            amount REAL NOT NULL,
            category TEXT NOT NULL,
            created_at TEXT NOT NULL
        )
        """
    )
    conn.commit()
    conn.close()


def get_recent_expenses(limit=10):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        "SELECT id, description, amount, category, created_at "
        "FROM expenses ORDER BY created_at DESC LIMIT ?",
        (limit,),
    )
    rows = cur.fetchall()
    conn.close()
    return rows


def get_monthly_summary():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute(
        """
        SELECT category, SUM(amount)
        FROM expenses
        WHERE strftime('%Y-%m', created_at) = strftime('%Y-%m', 'now')
        GROUP BY category
        """
    )
    data = cur.fetchall()
    conn.close()

    category_totals = {row[0]: row[1] for row in data}
    overall_total = sum(category_totals.values())
    return category_totals, overall_total


def categorize(description):
    """Rule-based categorizer that works for both full sentences and single words."""
    text = description.lower()

    # Food & drinks
    if any(
        w in text
        for w in [
            "biryani",
            "biriyani",
            "cappuccino",
            "coffee",
            "tea",
            "kuzhimandhi",
            "lunch",
            "dinner",
            "meal",
            "food",
            "pizza",
            "burger",
            "snack",
        ]
    ):
        return "Food"

    # Bills & utilities
    if any(
        w in text
        for w in [
            "recharge",
            "electricity",
            "mobile bill",
            "wifi",
            "internet",
            "water bill",
            "gas bill",
            "bill",
        ]
    ):
        return "Bills"

    # Transport
    if any(
        w in text
        for w in [
            "uber",
            "ola",
            "rapido",
            "flight",
            "bus",
            "train",
            "metro",
            "auto",
            "cab",
            "taxi",
            "petrol",
            "diesel",
            "fuel",
        ]
    ):
        return "Transport"

    # Shopping
    if any(
        w in text
        for w in [
            "jersey",
            "shirt",
            "socks",
            "clothes",
            "dress",
            "pants",
            "shoes",
            "shopping",
            "amazon",
            "flipkart",
            "bag",
            "watch",
        ]
    ):
        return "Shopping"

    # Rent / housing
    if any(w in text for w in ["rent", "maintenance", "hostel", "pg", "room rent"]):
        return "Rent"

    # Entertainment
    if any(
        w in text
        for w in [
            "movie",
            "netflix",
            "spotify",
            "hotstar",
            "subscription",
            "prime video",
            "game",
            "gaming",
        ]
    ):
        return "Entertainment"

    # Health
    if any(
        w in text
        for w in [
            "doctor",
            "hospital",
            "medicine",
            "pharmacy",
            "chemist",
            "medical",
            "tablet",
        ]
    ):
        return "Health"

    # Education
    if any(
        w in text
        for w in ["course", "udemy", "coursera", "books", "tuition", "coaching", "exam"]
    ):
        return "Education"

    return "Other"


@app.route("/", methods=["GET", "POST"])
def index():
    message = None

    if request.method == "POST":
        form_type = request.form.get("form_type")

        if form_type == "text":
            description = request.form.get("description", "").strip()
            if description:
                # Simple amount extraction from free text
                amount = 0.0
                for token in description.split():
                    try:
                        amount = float(token)
                        break
                    except ValueError:
                        continue

                category = categorize(description)
                created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                conn = sqlite3.connect(DB_PATH)
                cur = conn.cursor()
                cur.execute(
                    "INSERT INTO expenses (description, amount, category, created_at) "
                    "VALUES (?, ?, ?, ?)",
                    (description, amount, category, created_at),
                )
                conn.commit()
                conn.close()
                message = "Expense saved!"

        elif form_type == "structured":
            amount = request.form.get("amount", "").strip()
            item = request.form.get("item", "").strip()
            if amount and item:
                amount_val = float(amount)
                description = item  # same text is categorized and stored
                category = categorize(description)
                created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                conn = sqlite3.connect(DB_PATH)
                cur = conn.cursor()
                cur.execute(
                    "INSERT INTO expenses (description, amount, category, created_at) "
                    "VALUES (?, ?, ?, ?)",
                    (description, amount_val, category, created_at),
                )
                conn.commit()
                conn.close()
                message = "Expense saved!"

    recent = get_recent_expenses()
    category_totals, overall_total = get_monthly_summary()

    return render_template(
        "index.html",
        recent=recent,
        category_totals=category_totals,
        overall_total=overall_total,
        message=message,
    )


@app.route("/delete/<int:expense_id>", methods=["POST"])
def delete_expense(expense_id):
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("DELETE FROM expenses WHERE id = ?", (expense_id,))
    conn.commit()
    conn.close()
    return redirect("/")


if __name__ == "__main__":
    init_db()
    app.run(debug=True)
