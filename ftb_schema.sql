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
