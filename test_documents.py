from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from pathlib import Path


TEST_FOLDER = Path("test_documents")


def create_test_pdf(filename, title, lines):

    TEST_FOLDER.mkdir(
        exist_ok=True
    )

    path = TEST_FOLDER / filename

    c = canvas.Canvas(
        str(path),
        pagesize=A4
    )

    width, height = A4

    # Header
    c.setFont(
        "Helvetica-Bold",
        18
    )

    c.drawString(
        20 * mm,
        height - 25 * mm,
        "TEST DOCUMENT"
    )

    c.setFont(
        "Helvetica-Bold",
        14
    )

    c.drawString(
        20 * mm,
        height - 38 * mm,
        title
    )

    # Warning
    c.setFont(
        "Helvetica-Bold",
        11
    )

    c.drawString(
        20 * mm,
        height - 52 * mm,
        "NOT A REAL DOCUMENT - FOR SOFTWARE TESTING ONLY"
    )

    # Content
    y = height - 75 * mm

    c.setFont(
        "Helvetica",
        11
    )

    for line in lines:

        c.drawString(
            25 * mm,
            y,
            line
        )

        y -= 10 * mm

        if y < 25 * mm:

            c.showPage()

            y = height - 25 * mm

            c.setFont(
                "Helvetica",
                11
            )

    c.save()

    return str(path)


def create_all_test_documents():

    documents = []

    documents.append(
        create_test_pdf(
            "test_aadhaar.pdf",
            "AADHAAR CARD",
            [
                "TEST AADHAAR DOCUMENT",
                "Name: Test Student",
                "Date of Birth: 01-01-2005",
                "Aadhaar Number: XXXX XXXX XXXX",
                "Unique Identification Authority",
                "Address: Test Address",
                "This document is only for testing."
            ]
        )
    )

    documents.append(
        create_test_pdf(
            "test_community_certificate.pdf",
            "COMMUNITY CERTIFICATE",
            [
                "COMMUNITY CERTIFICATE",
                "Name: Test Student",
                "Community: BC",
                "Caste: Test Community",
                "Certificate Number: TEST-12345",
                "Issued for software testing.",
                "This is not an official certificate."
            ]
        )
    )

    documents.append(
        create_test_pdf(
            "test_marksheet.pdf",
            "HIGHER SECONDARY MARK SHEET",
            [
                "HIGHER SECONDARY EXAMINATION",
                "Name: Test Student",
                "12th Standard Mark Sheet",
                "Tamil: 85",
                "English: 82",
                "Mathematics: 91",
                "Physics: 88",
                "Chemistry: 86",
                "Computer Science: 94",
                "Total Marks: 526",
                "This document is only for testing."
            ]
        )
    )

    documents.append(
        create_test_pdf(
            "test_bank_passbook.pdf",
            "BANK PASSBOOK",
            [
                "BANK PASSBOOK",
                "Account Holder: Test Student",
                "Bank: Test Bank",
                "Branch: Test Branch",
                "Account Number: XXXX1234",
                "IFSC: TEST0001234",
                "This document is only for testing."
            ]
        )
    )

    return documents