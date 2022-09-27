PRAGMA foreign_keys=OFF;
BEGIN TRANSACTION;
CREATE TABLE comments (id integer primary key, name TEXT, title TEXT, url TEXT, date TEXT, author TEXT, comment TEXT);
INSERT OR IGNORE INTO comments VALUES(0,'name','title','url','date','author','comment');
COMMIT;
