import tomllib
import datetime

from pathlib import Path
from dataclasses import dataclass
from typing import List

@dataclass
class Entrie:
    day: int
    activity: str

class Document:
    date: datetime.datetime
    entries: List[Entrie]
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

    for entry in data.get("work", []):
        doc.entries.append(Entrie(
                day = entry["day"],
                activity = entry["role"]
            ))

    return doc
    
