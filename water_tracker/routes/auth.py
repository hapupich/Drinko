from flask import render_template, request, redirect, session
from . import auth_bp
from db import mongo

@auth_bp.route("/register", methods=["GET", "POST"])
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
        return redirect("/auth/login")
    
    return render_template("register.html")

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
