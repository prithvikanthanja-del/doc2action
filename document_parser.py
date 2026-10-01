import fitz
import pytesseract
from PIL import Image
import io


pytesseract.pytesseract.tesseract_cmd = (
    r"C:\Program Files\Tesseract-OCR\tesseract.exe"
)


def extract_text(file):

    data = file.read()

    doc = fitz.open(
        stream=data,
        filetype="pdf"
    )

    text = ""

    for i, page in enumerate(doc):

        page_text = page.get_text(
            "text"
        ).strip()

        if page_text:

            print(
                f"Page {i + 1}: "
                f"{len(page_text)} characters"
            )

            text += (
                f"\n--- Page {i + 1} ---\n"
                f"{page_text}\n"
            )

        else:

            print(
                f"Page {i + 1}: "
                "No text found. Running OCR..."
            )

            pix = page.get_pixmap(
                matrix=fitz.Matrix(2, 2)
            )

            img = Image.open(
                io.BytesIO(
                    pix.tobytes("png")
                )
            )

            ocr_text = pytesseract.image_to_string(
                img
            ).strip()

            text += (
                f"\n--- Page {i + 1} ---\n"
                f"{ocr_text}\n"
            )

    return text.strip()