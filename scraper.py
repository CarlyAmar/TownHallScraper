import requests
import bs4
import re
import comment
import commentdb
import argparse
import logging
import sys

TIMEOUT = 60


URL = "http://townhall.virginia.gov/L/Comments.cfm?GdocForumID=1953"


def get_comment_links():
    response = requests.get(URL, timeout=TIMEOUT*4)
    soup = bs4.BeautifulSoup(response.content, features="html.parser")
    link_strings = [row.contents[1] for row in soup.table if row != "\n"]
    links = []
    for ls in link_strings:
        m = re.findall("viewcomments\.cfm\?commentid=[0-9]+", str(ls))
        for match in m:
            links.append(match)
    return links


def parse_datetime(block: bs4.element.Tag) -> str:
    time_string = str(block.contents)
    regex = "[0-1]?[0-9]/[0-3]?[0-9]/22[\xa0 \t]+[0-1]?[0-9]:[0-5][0-9][\xa0 ]+[(a|p)]m"
    date_str = re.findall(regex, time_string)[0].replace("\xa0", " ")
    return date_str
    # return datetime.datetime.strptime("0"+date_str, '%m/%d/%y  %I:%M %p')


def parse_author(block: bs4.element.Tag) -> str:
    return str(block.contents).split("\r\n")[1].strip()


def parse_title(block: bs4.element.Tag) -> str:
    srch = '</?strong>'
    block_string = str(block.contents)
    line = block_string.split("\r\n")[2]
    begin = re.search(srch, line).span()[1]
    end = re.search(srch, line[begin:]).span()[0]
    line = line[begin:begin+end]
    return line


def parse_comment(block: bs4.element.Tag) -> str:
    comments = [x for x in block.find('div', {'class': 'divComment'}).contents if x != "\n"]
    return str(comments).replace('"', '').replace("'", "").replace(";", "")


def get_comment(url: str) -> dict:
    ret = {
        "url": url,
        "comment_id": int(url.split('=')[1])
    }
    response = requests.get("http://townhall.virginia.gov/L/{}".format(url), timeout=TIMEOUT)
    soup = bs4.BeautifulSoup(response.content, features="html.parser")
    cbox = soup.find('div', {'class': 'Cbox'})
    # print(str(cbox.contents))
    ret["date"] = parse_datetime(cbox)
    ret["author"] = parse_author(cbox)
    ret["title"] = parse_title(cbox)
    ret["comment"] = parse_comment(cbox)

    return ret


def test():
    db = commentdb.DBConnection("test.db")
    comments_idx = db.get_saved_comment_ids()
    print("Comment IDS: {}".format(str(comments_idx)))


def main():
    print("Getting links...")
    comment_links = get_comment_links()
    db = commentdb.DBConnection("test.db")
    print("Updating comments index...")
    comments_idx = db.get_saved_comment_ids()
    skipped = 0
    saved = 0
    oppose = 0
    support = 0
    unknown = 0
    scanning = False
    for lnk in reversed(comment_links):
        percent = (len(comments_idx)/len(comment_links))*100
        try:
            comment_id = int(lnk.split("=")[1])
            if comment_id in comments_idx:
                write_buffer("Scanning for new comments ({}/{})".format(skipped, len(comment_links)))
                skipped += 1
                scanning = True
                continue
            if scanning:
                scanning = False
                print()
            com = comment.Comment(get_comment(lnk))
            if "oppose" in com.title.lower():
                oppose += 1
            elif "support" in com.title.lower():
                support += 1
            else:
                unknown += 1
            print("Saving {percent:.2f}% [{comment_id} - {title} - {author}]".format(
                percent=percent, comment_id=com.comment_id, title=com.title, author=com.author
            ))
            db.insert_comment(com)
            comments_idx.add(comment_id)
            saved += 1
            if saved % 25 == 0:
                total = support + oppose + unknown
                msg = "Support: {} ({:.2f}%) Oppose: {} ({:.2f}%) Unknown: {} ({:.2f}%) Total: {}".format(
                    support, support/total*100, oppose, oppose/total*100, unknown, unknown/total*100, total
                )
                print("="*len(msg))
                print(msg)
                print("="*len(msg))
        except Exception as e:
            print("Could not finish saving comment: {} due to [{}: {}]".format(lnk, str(type(e)), str(e)))

    print("Done!")


def write_buffer(msg: str) -> None:
    sys.stdout.write("\r"+msg)
    sys.stdout.flush()


def get_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("mode", nargs="?", default="run", action="store", choices=["run", "test"])
    return parser.parse_args()


if __name__ == "__main__":
    args = get_args()
    try:
        if args.mode == "run":
            main()
        elif args.mode == "test":
            test()
        else:
            print("Could not recognize mode: {}".format(args.mode))
    except Exception as e:
        print("ERROR: [{}: {}]".format(str(type(e)), str(e)))

