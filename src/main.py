import os
import sys
import shutil

from read import read
from editOsd import edit
from pathlib import Path

def main():
    document = read(sys.argv[1])
    path = cloneBase(document.date.strftime("%Y-%m"))
    if not path:
        return 1
    edit(document, path)

def cloneBase(date):
    output_dir = Path(sys.argv[2]).expanduser()
    clone_path = output_dir / f"Prae_{date}"

    if checkPraePathExists(clone_path):
        print(f"Prae already exists under path: '{clone_path}'")
        answer = input("Overwrite? [y/N]: ").strip().lower()

        if answer not in ("y", "yes"):
            return ""

        shutil.rmtree(clone_path)

    clone_path.mkdir(parents=True, exist_ok=True)

    for i in range(1, 3):
        source = (
            Path(__file__).resolve().parent.parent
            / "base"
            / f"Prae_BASE_{i}.ods"
        )

        destination = clone_path / f"Prae_{date}_{i}.ods"

        shutil.copyfile(source, destination)

    return clone_path


def checkPraePathExists(path: Path) -> bool:
    return path.exists() and any(path.glob("*.ods"))

if __name__ == "__main__":
    main()
