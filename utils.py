from db import db
from flask import session
from werkzeug.security import check_password_hash, generate_password_hash

def check_if_username_exists(username: str):
    sql = "SELECT id, username FROM users WHERE username=:username"
    result = db.session.execute(sql, {"username": username})
    user = result.fetchone()
    if not user:
        return False
    return True

def get_logged_in_user():
    if is_logged_in:
        sql = "SELECT id, username FROM users WHERE username=:username"
        username = session.get("username")
        result = db.session.execute(sql, {"username": username})
        user = result.fetchone()
        if not user:
            return None
        return user
    return None

def check_user_and_password(username: str, password: str):
    if password == "" or username == "" or check_if_username_exists(username):
        return False
    return True

def is_logged_in():
    if session.get("username") is None:
        return False
    return True 

def handle_login(username, password):
    error = None
    sql = "SELECT id, password FROM users WHERE username=:username"
    result = db.session.execute(sql, {"username": username})
    user = result.fetchone()

    if not user or check_user_and_password(username, password):
        error = "Username or password is incorrect."
        return error

    hashed_pass = user.password
    if check_password_hash(hashed_pass, password):
        session["username"] = username
        session["logged_in"] = True
        return error

def get_friendrequests_for_user():
    if is_logged_in:
        user_id = get_logged_in_user().id
        sql = """
        SELECT friends.id, u2.username AS player_a, u.username AS player_b, friends.accepted  FROM friends
        JOIN users u on u.id = friends.player_b
        JOIN users u2 on u2.id = friends.player_a
        WHERE friends.accepted = FALSE AND friends.player_b=:player_id;
        """
        result = db.session.execute(sql, {"player_id":user_id})
        requests = result.fetchall()
        return requests

def is_not_friend_yet(user_id):
    logged_id = get_logged_in_user().id
    if (user_id == logged_id):
        return False
    
    sql = """
    SELECT COUNT(*) FROM friends
    WHERE 
    (player_a=:logged OR player_b=:logged) AND
    (player_a=:target OR player_b=:target);
    """
    result = db.session.execute(sql, {"logged": logged_id, "target": user_id})
    res = result.fetchone()
    if res.count > 0:
        return False
    return True

def accept_friend_request(req_id):
    if is_logged_in:
        sql = """UPDATE friends SET accepted=TRUE WHERE id=:req_id"""
        db.session.execute(sql, {"req_id":req_id})
        db.session.commit()

def send_friend_req(target_player_id):
    if is_logged_in:
        logged_user_id = get_logged_in_user().id
        sql = """
        INSERT INTO friends(player_a, player_b, accepted)
        VALUES (:logged, :target, FALSE);
        """
        db.session.execute(sql, {"logged": logged_user_id, "target": target_player_id})
        db.session.commit()

def decline_friend_request(req_id):
    if is_logged_in:
        sql = """DELETE FROM friends WHERE id=:req_id"""
        db.session.execute(sql, {"req_id":req_id})
        db.session.commit()


def is_game_owned_by_logged_user(id):
    if is_logged_in:
        username = session.get("username")
        sql = """
        SELECT games.id FROM games
        WHERE games.id=:id AND
        games.player_a = (SELECT id FROM users WHERE users.username=:username);
        """
        result = db.session.execute(sql, {"id":id, "username":username})
        is_owned = result.fetchone()
        if not is_owned:
            return False
        return True

def get_winner(player_a, player_a_hand, player_b, player_b_hand):
    if player_a_hand == player_b_hand:
        return None
    elif player_a_hand == "ROCK" and player_b_hand == "SCISSORS":
        return player_a
    elif player_a_hand == "PAPER" and player_b_hand == "ROCK":
        return player_a
    elif player_a_hand == "SCISSORS" and player_b_hand == "PAPER":
        return player_a
    return player_b

def delete_game_by_id(id):
    sql = """DELETE FROM games WHERE id=:id"""
    db.session.execute(sql, {"id": id})
    db.session.commit()


def delete_player_from_db(player_id):
    sql = """DELETE from users WHERE id=:player_id;"""
    db.session.execute(sql, {"player_id": player_id})
    db.session.commit()

def is_logged_admin():
    if is_logged_in:
        username = session.get("username")
        sql = """
                SELECT u.username AS username FROM admins
                JOIN users u on u.id = admins.user_id
                WHERE username=:username;
              """

        result = db.session.execute(sql, {"username": username})
        user = result.fetchone()
        if user:
            return True

    return False

def get_ongoing_games():
    sql = """SELECT games.id, a.username AS player_a, player_a_hand, b.username AS player_b, player_b_hand, game_status, u.username AS winner, time FROM games
           LEFT JOIN users u on u.id = games.winner
           LEFT JOIN users a on a.id = games.player_a
           LEFT JOIN users b on b.id = games.player_b;"""
    result = db.session.execute(sql)
    games = result.fetchall()
    return games

def get_all_players():
    sql = "SELECT id, username FROM users;"
    result = db.session.execute(sql)
    players = result.fetchall()
    return players

def get_one_game(id):
    sql = "SELECT * FROM games WHERE id=:id;"
    result = db.session.execute(sql, {"id": id})
    game = result.fetchone()
    return game
