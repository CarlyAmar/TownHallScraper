import comment
import commentdb
from typing import *
from collections import Counter


class Reader:
    def __init__(self, db: commentdb.DBConnection):
        self._db = db
        self._comments = db.get_all_comments()

    def with_tag(self, tag: str, allow_anon: bool = True) -> List[comment.Comment]:
        comments = []
        for com in self._comments:
            if tag in com.title.lower() and (allow_anon or not com.is_anon()):
                comments.append(com)
        return comments

    def filter_repeats(self):
        new_comments = []
        body_set = set()
        for com in self._comments:
            if com.comment not in body_set:
                new_comments.append(com)
                body_set.add(com.comment)
        self._comments = new_comments

    def amount_anon(self) -> int:
        anon = 0
        for com in self._comments:
            if com.is_anon():
                anon += 1
        return anon

    def __str__(self, verbose: bool = False) -> str:
        support = 0
        oppose = 0
        unknown = 0
        total = support + oppose + unknown
        msg = "Support: {} ({:.2f}%) Oppose: {} ({:.2f}%) Unknown: {} ({:.2f}%) Total: {}".format(
            support, support / total * 100, oppose, oppose / total * 100, unknown, unknown / total * 100, total
        )
        return msg

    def __len__(self) -> int:
        return len(self._comments)

    def count_titles(self) -> Counter:
        count = Counter()
        for comm in self._comments:
            count.update({comm.title: 1})
        return count

    def count_authors(self) -> Counter:
        count = Counter()
        for comm in self._comments:
            count.update({comm.author: 1})
        return count

    def count_comments(self) -> Counter:
        count = Counter()
        for comm in self._comments:
            count.update({comm.comment: 1})
        return count


def print_stats(stats: dict):
    msg = ""
    for key in stats.keys():
        msg += "[{key}: {val} ({percent:.2f}%)] ".format(key=key, val=stats[key], percent=stats[key]/stats["total"]*100)
    print("="*len(msg))
    print(msg)
    print("="*len(msg))


if __name__ == "__main__":
    db = commentdb.DBConnection("test.db")
    reader = Reader(db)
    reader.filter_repeats()

    # ===================================================================
    support_anon = len(reader.with_tag("support"))
    oppose_anon = len(reader.with_tag("oppose"))
    unknown_anon = len(reader) - support_anon - oppose_anon

    stats = {
        "support": support_anon,
        "oppose": oppose_anon,
        "unknown": unknown_anon,
        "total": support_anon + oppose_anon + unknown_anon
    }
    print_stats(stats)
    # ===================================================================
    support = len(reader.with_tag("support", False))
    oppose = len(reader.with_tag("support", False))
    unknown = len(reader) - reader.amount_anon() - support - oppose
    stats = {
        "support": support,
        "oppose": oppose,
        "unknown": unknown,
        "total": support + oppose + unknown
    }
    print_stats(stats)

    print("Titles: {}".format(str(reader.count_titles())))
    print("Authors: {}".format(str(reader.count_authors())))
