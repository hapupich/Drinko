from flask import render_template, request, redirect, session
from . import auth_bp
from db import mongo

@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        gender = request.form["gender"]
        weight = float(request.form["weight"])
        height = float(request.form["height"])
        
        custom_goal_checked = "custom_goal_checkbox" in request.form
        if custom_goal_checked and request.form["daily_goal"]:
            daily_goal = int(request.form["daily_goal"])
        else:
            if gender == "male":
                daily_goal = int(weight * 35)
            elif gender == "female":
                daily_goal = int(weight * 31)
            else:
                daily_goal = 2000

        if mongo.db.users.find_one({"username": username}):
            return "User already exists!"

        mongo.db.users.insert_one({
            "username": username,
            "password": password,
            "gender": gender,
            "weight": weight,
            "height": height,
            "daily_goal": daily_goal
        })

        session["just_registered"] = {
            "username": username,
            "gender": gender,
            "weight": weight,
            "height": height,
            "daily_goal": daily_goal
        }

        return redirect("/auth/show_goal")
    
    return render_template("register.html")

@auth_bp.route("/show_goal")
def show_goal():
    data = session.get("just_registered")
    if not data:
        return redirect("/auth/login")
    return render_template("show_goal.html", user_data=data)

@auth_bp.route("/login", methods=["GET", "POST"])
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

@auth_bp.route("/logout")
def logout():
    session.pop("username", None)
    return redirect("/auth/login")
