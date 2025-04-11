from flask import render_template, request, redirect, session
from datetime import datetime, timedelta
from . import main_bp
from db import mongo

@main_bp.route("/")
def main_page():
    if "username" not in session:
        return redirect("/auth/login")
    
    username = session["username"]
    today = datetime.now().strftime("%Y-%m-%d")
    user = mongo.db.users.find_one({"username": username})
    log = mongo.db.water_logs.find_one({"username": username, "date": today})
    
    goal = user.get("daily_goal", 2000)  # Default goal: 2000ml
    achieved = log["amount"] if log else 0
    progress = int((achieved / goal) * 100) if goal > 0 else 0
    
    return render_template("main.html", goal=goal, achieved=achieved, progress=progress)

@main_bp.route("/add_water", methods=["POST"])
def add_water():
    if "username" not in session:
        return redirect("/auth/login")
    
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

@main_bp.route("/profile")
def profile():
    if "username" not in session:
        return redirect("/auth/login")
    
    username = session["username"]
    yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    log = mongo.db.water_logs.find_one({"username": username, "date": yesterday})
    yesterday_amount = log["amount"] if log else 0
    
    return render_template("profile.html", username=username, yesterday_amount=yesterday_amount)
