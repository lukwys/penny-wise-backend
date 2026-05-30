import easyocr
from fastapi import UploadFile

reader = easyocr.Reader(lang_list=["pl"])


async def scan_receipt_text(receipt: UploadFile):
    results = reader.readtext(await receipt.read())

    return [item[1] for item in results]
