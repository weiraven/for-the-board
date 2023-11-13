-- Create users table
-- Keep the double quotes because otherwise PostgreSQL treats User as a reserved keyword
CREATE TABLE "User" (
    user_id SERIAL NOT NULL,
    username VARCHAR(255) NOT NULL UNIQUE,
    email VARCHAR(100) NOT NULL UNIQUE,
    password VARCHAR(100) NOT NULL,
    date_created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (user_id)
);

-- When interacting with the "User" table in DataGrip, always remember to use the quotes!
INSERT INTO "User" (username, email, password)
VALUES
    ('dnitsavo', 'dnitsavo@uncc.edu', 'password'),
    ('chachachang', 'pchang13@uncc.edu', 'password'),
    ('weiward', 'twei1@uncc.edu', 'password'),
    ('breakpause', 'bhach@uncc.edu', 'password'),
    ('parvati', 'revans35@uncc.edu', 'password'),
    ('tomz', 'tzimnick@uncc.edu', 'password')
;