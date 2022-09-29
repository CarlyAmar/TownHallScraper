import datetime
import json
from json import JSONEncoder


class Comment:
    def __init__(self, config: dict):
        self._config = config
        for key in self._config.keys():
            if type(self._config[key]) is str:
                self._config[key] = self._sanitize(self._config[key])

    @property
    def comment_id(self) -> int:
        return self._config["comment_id"]

    @property
    def url(self) -> str:
        return self._config["url"]

    @property
    def date(self) -> str:
        return self._config["date"]

    @property
    def author(self) -> str:
        return self._config["author"]

    @property
    def title(self) -> str:
        return self._config["title"]

    @property
    def comment(self) -> str:
        return self._config["comment"].replace("'", "").replace('"', '')

    def datetime(self) -> datetime.datetime:
        return datetime.datetime.strptime("0"+self.date, '%m/%d/%y  %I:%M %p')

    def __str__(self) -> str:
        return json.dumps(self.json(), indent=4)

    def json(self) -> dict:
        return self._config.copy()

    def is_anon(self) -> bool:
        return self.author == "Anonymous"

    @staticmethod
    def _sanitize(string: str):
        return string.replace('"', '').replace("'", "").strip().replace(".", "").replace("!", "")

    # subclass JSONEncoder
    class _DateTimeEncoder(JSONEncoder):
        # Override the default method
        def default(self, obj):
            if isinstance(obj, (datetime.date, datetime.datetime)):
                return obj.isoformat()

