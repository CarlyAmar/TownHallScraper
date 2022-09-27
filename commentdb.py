import sqlite3
import comment


class DBConnection:

    INSERT_SQL = """INSERT OR IGNORE INTO comments VALUES({comment_id},"{author}","{title}","{url}","{date}","{author}","{comment}");"""
    SELECT_SQL = "SELECT * FROM comments WHERE id={comment_id};"

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
