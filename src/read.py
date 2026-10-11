import tomllib
import datetime

from pathlib import Path

class Entrie:
    id: int
    day: int
    activity: str
    parent_doc: Document

    def __init__(self, id: int, day: int, activity: str, parent_doc: Document) -> None:
        self.id = id
        self.day = day
        self.activity = activity
        self.parent_doc = parent_doc

    @property
    def Value(self) -> int:
        base = self.parent_doc.wage // self.parent_doc.entriesCount
        remainder = self.parent_doc.wage % self.parent_doc.entriesCount

        return base + (1 if self.id < remainder else 0)

class Document:
    date: datetime.datetime
    entries: list[Entrie]
    wage: int

    def __init__(self, date:datetime.datetime, wage: int):
        self.date = date
        self.wage = wage
        self.entries = []

    @property
    def entriesCount(self):
        return len(self.entries)


def read(path:str) -> Document:
    File = Path(path)
    
    if not File.exists():
        raise Exception("Oh nein")

    with File.open("rb") as config:
        data = tomllib.load(config)

    date = datetime.datetime.strptime(File.stem, "%Y-%m")
    doc = Document(date, data["wage"])

    for i,entry in enumerate(data.get("work", [])):
        doc.entries.append(Entrie(i, entry["day"], entry["role"], doc))

    return doc
    
