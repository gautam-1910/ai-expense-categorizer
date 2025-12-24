import sqlite3
from datetime import datetime
from flask import (
    Flask, render_template, request, redirect,
    url_for, session
)
from werkzeug.security import generate_password_hash, check_password_hash


DB_PATH = "expenses.db"

app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.secret_key = "change-this-secret-key"  # replace with a better secret


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    cur = conn.cursor()

    # Users table: now email instead of username
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL
        )
        """
    )

    # Expenses table, tied to a user
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            description TEXT NOT NULL,
            amount REAL NOT NULL,
            category TEXT NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
        """
    )

    conn.commit()
    conn.close()


# ---------- Helpers ----------

def get_current_user():
    user_id = session.get("user_id")
    if not user_id:
        return None
    conn = get_db()
    cur = conn.cursor()
    # use email column
    cur.execute("SELECT id, email FROM users WHERE id = ?", (user_id,))
    row = cur.fetchone()
    conn.close()
    return row


def login_required(view_func):
    def wrapped(*args, **kwargs):
        if not session.get("user_id"):
            return redirect(url_for("login"))
        return view_func(*args, **kwargs)
    wrapped.__name__ = view_func.__name__
    return wrapped


def get_recent_expenses(user_id, limit=10):
    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT id, description, amount, category, created_at
        FROM expenses
        WHERE user_id = ?
        ORDER BY created_at DESC
        LIMIT ?
        """,
        (user_id, limit),
    )
    rows = cur.fetchall()
    conn.close()
    return rows


def get_monthly_summary(user_id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT category, SUM(amount)
        FROM expenses
        WHERE user_id = ?
          AND strftime('%Y-%m', created_at) = strftime('%Y-%m', 'now')
        GROUP BY category
        """,
        (user_id,),
    )
    data = cur.fetchall()
    conn.close()
    category_totals = {row[0]: row[1] for row in data}
    overall_total = sum(category_totals.values())
    return category_totals, overall_total


def categorize(description):
    text = description.lower()

    # Food & drinks
    if any(
        w in text
        for w in [
            "biryani", "biriyani", "cappuccino", "coffee", "tea","kuzhimandhi",
            "lunch", "dinner", "meal", "food", "pizza", "burger", "snack",
        ]
    ):
        return "Food"

    # Bills & utilities
    if any(
        w in text
        for w in [
            "recharge", "electricity", "mobile bill", "wifi", "internet",
            "water bill", "gas bill", "bill",
        ]
    ):
        return "Bills"

    # Transport
    if any(
        w in text
        for w in [
            "uber", "ola", "rapido", "bus", "train", "metro", "auto",
            "cab", "taxi", "petrol", "diesel", "fuel",
        ]
    ):
        return "Transport"

    # Shopping
    if any(
        w in text
        for w in [
            "jersey", "shirt", "socks", "clothes", "dress", "pants",
            "shoes", "shopping", "amazon", "flipkart", "bag", "watch",
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
            "movie", "netflix", "spotify", "hotstar", "subscription",
            "prime video", "game", "gaming",
        ]
    ):
        return "Entertainment"

    # Health
    if any(
        w in text
        for w in [
            "doctor", "hospital", "medicine", "pharmacy", "chemist",
            "medical", "tablet",
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


# ---------- Auth routes ----------

@app.route("/register", methods=["GET", "POST"])
def register():
    error = None
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "").strip()

        if not email or not password:
            error = "Email and password are required."
        else:
            conn = get_db()
            cur = conn.cursor()
            cur.execute("SELECT id FROM users WHERE email = ?", (email,))
            if cur.fetchone():
                error = "Email already registered."
            else:
                pw_hash = generate_password_hash(password)
                cur.execute(
                    "INSERT INTO users (email, password_hash) VALUES (?, ?)",
                    (email, pw_hash),
                )
                conn.commit()
                conn.close()
                return redirect(url_for("login"))
            conn.close()

    return render_template("register.html", error=error)


@app.route("/login", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "").strip()

        conn = get_db()
        cur = conn.cursor()
        cur.execute(
            "SELECT id, password_hash FROM users WHERE email = ?",
            (email,),
        )
        row = cur.fetchone()
        conn.close()

        if row and check_password_hash(row["password_hash"], password):
            session["user_id"] = row["id"]
            return redirect(url_for("index"))
        else:
            error = "Invalid email or password."

    return render_template("login.html", error=error)


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


# ---------- Main expense routes ----------

@app.route("/", methods=["GET", "POST"])
@login_required
def index():
    message = None
    error = None
    user = get_current_user()
    user_id = user["id"]

    if request.method == "POST":
        form_type = request.form.get("form_type")

        if form_type == "text":
            description = request.form.get("description", "").strip()
            if not description:
                error = "Please enter a description for the expense."
            else:
                amount = None
                for token in description.split():
                    try:
                        value = float(token)
                        if value > 0:
                            amount = value
                            break
                    except ValueError:
                        continue

                if amount is None:
                    error = "Please include a positive amount in the description."
                else:
                    category = categorize(description)
                    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                    conn = get_db()
                    cur = conn.cursor()
                    cur.execute(
                        """
                        INSERT INTO expenses (user_id, description, amount, category, created_at)
                        VALUES (?, ?, ?, ?, ?)
                        """,
                        (user_id, description, amount, category, created_at),
                    )
                    conn.commit()
                    conn.close()
                    message = "Expense saved!"

        elif form_type == "structured":
            amount_raw = request.form.get("amount", "").strip()
            item = request.form.get("item", "").strip()
            category_override = request.form.get("category_override", "").strip()

            if not amount_raw or not item:
                error = "Please provide both amount and item."
            else:
                try:
                    amount_val = float(amount_raw)
                    if amount_val <= 0:
                        error = "Amount must be greater than zero."
                except ValueError:
                    error = "Amount must be a valid number."

            if not error:
                description = item
                category = category_override or categorize(description)
                created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                conn = get_db()
                cur = conn.cursor()
                cur.execute(
                    """
                    INSERT INTO expenses (user_id, description, amount, category, created_at)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (user_id, description, amount_val, category, created_at),
                )
                conn.commit()
                conn.close()
                message = "Expense saved!"

    recent = get_recent_expenses(user_id)
    category_totals, overall_total = get_monthly_summary(user_id)

    return render_template(
        "index.html",
        recent=recent,
        category_totals=category_totals,
        overall_total=overall_total,
        message=message,
        error=error,
        user=user,
    )


@app.route("/delete/<int:expense_id>", methods=["POST"])
@login_required
def delete_expense(expense_id):
    user = get_current_user()
    user_id = user["id"]

    conn = get_db()
    cur = conn.cursor()
    cur.execute(
        "DELETE FROM expenses WHERE id = ? AND user_id = ?",
        (expense_id, user_id),
    )
    conn.commit()
    conn.close()
    return redirect(url_for("index"))


if __name__ == "__main__":
    init_db()
    app.run(debug=True)
