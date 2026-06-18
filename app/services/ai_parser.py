import json
import re
import os
import anthropic
from abc import ABC, abstractmethod
from google import genai
from app.exceptions import ParsingError

RECEIPT_PARSE_PROMPT = (
    "You are a receipt parser. Extract all purchased items and their final prices from the following receipt text. "
    # "If any line with a negative value appears after an item, treat it as a discount and subtract it from the item's price, "
    "returning only the final price."
    'Return a JSON array where each element has "name" and "price" (as a number). '
    "Return only raw JSON array, no markdown, no code blocks, no explanation.\n\nReceipt:\n{scanned_text}"
)

genai_client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
anthropic_client = anthropic.Anthropic()


class AIParser(ABC):
    @abstractmethod
    def parse(self, scanned_text: str) -> list[dict]:
        pass


class GeminiParser(AIParser):
    def parse(self, scanned_text):
        try:
            response = genai_client.models.generate_content(
                model="gemini-3.5-flash",
                contents=RECEIPT_PARSE_PROMPT.format(
                    scanned_text="\n".join(scanned_text)
                ),
            )
        except Exception as e:
            raise ParsingError(e.message) from e

        return parse_response(response.text)


class ClaudeParser(AIParser):
    def parse(self, scanned_text):
        try:
            response = anthropic_client.messages.create(
                model="claude-haiku-4-5",
                max_tokens=1000,
                messages=[
                    {
                        "role": "user",
                        "content": RECEIPT_PARSE_PROMPT.format(
                            scanned_text="\n".join(scanned_text)
                        ),
                    }
                ],
            )
        except Exception as e:
            raise ParsingError(e.message) from e

        return parse_response(response.content[0].text)


def parse_response(text: str):
    try:
        text = re.sub(r"```(?:json)?\s*", "", text).strip()

        return json.loads(text)
    except json.JSONDecodeError as e:
        raise ParsingError("AI model returned an unexpected response format") from e


def get_parser():
    if os.getenv("AI_PROVIDER") == "anthropic":
        return ClaudeParser()
    else:
        return GeminiParser()
