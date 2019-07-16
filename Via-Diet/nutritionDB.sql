DROP TABLE IF EXISTS user;
DROP TABLE IF EXISTS transactions;
DROP TABLE IF EXISTS items;

CREATE TABLE user(
    employeeId INTEGER PRIMARY KEY NOT NULL,
    empPassword TEXT NOT NULL
);

CREATE TABLE items(
    itemId INTEGER PRIMARY KEY NOT NULL,
    itemName TEXT,
    restaurant TEXT,
    isSide BOOLEAN,
    calories FLOAT,
    protein FLOAT,
    fat FLOAT,
    carb FLOAT,
    fiber FLOAT,
    sugar FLOAT,
    calcium FLOAT,
    iron FLOAT,
    phosphorous FLOAT,
    sodium FLOAT,
    vitaminA FLOAT,
    vitaminC FLOAT,
    cholesterol FLOAT,
    isMeal BOOLEAN
);

CREATE TABLE transactions(
    transactionId INTEGER PRIMARY KEY NOT NULL,
    employeeID INTEGER NOT NULL,
    dateTrans TEXT NOT NULL,
    itemId INTEGER NOT NULL,
    FOREIGN KEY(employeeID) REFERENCES user(employeeId),
    FOREIGN KEY(itemId) REFERENCES items(itemId)
);

.separator ,
.import loginCredentials.csv user
.import itemInfo.csv items
.import transactions.csv transactions