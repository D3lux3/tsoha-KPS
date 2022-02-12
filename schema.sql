CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username TEXT NOT NULL,
    password TEXT,
    userlevel INTEGER
);

CREATE TABLE admins (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users ON DELETE CASCADE
);

CREATE TABLE games (
    id SERIAL PRIMARY KEY,
    player_a INTEGER REFERENCES users ON DELETE CASCADE,
    player_b INTEGER REFERENCES users ON DELETE CASCADE,
    player_a_hand TEXT,
    player_b_hand TEXT,
    game_status BOOLEAN,
    winner INTEGER REFERENCES users ON DELETE CASCADE,
    time TIMESTAMP
);