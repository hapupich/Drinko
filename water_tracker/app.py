from flask import Flask, render_template, request, redirect, session
from flask_pymongo import PyMongo
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'default_secret_key')

# MongoDB Configuration
app.config["MONGO_URI"] = os.getenv('MONGO_URI', 'mongodb://localhost:27017/water_tracker')
mongo = PyMongo(app)

# Routes
@app.route("/")
def main_page():
    if "username" not in session:
        return redirect("/login")
    
    username = session["username"]
    today = datetime.now().strftime("%Y-%m-%d")
    user = mongo.db.users.find_one({"username": username})
    log = mongo.db.water_logs.find_one({"username": username, "date": today})
    
    goal = user.get("daily_goal", 2000)  # Default goal: 2000ml
    achieved = log["amount"] if log else 0
    progress = int((achieved / goal) * 100) if goal > 0 else 0
    
    return render_template("main.html", goal=goal, achieved=achieved, progress=progress)

@app.route("/add_water", methods=["POST"])
def add_water():
    if "username" not in session:
        return redirect("/login")
    
    username = session["username"]
    today = datetime.now().strftime("%Y-%m-%d")
    
    try:
        amount = int(request.form["amount"])
        if amount <= 0:
            return "Invalid amount", 400
    except ValueError:
        return "Invalid input", 400
    
    log = mongo.db.water_logs.find_one({"username": username, "date": today})
    if log:
        mongo.db.water_logs.update_one(
            {"username": username, "date": today},
            {"$inc": {"amount": amount}}
        )
    else:
        mongo.db.water_logs.insert_one({
            "username": username,
            "date": today,
            "amount": amount
        })
    
    return redirect("/")

@app.route("/profile")
def profile():
    if "username" not in session:
        return redirect("/login")
    
    username = session["username"]
    yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    log = mongo.db.water_logs.find_one({"username": username, "date": yesterday})
    yesterday_amount = log["amount"] if log else 0
    
    return render_template("profile.html", username=username, yesterday_amount=yesterday_amount)

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        daily_goal = int(request.form["daily_goal"])
        
        if mongo.db.users.find_one({"username": username}):
            return "User already exists!"
        
        mongo.db.users.insert_one({
            "username": username,
            "password": password,
            "daily_goal": daily_goal
        })
        return redirect("/login")
    
    return render_template("register.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        user = mongo.db.users.find_one({"username": username})
        
        if user and user["password"] == password:
            session["username"] = username
            return redirect("/")
        return "Invalid credentials!"
    
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.pop("username", None)
    return redirect("/login")

if __name__ == "__main__":
    app.run(debug=True)