
from pathlib import Path
import uno

from com.sun.star.beans import PropertyValue
from read import Document


MONTHS = [
    "Jänner", "Februar", "März", "April", "Mai", "Juni",
    "Juli", "August", "September", "Oktober", "November", "Dezember"
]


def edit(document: Document, path: Path) -> None:
    editPrae1(document, path)


def editPrae1(document: Document, path: Path) -> None:
    file_path = path / f"{path.name}_1.ods"

    local_ctx = uno.getComponentContext()
    resolver = local_ctx.ServiceManager.createInstanceWithContext(
        "com.sun.star.bridge.UnoUrlResolver", local_ctx
    )

    ctx = resolver.resolve(
        "uno:socket,host=localhost,port=2002;"
        "urp;StarOffice.ComponentContext"
    )

    desktop = ctx.ServiceManager.createInstanceWithContext(
        "com.sun.star.frame.Desktop", ctx
    )

    doc_url = uno.systemPathToFileUrl(str(file_path.resolve()))

    properties = []
    prop = PropertyValue()
    prop.Name = "Hidden"
    prop.Value = True
    properties.append(prop)

    spreadsheet = desktop.loadComponentFromURL(
        doc_url, "_blank", 0, tuple(properties)
    )

    if spreadsheet is None:
        raise RuntimeError(f"Could not open spreadsheet: {file_path}")

    try:
        sheet = spreadsheet.Sheets.getByName(
            "PRAE_digitale Eingabe"
        )

        cell = sheet.getCellRangeByName("B11")
        cell.setString(MONTHS[document.date.month - 1])

        cell = sheet.getCellRangeByName("K11")
        cell.setString(document.date.year)

        for entrie in document.entries:
            x = parseX(3 * ((entrie.day - 1) % 10 + 1))
            y = (entrie.day - 1) // 10 + 12

            cell = sheet.getCellRangeByName(x + str(y))
            cell.setString();
        spreadsheet.store()
    finally:
        spreadsheet.close(True)

def parseX(n) -> str:
    result = ""

    while n > 0:
        n -= 1
        result = chr(ord('A') + n % 26) + result
        n //= 26

    return result
