import subprocess
import tempfile
import time
from pathlib import Path

import uno
from com.sun.star.beans import PropertyValue

from read import Document


MONTHS = [
    "Jänner", "Februar", "März", "April", "Mai", "Juni",
    "Juli", "August", "September", "Oktober", "November", "Dezember",
]

WORK = {
    "coach": "Jugendtraining",
    "match": "Matchbetreuung",
    "tech": "Techniker",
}

UNO_URL = (
    "uno:socket,host=localhost,port=2002;"
    "urp;StarOffice.ComponentContext"
)


def property_value(name: str, value: object) -> PropertyValue:
    prop = PropertyValue()
    prop.Name = name
    prop.Value = value
    return prop


def connect_to_libreoffice(timeout: float = 30.0):
    local_ctx = uno.getComponentContext()
    resolver = local_ctx.ServiceManager.createInstanceWithContext(
        "com.sun.star.bridge.UnoUrlResolver",
        local_ctx,
    )

    deadline = time.monotonic() + timeout

    while time.monotonic() < deadline:
        try:
            return resolver.resolve(UNO_URL)
        except Exception:
            time.sleep(0.25)

    raise TimeoutError("LibreOffice UNO connection timed out")


def edit(document: Document, path: Path) -> None:
    with tempfile.TemporaryDirectory(prefix="lo-uno-") as profile:
        profile_url = uno.systemPathToFileUrl(profile)

        process = subprocess.Popen([
            "libreoffice",
            "--headless",
            "--nologo",
            "--nodefault",
            "--nofirststartwizard",
            f"-env:UserInstallation={profile_url}",
            "--accept=socket,host=localhost,port=2002;urp;"
            "StarOffice.ServiceManager",
        ])

        desktop = None

        try:
            deadline = time.monotonic() + 30.0

            while time.monotonic() < deadline:
                if process.poll() is not None:
                    raise RuntimeError(
                        f"LibreOffice exited with code {process.returncode}"
                    )

                try:
                    ctx = connect_to_libreoffice(timeout=0.5)
                    desktop = ctx.ServiceManager.createInstanceWithContext(
                        "com.sun.star.frame.Desktop",
                        ctx,
                    )
                    break
                except TimeoutError:
                    continue

            if desktop is None:
                raise TimeoutError("Could not connect to LibreOffice")

            editPrae1(document, path, desktop)
            editPrae2(document, path, desktop)

        finally:
            if desktop is not None:
                try:
                    desktop.terminate()
                except Exception:
                    pass

            try:
                process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                process.terminate()

                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait()


def edit_spreadsheet(
    file_path: Path,
    sheet_name: str,
    update,
) -> None:
    if not file_path.is_file():
        raise FileNotFoundError(file_path)

    ctx = connect_to_libreoffice()
    desktop = ctx.ServiceManager.createInstanceWithContext(
        "com.sun.star.frame.Desktop",
        ctx,
    )

    spreadsheet = desktop.loadComponentFromURL(
        uno.systemPathToFileUrl(str(file_path.resolve())),
        "_blank",
        0,
        (property_value("Hidden", True),),
    )

    if spreadsheet is None:
        raise RuntimeError(f"Could not open spreadsheet: {file_path}")

    try:
        sheet = spreadsheet.Sheets.getByName(sheet_name)
        update(sheet)
        spreadsheet.store()
    finally:
        spreadsheet.close(True)


def editPrae1(
    document: Document,
    path: Path,
    desktop=None,
) -> None:
    file_path = path / f"{path.name}_1.ods"

    def update(sheet) -> None:
        sheet.getCellRangeByName("B11").setString(
            MONTHS[document.date.month - 1]
        )
        sheet.getCellRangeByName("K11").setValue(document.date.year)

        for entry in document.entries:
            column = parseX(3 * ((entry.day - 1) % 10 + 1))
            row = (entry.day - 1) // 10 + 12

            sheet.getCellRangeByName(f"{column}{row}").setString(
                str(entry.Value)
            )

    edit_spreadsheet(file_path, "PRAE_digitale Eingabe", update)


def editPrae2(
    document: Document,
    path: Path,
    desktop=None,
) -> None:
    file_path = path / f"{path.name}_2.ods"

    def update(sheet) -> None:
        sheet.getCellRangeByName("C5").setString(
            f"{MONTHS[document.date.month - 1]} {document.date.year}"
        )

        for row, entry in enumerate(document.entries, start=8):
            sheet.getCellRangeByName(f"A{row}").setValue(entry.day)
            sheet.getCellRangeByName(f"B{row}").setString(
                str(entry.Value)
            )
            sheet.getCellRangeByName(f"C{row}").setString(
                WORK[entry.activity]
            )

    edit_spreadsheet(file_path, "Abrechnungsaufzeichnung PRAE", update)


def parseX(n: int) -> str:
    result = ""

    while n > 0:
        n -= 1
        result = chr(ord("A") + n % 26) + result
        n //= 26

    return result
