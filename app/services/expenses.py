import easyocr
from fastapi import UploadFile

from app.exceptions import OcrError

reader = easyocr.Reader(lang_list=["pl"])


async def scan_receipt_text(receipt: UploadFile) -> list[str]:
    try:
        results = reader.readtext(await receipt.read(), ycenter_ths=0.3)
    except Exception as e:
        raise OcrError() from e

    if not results:
        raise OcrError("No text found in image")

    filtered_items = filter(lambda item: item[2] >= 0.5, results)
    sorted_items = sorted(filtered_items, key=lambda item: item[0][0][1])

    threshold = 40

    rows = []

    for item in sorted_items:
        item_y = item[0][0][1]

        if not rows or item_y - int(rows[-1][0][0][0][1]) > threshold:
            rows.append([item])
        else:
            rows[-1].append(item)

    return [item[1] for item in sorted_items]
