import os
from functools import wraps

from flask import Flask, redirect, render_template, request, session, url_for, flash
from pymongo import MongoClient
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "change-this-in-production")

MONGO_URI = os.environ.get("MONGO_URI", "mongodb://localhost:27017/")
MONGO_DB_NAME = os.environ.get("MONGO_DB_NAME", "ai_cardio")
GRADIO_URL = os.environ.get("GRADIO_URL", "http://127.0.0.1:7860")

mongo_client = MongoClient(MONGO_URI)
db = mongo_client[MONGO_DB_NAME]
users_collection = db["users"]
users_collection.create_index("username", unique=True)


def login_required(view_func):
    @wraps(view_func)
    def wrapper(*args, **kwargs):
        if "username" not in session:
            return redirect(url_for("login"))
        return view_func(*args, **kwargs)

    return wrapper


@app.route("/")
def index():
    return render_template("home.html")


@app.route("/ai-app")
@login_required
def ai_app():
    return redirect(GRADIO_URL)


@app.after_request
def add_permissions_policy(response):
    response.headers["Permissions-Policy"] = 'microphone=(self "http://127.0.0.1:7860"), camera=(self "http://127.0.0.1:7860")'
    return response


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        if not username or not password:
            flash("Username and password are required.", "error")
            return render_template("register.html")

        if users_collection.find_one({"username": username}):
            flash("Username already exists. Please choose another.", "error")
            return render_template("register.html")

        users_collection.insert_one(
            {
                "username": username,
                "password_hash": generate_password_hash(password),
            }
        )
        flash("Registration successful. Please login.", "success")
        return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        user = users_collection.find_one({"username": username})
        if not user or not check_password_hash(user["password_hash"], password):
            flash("Invalid username or password.", "error")
            return render_template("login.html")

        session["username"] = username
        return redirect(GRADIO_URL)

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=True, use_reloader=False)
