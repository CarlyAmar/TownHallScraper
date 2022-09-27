import sqlite3
import comment
from typing import *


class DBConnection:

    INSERT_SQL = """INSERT OR IGNORE INTO comments VALUES({comment_id},"{author}","{title}","{url}","{date}","{author}","{comment}");"""
    SELECT_SQL = "SELECT * FROM comments WHERE id={comment_id};"
    GET_ID_SQL = "SELECT id FROM comments;"
    SELECT_ALL = "SELECT * FROM comments;"

    def __init__(self, db_file: str):
        self._conn = sqlite3.connect(db_file)

    def __del__(self):
        self._conn.close()

    def insert_comment(self, comm: comment.Comment) -> None:
        cmd = DBConnection.INSERT_SQL.format(**comm.json())
        cursor = self._conn.cursor()
        cursor.execute("BEGIN TRANSACTION;")
        cursor.execute(cmd)
        cursor.execute("COMMIT;")
        cursor.close()

    def get_comment(self, comment_id: int) -> comment.Comment:
        cmd = DBConnection.SELECT_SQL.format(comment_id=comment_id)
        cursor = self._conn.cursor()
        cursor.execute(cmd)
        reply = cursor.fetchone()
        print("REPLY: {}".format(reply))
        cursor.close()
        config = {
            "comment_id": reply[0],
            "url": reply[3],
            "date": reply[4],
            "author": reply[1],
            "title": reply[2],
            "comment": reply[6]
        }
        return comment.Comment(config)

    def get_saved_comment_ids(self) -> set:
        cursor = self._conn.cursor()
        cursor.execute(DBConnection.GET_ID_SQL)
        reply = cursor.fetchall()
        cursor.close()
        saved_ids = set([x[0] for x in reply])
        return saved_ids

    def get_all_comments(self) -> List[comment.Comment]:
        cursor = self._conn.cursor()
        cursor.execute(DBConnection.SELECT_ALL)
        reply = cursor.fetchall()
        cursor.close()
        comments = []
        for row in reply:
            comments.append(comment.Comment(DBConnection.row_to_dict(row)))
        return comments

    @staticmethod
    def row_to_dict(row: tuple) -> dict:
        return {
            "comment_id": row[0],
            "url": row[3],
            "date": row[4],
            "author": row[1],
            "title": row[2],
            "comment": row[6]
        }
