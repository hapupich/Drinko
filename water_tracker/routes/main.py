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
    
    logs = mongo.db.water_logs.find({"username": username, "date": today})

    achieved = sum(log["amount"] for log in logs)

    goal = user.get("daily_goal", 2000)  # Default goal: 2000ml
    progress = int((achieved / goal) * 100) if goal > 0 else 0

    liquids = mongo.db.liquids.find()

    return render_template("main.html", goal=goal, achieved=achieved, progress=progress, liquids=liquids)

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
        liquid = request.form["liquid"]
    except (ValueError, KeyError):
        return "Invalid input", 400
    
    mongo.db.water_logs.insert_one({
        "username": username,
        "date": today,
        "liquid": liquid,
        "amount": amount
    })
    
    return redirect("/")

@main_bp.route("/profile")
def profile():
    if "username" not in session:
        return redirect("/auth/login")
    
    username = session["username"]
    user = mongo.db.users.find_one({"username": username})
    
    yesterday = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")
    logs = mongo.db.water_logs.find({"username": username, "date": yesterday})

    drinks_summary = {}
    total_yesterday = 0

    for log in logs:
        drink = log.get("liquid", "Unknown")
        amount = log.get("amount", 0)
        drinks_summary[drink] = drinks_summary.get(drink, 0) + amount
        total_yesterday += amount
    
    return render_template(
        "profile.html",
        username=username,
        yesterday_amount=total_yesterday,
        drinks_summary=drinks_summary,
        gender=user.get("gender"),
        weight=user.get("weight"),
        height=user.get("height"),
        daily_goal=user.get("daily_goal")
    )

