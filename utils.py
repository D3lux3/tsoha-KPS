from db import db
from flask import session

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
