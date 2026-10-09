import os
import sys
import shutil

from read import read, Document
from pathlib import Path

def main():
    # TODO: validate sys args
    document = read(sys.argv[1])

    # clone base prae files
    date_str = document.date.strftime("%Y-%m")

    for i in range(1, 2):
        clone_path = Path(sys.argv[2]).joinpath(f"Prae_{date_str}_{i}")
    while (True):
        if clone_path.exists:
            print(f"Prae files at \'{clone_path}\' already exist\nDo you want to overwrite? Else the program will be terminated. (y/N)")
        input = input()
        if (input.lower() in ["yes", "y"]):
            os.remove(clone_path)
            break
        elif (input in ["No", "N"]):
            return 1

    for i in range(1, 2):
        shutil.copyfile(Path(f"../base/Prae_BASE_{i}.ods"),
                        clone_path)

if __name__ == "__main__":
    main()
