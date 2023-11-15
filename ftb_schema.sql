-- Create users table
-- Changing "User" to Player since User as a reserved keyword and the quotes are annoying
CREATE TABLE Player (
    user_id SERIAL NOT NULL,
    username VARCHAR(100) NOT NULL UNIQUE,
    email VARCHAR(255) NOT NULL UNIQUE,
    password VARCHAR(100) NOT NULL,
    date_created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (user_id)
);

CREATE TABLE ForumPost (
    post_id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    content TEXT,
    author_id INT,
    author_name VARCHAR(255),
    time_posted TIMESTAMP DEFAULT,
    upvotes INT,
    downvotes INT,
    parent_post_id INT,
    FOREIGN KEY (author_id) REFERENCES Player (user_id),
    FOREIGN KEY (parent_post_id) REFERENCES ForumPost(post_id)
);

INSERT INTO Player (username, email, password)
VALUES
    ('dnitsavo', 'dnitsavo@uncc.edu', 'password'),
    ('chachachang', 'pchang13@uncc.edu', 'password'),
    ('weiward', 'twei1@uncc.edu', 'password'),
    ('breakpause', 'bhach@uncc.edu', 'password'),
    ('parvati', 'revans35@uncc.edu', 'password'),
    ('tomz', 'tzimnick@uncc.edu', 'password')
;