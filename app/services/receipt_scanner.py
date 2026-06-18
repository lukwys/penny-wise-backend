import cv2
from cv2.typing import MatLike
import easyocr
from fastapi import UploadFile
import numpy as np

from app.exceptions import OcrError

reader = easyocr.Reader(lang_list=["pl"])


async def decode_image(uloaded_image: UploadFile) -> MatLike:
    image_bytes = await uloaded_image.read()
    image_buffer = np.frombuffer(image_bytes, np.uint8)
    image = cv2.imdecode(image_buffer, cv2.IMREAD_COLOR)

    if image is None:
        OcrError("Can't decode an image")

    return image


def order_points(pts):
    rect = np.zeros((4, 2), dtype=np.float32)
    sums = pts.sum(axis=1)
    diff = np.diff(pts, axis=1)
    rect[0] = pts[np.argmin(sums)]
    rect[2] = pts[np.argmax(sums)]
    rect[1] = pts[np.argmin(diff)]
    rect[3] = pts[np.argmax(diff)]
    return rect


def extract_receipt(image: MatLike):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (11, 11), 0)
    edges = cv2.Canny(blurred, 75, 200)
    kernel = np.ones((15, 15), np.uint8)
    dilated = cv2.dilate(edges, kernel, iterations=1)
    contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    contours = sorted(contours, key=cv2.contourArea, reverse=True)
    largestContour = contours[0]
    epsilon = 0.02 * cv2.arcLength(largestContour, True)
    approx = cv2.approxPolyDP(largestContour, epsilon, True)

    if len(approx) == 4:
        pts = approx.reshape(4, 2).astype(np.float32)
        width, height = 800, 1200
        dst = np.array(
            [[0, 0], [width, 0], [width, height], [0, height]], dtype=np.float32
        )

        homography_matrix = cv2.getPerspectiveTransform(order_points(pts), dst)
        warped = cv2.warpPerspective(image, homography_matrix, (width, height))
        return warped

    return image


async def preprocess_receipt_image(uloaded_image: UploadFile) -> np.ndarray:
    image = await decode_image(uloaded_image)

    return extract_receipt(image)


async def scan_receipt_text(receipt: UploadFile) -> list[str]:
    try:
        preprocesed_image = await preprocess_receipt_image(receipt)
        results = reader.readtext(preprocesed_image, ycenter_ths=0.3)
    except Exception as e:
        raise OcrError() from e

    if not results:
        raise OcrError("No text found in image")

    filtered_items = filter(lambda item: item[2] >= 0.3, results)
    sorted_items = sorted(filtered_items, key=lambda item: item[0][0][1])

    return [item[1] for item in sorted_items]
