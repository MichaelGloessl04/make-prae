import tomllib
import datetime

from pathlib import Path
from dataclasses import dataclass
from time import daylight
from typing import List

class Entrie:
    day: int
    activitie: str

class Document:
    date: datetime.datetime
    entries: List[Entrie]
    wage: int

    @property
    def entriesCount(self):
        return len(self.entries)


def read(path:str):
    File = Path(path)

    with File.open("rb") as config:
        data = tomllib.load(config)

    

    return 0
    
