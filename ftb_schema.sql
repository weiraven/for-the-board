-- Create users table. Named Player because User is a reserved word in PostgreSQL.
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
    upvotes INT,
    parent_post_id INT,
    flairs VARCHAR(255),  
    category VARCHAR(255),
    FOREIGN KEY (author_id) REFERENCES Player (user_id),
    FOREIGN KEY (parent_post_id) REFERENCES ForumPost (post_id)
);

CREATE TABLE Game (
    game_id SERIAL PRIMARY KEY,
    game VARCHAR(255) NOT NULL ,
    description TEXT
);

CREATE TABLE game_session (
    active_game_id SERIAL PRIMARY KEY,
    game_id INTEGER REFERENCES game(game_id) NOT NULL,
    title VARCHAR(255) NOT NULL,
    open_for_join BOOLEAN DEFAULT TRUE NOT NULL,
    owner VARCHAR(255) REFERENCES player(username),
    log TEXT
);

CREATE TABLE active_game (
    active_game_id SERIAL NOT NULL,
    user_id INTEGER REFERENCES player(user_id) NOT NULL
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

INSERT INTO ForumPost (title, content, author_id, upvotes, flairs, category)
VALUES
    ('TEST POST! TEST POST! TEST POST!', 'Lorem ipsum dolor sit amet consectetur adipisicing elit. Dignissimos aspernatur omnis, perferendis fuga quaerat ex, id sed dolores minus dolorum veritatis dolor commodi voluptates, praesentium beatae error consectetur hic. Fuga consequuntur illo odit sit eveniet laudantium? Impedit laboriosam mollitia ut iusto harum voluptates, nostrum nam esse tempora facilis cupiditate.', 1, 0, 'Strategy, Miscellaneous', 'community-square'),
    ('[LFG][sHC][static][Aether][DC Travel][SGE] Mit Healer LFG 7.0+', '<p>I''m looking for a week 1-2 clearing static for 7.0 savage and ultimate content. I strongly prefer to play Sage but I can swap to Scholar for the right group. My long-time static and friend-group is disbanding after this tier. I''ve cleared all past savage raid tiers and ultimates while they were relevant (before potency/level-cap increase soft nerfs) except UCOB and TOP.</p><p>- My logs: https://www.fflogs.com/character/na/cactuar/spiral%20sun<br>- My VODs: https://www.twitch.tv/weiward/videos<br></p><p>Availability: I''m currently back in school full-time, so unfortunately I won''t have PTO/vacation time to alarm-clock week 1. But I will be openly available at the following times:</p><p>- Mon/Wed/Fri: After 6 PM EST<br>- Tues/Thur - After 10 PM EST<br>- Saturday & Sunday: All Day<br></p><p>Please send me a DM via Discord if interested, cheers!</p>', 1, 0, 'FFXIV, LFG, Raid', 'community-square'),
    ('LF3M for fresh D&D 5e campaign', '<p>Calling All Adventurers!</p><p>Are you ready to embark on an epic journey? Do you have the courage to face the unknown, the wisdom to solve intricate puzzles, and the charisma to lead or negotiate your way out of tricky situations? If so, we want you to join our virtual Dungeons & Dragons 5e campaign!</p><p>Our campaign is set in a richly detailed world, teeming with diverse cultures, ancient mysteries, and untold dangers. Whether you''re a seasoned veteran or a newcomer to the game, you''ll find a place at our table!</p>', 3, 0, 'D&D, LFM', 'community-square'),
    ('How to pick up elves in a dungeon', 'Step 1: Just roll a nat 20 on your rizz check 4head lol', 4, 0, 'Fantasy, Humor', 'community-square')
;

--Datasets you can use for Player & ForumPost table - brandon

--Player
INSERT INTO Player (first_name, last_name, username, email, password)
VALUES ('Maximus', 'Spellbound', 'EpicWizardry42', 'epicwizard42@roll20forum.com', 'magicPassword123');

INSERT INTO Player (first_name, last_name, username, email, password)
VALUES ('Theodore', 'Lorekeeper', 'LoreKing3000', 'loreking3000@roll20forum.com', 'loreMasterPass');

INSERT INTO Player (first_name, last_name, username, email, password)
VALUES ('Nora', 'Newb', 'AlwaysLearning', 'alwayslearning@roll20forum.com', 'newbiePassword');

-- Insert Player 4: The Snack Provider
INSERT INTO Player (first_name, last_name, username, email, password)
VALUES ('Sam', 'Snacker', 'SnackDragon', 'snackdragon@roll20forum.com', 'snackAttack123');

-- Insert Player 5: The One Who Always Plays a Rogue
INSERT INTO Player (first_name, last_name, username, email, password)
VALUES ('Rick', 'Rogue', 'SneakyStabber', 'sneakystabber@roll20forum.com', 'stealthModePass');

-- Insert Player 6: The Rulebook Lawyer
INSERT INTO Player (first_name, last_name, username, email, password)
VALUES ('Lawrence', 'Legality', 'RuleLawyer', 'rulelawyer@roll20forum.com', 'ruleTheGame123');

-- Insert Player 7: The "It's What My Character Would Do" Excuse User
INSERT INTO Player (first_name, last_name, username, email, password)
VALUES ('Chris', 'Chaos', 'ChaoticNeutral', 'chaoticneutral@roll20forum.com', 'chaosIsMyPass');

-- Insert Player 8: The Dungeon Master's Pet
INSERT INTO Player (first_name, last_name, username, email, password)
VALUES ('Daniel', 'Mastermind', 'DMsFave', 'dmsfave@roll20forum.com', 'favoritePlayer123');

-- Insert Player 9: The One Who Takes Forever to Make a Move
INSERT INTO Player (first_name, last_name, username, email, password)
VALUES ('Ivy', 'Indecision', 'IndecisiveHero', 'indecisivehero@roll20forum.com', 'makeAMovePass');

-- Insert Player 10: The Mysterious One Who Barely Talks
INSERT INTO Player (first_name, last_name, username, email, password)
VALUES ('Morgan', 'Mystique', 'SilentAssassin', 'silentassassin@roll20forum.com', 'silentButDeadly123');


--Forumpost
-- Post 1: A romanticized view of medieval strategy games
INSERT INTO ForumPost (title, content, author_id, upvotes, flairs, category)
VALUES ('In Defense of the Noble Knight in Chess', 'M''ladies and m''lords, let us discuss the unparalleled valor of the knight in our beloved game of chess. A piece of both cunning and bravery!', 1, 15, 'Chess, Knight, Strategy', 'community-square');

-- Post 2: Seeking members for a chivalrous D&D campaign
INSERT INTO ForumPost (title, content, author_id, upvotes, flairs, category)
VALUES ('D&D Campaign: Knights of the Round Table', 'Greetings! I seek gallant adventurers to join my D&D campaign themed around the Knights of the Round Table. Chivalry and honor shall be our guiding stars!', 2, 20, 'D&D, Chivalry, Knights', 'looking-for-group');

-- Post 3: Sharing a medieval-themed board game design
INSERT INTO ForumPost (title, content, author_id, upvotes, flairs, category)
VALUES ('Behold My Medieval Board Game Creation', 'Good sirs and fair maidens, I present to thee my latest creation: a board game set in the medieval era, complete with castles and dragons. Seek thy counsel for improvement!', 3, 25, 'Board Game, Medieval, Design', 'creative-content');

-- Post 4: Discussing the art of role-playing in games
INSERT INTO ForumPost (title, content, author_id, upvotes, flairs, category)
VALUES ('The Art of Role-Playing: Tips for the Aspiring Bard', 'To my fellow enthusiasts in the art of role-playing, particularly those who wish to master the bard’s way, what are thy tips for captivating an audience both in-game and out?', 4, 18, 'Role-Playing, Bard, Tips', 'gamemaster-corner');

-- Post 5: A humorous take on fantasy tropes
INSERT INTO ForumPost (title, content, author_id, upvotes, flairs, category)
VALUES ('Fantasy Tropes That Never Get Old', 'Verily, I say, the trope of mistaking a halfling for a child never doth grow old. What be some fantasy tropes that bring thee joy or mirth in thy campaigns?', 5, 30, 'Fantasy, Tropes, Humor', 'community-square');

-- Post 6: Seeking group for a high fantasy adventure
INSERT INTO ForumPost (title, content, author_id, upvotes, flairs, category)
VALUES ('High Fantasy Adventure Awaits!', 'Hark! Who among thee wishes to embark on a high fantasy adventure this fortnight? Wizards, elves, and dwarves preferred. We shall traverse mystical lands together!', 6, 22, 'D&D, High Fantasy, LFG', 'looking-for-group');

-- Post 7: A debate on the best fantasy novels
INSERT INTO ForumPost (title, content, author_id, upvotes, flairs, category)
VALUES ('Debate: The Greatest Fantasy Novel of All Time', 'Good denizens of ForTheBoard, I propose a debate: what is the greatest fantasy novel ever penned? My vote lies with Tolkien, but I await thine opinions.', 7, 19, 'Fantasy, Novels, Debate', 'community-square');

-- Post 8: Sharing experiences from a medieval fair
INSERT INTO ForumPost (title, content, author_id, upvotes, flairs, category)
VALUES ('Tales from the Medieval Fair', 'This weekend, I ventured to a medieval fair and it was as if I had stepped into another realm! Share thine own experiences of such wondrous events!', 8, 17, 'Medieval Fair, Experiences, Stories', 'community-square');

-- Post 9: Tips for creating a knight character in D&D
INSERT INTO ForumPost (title, content, author_id, upvotes, flairs, category)
VALUES ('Creating the Ultimate Knight Character in D&D', 'Fellow adventurers, I seek thine wisdom in crafting the ultimate knight character in Dungeons & Dragons. Any tips for a squire such as myself?', 9, 21, 'D&D, Knight, Character Creation', 'gamemaster-corner');

-- Post 10: Discussing the revival of traditional board games
INSERT INTO ForumPost (title, content, author_id, upvotes, flairs, category)
VALUES ('The Renaissance of Traditional Board Games', 'In this age of digital diversion, I find myself drawn back to the joys of traditional board games. Do any among you share this sentiment? Let us discuss the classics!', 10, 20, 'Board Games, Traditional, Discussion', 'community-square');

-- Post 11: Reporting a bug with a board game scoring feature
INSERT INTO ForumPost (title, content, author_id, upvotes, flairs, category)
VALUES ('Issue with Scoring in Online Board Game', 'Fellow gamers, has anyone else encountered issues with the scoring system in our online board game portal? My last three games didn’t record scores properly. Seeking assistance or a fix!', 3, 12, 'Board Games, Scoring, Bug', 'bug-report-technical');

-- Post 12: Technical issue with a D&D character creation tool
INSERT INTO ForumPost (title, content, author_id, upvotes, flairs, category)
VALUES ('Glitch in D&D Character Creator Tool', 'Greetings, adventurers! I’ve been facing a peculiar glitch in the D&D character creator tool where certain abilities are not updating correctly. Anyone else experiencing this or know a workaround?', 5, 18, 'D&D, Character Creation, Glitch', 'bug-report-technical');
