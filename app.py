# Adds a form, second route

from flask import Flask, render_template, request

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username")
        db.execute("INSERT INTO users (username) VALUES(?)", username)
        return render_template("success.html", username=username)
    return render_template("register.html")
def greet():
    return render_template("greet.html", name=request.args.get("name", "world"))
