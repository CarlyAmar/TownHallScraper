import requests
import bs4
import re
import comment
import commentdb


URL = "http://townhall.virginia.gov/L/Comments.cfm?GdocForumID=1953"


def get_comment_links():
    response = requests.get(URL)
    soup = bs4.BeautifulSoup(response.content)
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
    response = requests.get("http://townhall.virginia.gov/L/{}".format(url))
    soup = bs4.BeautifulSoup(response.content)
    cbox = soup.find('div', {'class': 'Cbox'})
    # print(str(cbox.contents))
    ret["date"] = parse_datetime(cbox)
    ret["author"] = parse_author(cbox)
    ret["title"] = parse_title(cbox)
    ret["comment"] = parse_comment(cbox)

    return ret


def test():
    comment_links = get_comment_links()
    for lnk in comment_links:
        print("LINK: [{}]".format(lnk))

    com_dict = get_comment(comment_links[0])
    print(str(com_dict))
    com = comment.Comment(com_dict)
    print("Comment: {}".format(str(com)))
    conn = commentdb.DBConnection("test.db")
    conn.insert_comment(com)
    print("Getting Comment:")
    print(conn.get_comment(com.comment_id))


def main():
    comment_links = get_comment_links()
    db = commentdb.DBConnection("test.db")
    for lnk in comment_links:
        com = comment.Comment(get_comment(lnk))
        print("Saving [{comment_id} - {title} - {author}]".format(
            comment_id=com.comment_id, title=com.title, author=com.author
        ))
        db.insert_comment(com)

    print("Done!")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print("ERROR: [{}: {}]".format(str(type(e)), str(e)))

