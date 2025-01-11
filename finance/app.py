import os

from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session
from flask_session import Session
from werkzeug.security import check_password_hash, generate_password_hash

from helpers import apology, login_required, lookup, usd

# Configure application
app = Flask(__name__)

# Custom filter
app.jinja_env.filters["usd"] = usd

# Configure session to use filesystem (instead of signed cookies)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Configure CS50 Library to use SQLite database
db = SQL("sqlite:///finance.db")


@app.after_request
def after_request(response):
    """Ensure responses aren't cached"""
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response


@app.route("/")
@login_required
def index():
    """Show portfolio of stocks"""
    username = db.execute("SELECT username FROM users WHERE id = ?", (session["user_id"]))
    if not username:
        return apology("User not logged in")
    username = username[0]["username"]
    table_name = f"{username}_table"
    try:
        insert_query= db.execute (f"""SELECT * FROM {table_name}""")
    except RuntimeError as e:
        if "no such table" in str(e):
            return  render_template("nice.html")
    diverse_query = db.execute("SELECT cash FROM users WHERE username = ?", (username,))
    cash = diverse_query[0]["cash"]
    total_value = sum(stock["price"] * stock["shares"] for stock in insert_query)
    total_funds = cash + total_value
    return render_template("index.html", insert_query=insert_query, cash = cash, total_funds = total_funds)

@app.route("/buy", methods=["GET", "POST"])
@login_required
def buy():
    """Buy shares of stock"""
    if request.method == "POST":
        symbol = request.form.get("symbol")
        symbol = lookup(symbol)  # Make sure lookup returns the necessary fields
        if not symbol:
            return apology("Invalid symbol")

        shares = request.form.get("shares")
        if shares.isdigit():
            shares = int(shares)
            if shares <= 0:
                return apology("Invalid number of shares")
        else:
            return apology("Invalid number of shares")

        username = db.execute("SELECT username FROM users WHERE id = ?", (session["user_id"]))
        if not username:
            return apology("User not logged in")
        username = username[0]["username"]
        table_name = f"{username}_table"
        real_name=f"{username}_history_table"
        db.execute(f"""
            CREATE TABLE IF NOT EXISTS {table_name} (
                name TEXT,
                price NUMERIC,
                symbol TEXT,
                shares INTEGER
            );
        """)
        db.execute(f"""
            CREATE TABLE IF NOT EXISTS {real_name} (
                name TEXT,
                price NUMERIC,
                symbol TEXT,
                shares INTEGER,
                type TEXT,
                time DATETIME DEFAULT CURRENT_TIMESTAMP
            );
        """)
        print(symbol)
        user_data = db.execute("SELECT cash FROM users WHERE username = ?", (username,))
        if not user_data:
            return apology("User data not found")

        cash = user_data[0]['cash']
        total_cost = shares * symbol['price']

        if cash >= total_cost:
            updated_cash = cash - total_cost
            update_query = "UPDATE users SET cash = ? WHERE username = ?"
            db.execute(update_query, updated_cash, username)
            # Check if the user already owns shares of the stock
            existing_shares = db.execute(f"SELECT shares FROM {table_name} WHERE symbol = ?", (symbol['symbol'],))
            if existing_shares:
                # Update the existing shares
                new_shares = existing_shares[0]['shares'] + shares
                update_query = f"UPDATE {table_name} SET shares = ? WHERE symbol = ?"
                db.execute(update_query, new_shares, symbol['symbol'])
                real_query = f"""INSERT INTO {real_name} (name, price, symbol, shares, type) VALUES(?, ?, ?, ?, ?)"""
                db.execute(real_query, symbol['name'], symbol['price'], symbol['symbol'], shares, 'buy')
            else:
                # Insert a new row for the stock
                insert_query = f"""INSERT INTO {table_name} (name, price, symbol, shares) VALUES(?, ?, ?, ?)"""
                db.execute(insert_query, symbol['name'], symbol['price'], symbol['symbol'], shares)
                # Insert a new row for the stock in the history table
                real_query = f"""INSERT INTO {real_name} (name, price, symbol, shares, type) VALUES(?, ?, ?, ?, ?)"""
                db.execute(real_query, symbol['name'], symbol['price'], symbol['symbol'], shares, 'buy')
            return redirect("/")
        else:
            return apology("Insufficient funds")
    else:
        return render_template("buy.html")



@app.route("/history")
@login_required
def history():
    """Show history of transactions"""
    username = db.execute("SELECT username FROM users WHERE id = ?", (session["user_id"]))
    if not username:
        return apology("User not logged in")
    username = username[0]["username"]
    real_name = f"{username}_history_table"
    insert_query= db.execute (f"""SELECT * FROM {real_name}""")
    return render_template("history.html", insert_query=insert_query)


@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in"""

    # Forget any user_id
    session.clear()

    # User reached route via POST (as by submitting a form via POST)
    if request.method == "POST":
        # Ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        rows = db.execute(
            "SELECT * FROM users WHERE username = ?", request.form.get("username")
        )

        # Ensure username exists and password is correct
        if len(rows) != 1 or not check_password_hash(
            rows[0]["hash"], request.form.get("password")
        ):
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        # Redirect user to home page
        return redirect("/")

    # User reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")


@app.route("/logout")
def logout():
    """Log user out"""

    # Forget any user_id
    session.clear()

    # Redirect user to login form
    return redirect("/")


@app.route("/quote", methods=["GET", "POST"])
@login_required
def quote():
    """Get stock quote."""
    if request.method == "POST":
        symbol = request.form.get("symbol")
        symbol = lookup(symbol)
        if not symbol:
            return apology("Invalid symbol", 400)
        return render_template("quoted.html", symbol = symbol)
    else:
        return render_template("quote.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    """Register user"""
    if request.method == "POST":
        username = request.form.get("username")
        if not username:
            return apology("username is blank", 400)
        else:
            password = request.form.get("password")
            confirm = request.form.get("confirmation")
        if not password:
            return apology("password is blank", 400)
        elif not confirm:
            return apology("passwords are not the same", 400)
        elif not password == confirm:
            return apology("passwords are not the same", 400)
        else:
            final = generate_password_hash(password)
            try:
                # Insert both username and hashed password in one query
                db.execute("INSERT INTO users (username, hash) VALUES(?, ?)", username, final)
            except ValueError:
                    return apology("username already used", 400)
    else:
        return render_template("register.html")
    return redirect("/")

@app.route("/sell", methods=["GET", "POST"])
@login_required
def sell():
    """Sell shares of stock"""

    if request.method == "POST":
        symbol = request.form.get("symbol")
        symbol = lookup(symbol)  # Make sure lookup returns the necessary fields
        if not symbol:
            return apology("Invalid symbol")

        shares = request.form.get("shares")
        if shares.isdigit():
            shares = int(shares)
            if shares <= 0:
                return apology("Invalid number of shares")
        else:
            return apology("Invalid number of shares")

        username = db.execute("SELECT username FROM users WHERE id = ?", (session["user_id"]))
        if not username:
            return apology("User not logged in")
        username = username[0]["username"]
        user_data = db.execute("SELECT cash FROM users WHERE username = ?", (username,))
        if not user_data:
            return apology("User data not found")
        table_name = f"{username}_table"
        real_name=f"{username}_history_table"
        existing_shares = db.execute(f"SELECT shares FROM {table_name} WHERE symbol = ?", (symbol['symbol'],))
        if existing_shares:
            # Update the existing shares
            if existing_shares[0]['shares'] >= shares:
                new_shares = existing_shares[0]['shares'] - shares
                update_query = f"UPDATE {table_name} SET shares = ? WHERE symbol = ?"
                db.execute(update_query, new_shares, symbol['symbol'])
                cash = user_data[0]['cash']
                total_gain = shares * symbol['price']
                updated_cash = cash + total_gain
                update_query = "UPDATE users SET cash = ? WHERE username = ?"
                db.execute(update_query, updated_cash, username)
                insert_query = f"""INSERT INTO {real_name} (name, price, symbol, shares, type) VALUES(?, ?, ?, ?, ?)"""
                db.execute(insert_query, symbol['name'], symbol['price'], symbol['symbol'], shares, 'sell')
            else:
                return apology("shares not enough")
    else:
        username = db.execute("SELECT username FROM users WHERE id = ?", (session["user_id"]))
        if not username:
            return apology("User not logged in")
        username = username[0]["username"]
        table_name = f"{username}_table"
        try:
            insert_query= db.execute (f"""SELECT * FROM {table_name}""")
        except RuntimeError as e:
            if "no such table" in str(e):
                return  render_template("nice.html")
        return render_template("sell.html", symbols=insert_query)
    return redirect("/")
@app.route("/deposit", methods=["GET", "POST"])
@login_required
def deposit():
    """Deposit money"""
    if request.method == "POST":
        amount = request.form.get("amount")
        if amount.isdigit():
            amount = int(amount)
            if amount <= 0:
                return apology("Invalid amount")
            else:
                username = db.execute("SELECT username FROM users WHERE id = ?", (session["user_id"]))
                if not username:
                    return apology("User not logged in")
                username = username[0]["username"]
                user_data = db.execute("SELECT cash FROM users WHERE username = ?", (username,))
                if not user_data:
                    return apology("User data not found")
                cash = user_data[0]['cash']
                updated_cash = cash + amount
                update_query = "UPDATE users SET cash = ? WHERE username = ?"
                db.execute(update_query, updated_cash, username)
                return redirect("/")
    else:
        return render_template("deposit.html")
