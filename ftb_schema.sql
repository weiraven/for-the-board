-- Create users table
-- Changing "User" to Player since User as a reserved keyword and the quotes are annoying
CREATE TABLE Player (
    user_id SERIAL,
    first_name VARCHAR(255) NOT NULL,
    last_name VARCHAR(255) NOT NULL,
    username VARCHAR(255) NOT NULL UNIQUE,
    email VARCHAR(255) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    date_created TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (user_id)
);

CREATE TABLE ForumPost (
    post_id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    content TEXT,
    author_id INT,
    time_posted TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    upvotes INT, -- removed downvotes since downvote button should just decrement upvotes
    parent_post_id INT,
    flairs VARCHAR(255), -- added flairs directly to CREATE TABLE statement
    FOREIGN KEY (author_id) REFERENCES Player (user_id),
    FOREIGN KEY (parent_post_id) REFERENCES ForumPost(post_id)
);

-- Now that we have sign-up and login auth implemented. We can no longer manually edit
-- passwords since Bcrypt will now salt and hash our passwords for us, so remember to 
-- DROP TABLE on any old user tables you may have created.
-- Keeping this comment here for dummy data in case you want to create some dummy accounts
-- in your own database instances.

--  1.   ('weiward', 'twei1@uncc.edu', 'asdf')
--  2.   ('dnitsavo', 'dnitsavo@uncc.edu', 'asdf')
--  3.   ('chachachang', 'pchang13@uncc.edu', 'asdf')
--  4.   ('breakpause', 'bhach@uncc.edu', 'asdf')
--  5.   ('parvati', 'revans35@uncc.edu', 'asdf')
--  6.   ('tomz', 'tzimnick@uncc.edu', 'asdf')

-- You will need to have a user account with user_id 1 and 4 at least for the following forum posts to work.

INSERT INTO ForumPost (title, content, author_id)
VALUES
    ('TEST POST! TEST POST! TEST POST!', 'Lorem ipsum dolor sit amet consectetur adipisicing elit. Dignissimos aspernatur omnis, perferendis fuga quaerat ex, id sed dolores minus dolorum veritatis dolor commodi voluptates, praesentium beatae error consectetur hic. Fuga consequuntur illo odit sit eveniet laudantium? Impedit laboriosam mollitia ut iusto harum voluptates, nostrum nam esse tempora facilis cupiditate.', 1),
    ('[LFG][sHC][static][Aether][DC Travel][SGE] Mit Healer LFG 7.0+', '<p>I''m looking for a week 1-2 clearing static for 7.0 savage and ultimate content. I strongly prefer to play Sage but I can swap to Scholar for the right group. My long-time static and friend-group is disbanding after this tier. I''ve cleared all past savage raid tiers and ultimates while they were relevant (before potency/level-cap increase soft nerfs) except UCOB and TOP.</p><p>- My logs: https://www.fflogs.com/character/na/cactuar/spiral%20sun<br>- My VODs: https://www.twitch.tv/weiward/videos<br></p><p>Availability: I''m currently back in school full-time, so unfortunately I won''t have PTO/vacation time to alarm-clock week 1. But I will be openly available at the following times:</p><p>- Mon/Wed/Fri: After 6 PM EST<br>- Tues/Thur - After 10 PM EST<br>- Saturday & Sunday: All Day<br></p><p>Please send me a DM via Discord if interested, cheers!</p>', 1),
    ('LF3M for fresh D&D 5e campaign', '<p>Calling All Adventurers!</p><p>Are you ready to embark on an epic journey? Do you have the courage to face the unknown, the wisdom to solve intricate puzzles, and the charisma to lead or negotiate your way out of tricky situations? If so, we want you to join our virtual Dungeons & Dragons 5e campaign!</p><p>Our campaign is set in a richly detailed world, teeming with diverse cultures, ancient mysteries, and untold dangers. Whether you''re a seasoned veteran or a newcomer to the game, you''ll find a place at our table!</p>', 3),
    ('How to pick up elves in a dungeon', 'Step 1: Just roll a nat 20 on your rizz check 4head lol', 4)
;

--Added new col
ALTER TABLE forumpost
ADD COLUMN category VARCHAR(255);