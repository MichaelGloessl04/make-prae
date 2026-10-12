import tomllib
import datetime

from pathlib import Path

MILEAGE_RATE = 0.2

class Entrie:
    id: int
    day: int
    activity: str
    kilometers: int
    parent_doc: Document

    def __init__(self, id: int, day: int, activity: str, parent_doc: Document, kilometer: int | None = None) -> None:
        self.id = id
        self.day = day
        self.activity = activity
        self.parent_doc = parent_doc
        if kilometer:
            self.kilometers = kilometer
        else:
            kilometer = 0

    @property
    def Value(self) -> int:
        base = self.parent_doc.wage // self.parent_doc.entriesCount
        remainder = self.parent_doc.wage % self.parent_doc.entriesCount

        return int(base + (1 if self.id < remainder else 0) + self.kilometers * MILEAGE_RATE)

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
        km = None
        if "km" in entry:
            km = entry["km"]
        doc.entries.append(Entrie(i, entry["day"], entry["role"], doc, km))

    return doc
    
