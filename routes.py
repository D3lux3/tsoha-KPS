from app import app
from flask import render_template, request, session, redirect
from werkzeug.security import check_password_hash, generate_password_hash
from db import db
from utils import check_user_and_password, get_logged_in_user, get_one_game, get_ongoing_games, get_winner, is_logged_in

@app.route("/")
def index():
    if is_logged_in():
        all_games = get_ongoing_games()
        print(all_games)
        return render_template("index.html", games= all_games)
    return redirect("/login")

@app.route("/registration")
def registration():
    return render_template("registration.html")

@app.route("/register", methods=["POST"])
def register():
    username = request.form["username"]
    password = request.form["password"]

    if not check_user_and_password(username, password):
        return

    hash_pass = generate_password_hash(password)
    sql = "INSERT INTO users (username, password, level) VALUES (:username, :password, :level)"
    db.session.execute(sql, {"username":username, "password":hash_pass, "level":1})
    db.session.commit()
    
    return redirect("/")

@app.route("/play/<int:id>", methods=["POST"])
def play(id):
    if not is_logged_in:
        return redirect("/login")
    user_id = int(get_logged_in_user().id)
    hand = request.form["hand"]
    game = get_one_game(id)

    winner_id = get_winner(game.player_a, game.player_a_hand, user_id, hand)

    sql = "UPDATE games SET player_b=:player_b, player_b_hand=:player_b_hand, game_status=:game_status, winner=:winner WHERE id=:id"
    db.session.execute(sql, {"player_b":user_id, "player_b_hand": hand, "game_status": True, "winner": winner_id, "id": id})
    db.session.commit()

    return redirect("/")

@app.route("/create", methods=["POST"])
def create_game():
    if not is_logged_in:
        return redirect("/login")
    user_id = int(get_logged_in_user().id)
    hand = request.form["hand"]
    sql = "INSERT INTO games (player_a, player_a_hand, game_status, time) VALUES (:player_a, :player_a_hand, :game_status, NOW())"
    db.session.execute(sql, {"player_a": user_id, "player_a_hand": hand, "game_status": False})
    db.session.commit()
    return redirect("/")

@app.route("/login")
def loginPage():
    return render_template("login.html")

@app.route("/log", methods=["POST"])
def login():
    username = request.form["username"]
    password = request.form["password"]

    sql = "SELECT id, password FROM users WHERE username=:username"
    result = db.session.execute(sql, {"username": username})
    user = result.fetchone()

    if not user or check_user_and_password(username, password):
        return

    hashed_pass = user.password
    if check_password_hash(hashed_pass, password):
        session["username"] = username
        session["logged_in"] = True

    return redirect("/")


@app.route("/logout")
def logout():
    del session["logged_in"]
    del session["username"]
    return redirect("/")
