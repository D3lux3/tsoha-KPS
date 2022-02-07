CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username TEXT NOT NULL,
    password TEXT,
    userlevel INTEGER
);

CREATE TABLE games (
    id SERIAL PRIMARY KEY,
    player_a INTEGER REFERENCES users,
    player_b INTEGER REFERENCES users,
    player_a_hand TEXT,
    player_b_hand TEXT,
    game_status BOOLEAN,
    winner INTEGER REFERENCES users,
    time TIMESTAMP
);
