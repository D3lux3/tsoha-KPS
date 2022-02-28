from crypt import methods
from os import abort
import re
from app import app
from flask import render_template, request, session, redirect, flash
from werkzeug.security import check_password_hash, generate_password_hash
from db import db
from utils import accept_friend_request, check_csrf, check_user_and_password, create_game_invite_to_db, create_game_to_db, decline_friend_request, delete_friend_by_id, delete_game_by_id, delete_player_from_db, get_all_friends_of_logged, get_all_players, get_friendrequests_for_user, get_game_invites_for_logged, get_logged_in_user, get_one_game, get_ongoing_games, get_winner, handle_login, handle_register, is_game_owned_by_logged_user, is_logged_admin, is_logged_friend_with_player, is_logged_in, is_not_friend_yet, send_friend_req

@app.route("/")
def index():
    if is_logged_in():
        print(is_logged_admin())
        all_games = get_ongoing_games()
        is_admin = is_logged_admin()

        return render_template("index.html", games= all_games, is_admin=is_admin)
    return redirect("/login")


@app.route("/invites/accept/<int:id>", methods=["POST"])
def accept_friend(id):

    token = request.form["csrf_token"]
    if not check_csrf(token):
        abort(403)

    accept_friend_request(id)
    return redirect("/invites")

@app.route("/create/invite/<int:id>", methods=["POST"])
def crete_game_invite(id):
    if is_logged_in and is_logged_friend_with_player(id):
        token = request.form["csrf_token"]
        if not check_csrf(token):
            abort(403)

        hand = request.form["hand"]
        create_game_invite_to_db(hand, id)
    return redirect("/")


@app.route("/invites/decline/<int:id>", methods=["POST"])
def decline_friend(id):

    token = request.form["csrf_token"]
    if not check_csrf(token):
        abort(403)

    decline_friend_request(id)
    return redirect("/invites")

@app.route("/invites/invite/<int:id>", methods=["POST"])
def friend_request(id):
    token = request.form["csrf_token"]
    if not check_csrf(token):
        abort(403)
    
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

    token = request.form["csrf_token"]
    if not check_csrf(token):
        abort(403)

    if is_logged_in() and is_logged_admin():
        delete_player_from_db(id)
    
    return redirect("/")

@app.route("/delete/game/<int:id>", methods=["POST"])
def delete_game(id):
    token = request.form["csrf_token"]
    if not check_csrf(token):
        abort(403)

    if is_game_owned_by_logged_user(id) or is_logged_admin:
        delete_game_by_id(id)
    return redirect("/")


@app.route("/register", methods=["POST", "GET"])
def register():
    if is_logged_in:
        redirect("/")
    
    if request.method == 'POST':
        username = request.form["username"]
        password = request.form["password"]
        password2 = request.form["password2"]
        error = handle_register(username, password, password2)
        
        if error is None:
            handle_login(username, password)
            return redirect("/")
        else:
            flash(error)
            return redirect("/register")

    return render_template("registration.html")

@app.route("/play/<int:id>", methods=["POST"])
def play(id):
    if not is_logged_in:
        return redirect("/login")

    token = request.form["csrf_token"]
    if not check_csrf(token):
        abort(403)

    user_id = int(get_logged_in_user().id)
    hand = request.form["hand"]
    game = get_one_game(id)

    winner_id = get_winner(game.player_a, game.player_a_hand, user_id, hand)

    sql = "UPDATE games SET player_b=:player_b, player_b_hand=:player_b_hand, game_status=:game_status, winner=:winner WHERE id=:id"
    db.session.execute(sql, {"player_b":user_id, "player_b_hand": hand, "game_status": True, "winner": winner_id, "id": id})
    db.session.commit()

    return redirect("/")

@app.route("/friends")
def friend_list():
    friends = get_all_friends_of_logged()
    return render_template("/friends.html", friends=friends)

@app.route("/delete/friend/<int:id>", methods=["POST"])
def delete_friend(id):

    token = request.form["csrf_token"]
    if not check_csrf(token):
        abort(403)

    if is_logged_friend_with_player(id):
        delete_friend_by_id(id)
    return redirect("/friends")

@app.route("/create", methods=["POST"])
def create_game():
    if not is_logged_in:
        return redirect("/login")
        
    token = request.form["csrf_token"]
    if not check_csrf(token):
        abort(403)
        
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
            return render_template("login.html", username=username)


    return render_template("login.html")


@app.route("/logout")
def logout():
    del session["logged_in"]
    del session["username"]
    del session["csrf_token"]
    return redirect("/")
