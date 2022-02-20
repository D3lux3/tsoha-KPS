from crypt import methods
import re
from app import app
from flask import render_template, request, session, redirect, flash
from werkzeug.security import check_password_hash, generate_password_hash
from db import db
from utils import accept_friend_request, check_user_and_password, create_game_invite_to_db, create_game_to_db, decline_friend_request, delete_game_by_id, delete_player_from_db, get_all_players, get_friendrequests_for_user, get_game_invites_for_logged, get_logged_in_user, get_one_game, get_ongoing_games, get_winner, handle_login, is_game_owned_by_logged_user, is_logged_admin, is_logged_friend_with_player, is_logged_in, is_not_friend_yet, send_friend_req

@app.route("/")
def index():
    if is_logged_in():
        print(is_logged_admin())
        all_games = get_ongoing_games()
        is_admin = is_logged_admin()

        return render_template("index.html", games= all_games, is_admin=is_admin)
    return redirect("/login")

@app.route("/registration")
def registration():
    return render_template("registration.html")

@app.route("/invites/accept/<int:id>", methods=["POST"])
def accept_friend(id):
    accept_friend_request(id)
    return redirect("/invites")

@app.route("/create/invite/<int:id>", methods=["POST"])
def crete_game_invite(id):
    if is_logged_in and is_logged_friend_with_player(id):
        hand = request.form["hand"]
        create_game_invite_to_db(hand, id)
    return redirect("/")


@app.route("/invites/decline/<int:id>", methods=["POST"])
def decline_friend(id):
    decline_friend_request(id)
    return redirect("/invites")

@app.route("/invites/invite/<int:id>", methods=["POST"])
def friend_request(id):
    send_friend_req(id)
    return redirect("/players")

@app.route("/invites")
def invites():
    if is_logged_in:
        requests = get_friendrequests_for_user()
        game_invites = get_game_invites_for_logged()
        return render_template("invites.html", friend_requests=requests, game_invites=game_invites)

@app.route("/players")
def players():
    all_players = get_all_players()
    is_admin = is_logged_admin()
    return render_template("players.html", players=all_players, is_admin=is_admin, is_not_friend_yet=is_not_friend_yet, is_logged_friend_with_player=is_logged_friend_with_player)

@app.route("/delete/<int:id>", methods=["POST"])
def delete_player(id):
    if is_logged_in() and is_logged_admin():
        delete_player_from_db(id)
    
    return redirect("/")

@app.route("/delete/game/<int:id>", methods=["POST"])
def delete_game(id):
    if is_game_owned_by_logged_user(id) or is_logged_admin:
        delete_game_by_id(id)
    return redirect("/")


@app.route("/register", methods=["POST"])
def register():
    username = request.form["username"]
    password = request.form["password"]

    if not check_user_and_password(username, password):
        return

    hash_pass = generate_password_hash(password)
    sql = "INSERT INTO users (username, password) VALUES (:username, :password)"
    db.session.execute(sql, {"username":username, "password":hash_pass})
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
    hand = request.form["hand"]
    create_game_to_db(hand)
    return redirect("/")

@app.route("/login", methods=["GET","POST"])
def login():

    if is_logged_in:
        redirect("/")

    if request.method == 'POST':
        username = request.form["username"]
        password = request.form["password"]
        error = handle_login(username, password)

        if error is None:
            return redirect("/")
        else:
            flash(error)
            return redirect("/login")

    return render_template("login.html")


@app.route("/logout")
def logout():
    del session["logged_in"]
    del session["username"]
    return redirect("/")
