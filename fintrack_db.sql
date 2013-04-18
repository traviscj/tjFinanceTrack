
DROP TABLE IF EXISTS accounts;
CREATE TABLE accounts (
    a_id INTEGER PRIMARY KEY AUTOINCREMENT,
    balance REAL NOT NULL,
    description TEXT NOT NULL,
	description_short TEXT NOT NULL
    );
INSERT INTO accounts (balance, description, description_short) VALUES (0, "SPENDING","S");
INSERT INTO accounts (balance, description, description_short) VALUES (0, "INCOME","I");
INSERT INTO accounts (balance, description, description_short) VALUES (100.00, "Account1","Ac1");
INSERT INTO accounts (balance, description, description_short) VALUES (-5.00, "account2","Ac2");

DROP TABLE IF EXISTS settled_transactions;
CREATE TABLE settled_transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    enter_date TEXT NOT NULL,
    post_date TEXT NOT NULL,
    from_account INTEGER NOT NULL,
    to_account INTEGER NOT NULL,
    delta_balance REAL NOT NULL,
    description TEXT NOT NULL
    );

-- 	enter_date, post_date,from_account,to_account,delta_balance,description

DROP TABLE IF EXISTS pending_transactions;
CREATE TABLE pending_transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    enter_date TEXT NOT NULL,
    post_date TEXT NOT NULL,
    from_account INTEGER NOT NULL,
    to_account INTEGER NOT NULL,
    delta_balance REAL NOT NULL,
    description TEXT NOT NULL
    );

INSERT INTO pending_transactions (enter_date,post_date,from_account,to_account,delta_balance,description)
    VALUES ("2013-04-17", "2013-04-17", 5, 1, 343.80, "plane ticket");
INSERT INTO pending_transactions (enter_date,post_date,from_account,to_account,delta_balance,description)
    VALUES ("2013-04-17", "2013-04-17", 5, 1, 88.00, "seat upgrade");
INSERT INTO pending_transactions (enter_date,post_date,from_account,to_account,delta_balance,description)
    VALUES ("2013-04-17", "2013-07-03", 2, 5, 343.80, "reimbursed plane ticket");

