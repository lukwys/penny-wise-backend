import json
import os

import easyocr
from fastapi import UploadFile
from google import genai

from app.exceptions import OcrError, ParsingError

reader = easyocr.Reader(lang_list=["pl"])
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

RECEIPT_PARSE_PROMPT = (
    "You are a receipt parser. Extract all purchased items and their prices from the following receipt text. "
    "Return a JSON array where each element has \"name\" and \"price\" (as a number). "
    "Return only the JSON, no explanation.\n\nReceipt:\n{scanned_text}"
)


async def scan_receipt_text(receipt: UploadFile) -> list[str]:
    try:
        results = reader.readtext(await receipt.read())
    except Exception as e:
        raise OcrError() from e

    if not results:
        raise OcrError("No text found in image")

    return [item[1] for item in results]


def generate_ai_content(scanned_text: str):
    try:
        response = client.models.generate_content(
            model="gemini-3.5-flash",
            contents=RECEIPT_PARSE_PROMPT.format(scanned_text=scanned_text)
        )
    except Exception as e:
        raise ParsingError("AI model did not return a response") from e

    try:
        return json.loads(response.text)

    except json.JSONDecodeError as e:
        raise ParsingError("AI model returned an unexpected response format") from e
