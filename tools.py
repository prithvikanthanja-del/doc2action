import re
from datetime import datetime


# ============================================================
# TOOL 1: DEADLINE EXTRACTION
# ============================================================

def extract_deadlines(text):

    patterns = [
        r"\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b",

        r"\b\d{1,2}\s+(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4}\b",

        r"\b\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{4}\b",

        r"\b(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2},?\s+\d{4}\b",

        r"\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{1,2},?\s+\d{4}\b"
    ]

    dates = []

    for pattern in patterns:

        matches = re.findall(
            pattern,
            text,
            re.IGNORECASE
        )

        for match in matches:

            match = match.strip()

            if match not in dates:
                dates.append(match)

    if not dates:
        return "No explicit dates found."

    return "\n".join(
        f"- {date}"
        for date in dates
    )


# ============================================================
# TOOL 2: REQUIREMENT EXTRACTION
# ============================================================

def extract_requirements(text):

    lines = text.splitlines()

    results = []

    keywords = [
        "required",
        "documents required",
        "documents needed",
        "documents",
        "submit",
        "submission",
        "eligibility",
        "eligible",
        "must",
        "mandatory",
        "bring",
        "upload",
        "apply",
        "application",
        "registration"
    ]

    for line in lines:

        line = line.strip()

        if not line:
            continue

        lower = line.lower()

        if any(
            keyword in lower
            for keyword in keywords
        ):

            if len(line) > 10:
                results.append(line)

    results = list(
        dict.fromkeys(results)
    )

    if not results:
        return "No obvious requirements found."

    return "\n".join(
        f"- {item}"
        for item in results[:40]
    )


# ============================================================
# TOOL 3: DOCUMENT STATISTICS
# ============================================================

def get_document_stats(text):

    words = len(text.split())

    characters = len(text)

    lines = len(
        text.splitlines()
    )

    return (
        f"Word count: {words}\n"
        f"Character count: {characters}\n"
        f"Line count: {lines}"
    )


# ============================================================
# TOOL 4: REQUIRED DOCUMENT CHECKLIST
# ============================================================

def build_document_checklist(text):

    checklist = [

        "Birth Certificate",

        "Community Certificate",

        "Nativity Certificate",

        "Income Certificate",

        "Aadhaar",

        "Entrance-exam marks/score",

        "Admission order",

        "Bonafide certificate",

        "Institution identity card",

        "+2 Mark sheet",

        "Bank passbook",

        "Fees paid receipts"
    ]

    lower_text = text.lower()

    results = []

    for item in checklist:

        if item.lower() in lower_text:

            results.append({
                "document": item,
                "status": "Required"
            })

    return results


# ============================================================
# TOOL 5: MANUAL DOCUMENT GAP CHECK
# ============================================================

def check_missing_documents(
    required_documents,
    user_documents
):

    user_documents_lower = [
        item.lower().strip()
        for item in user_documents
    ]

    results = []

    for required in required_documents:

        document_name = required["document"]

        found = False

        for user_doc in user_documents_lower:

            if (
                user_doc in document_name.lower()
                or document_name.lower() in user_doc
            ):

                found = True
                break

        if found:

            results.append({
                "document": document_name,
                "status": "Available"
            })

        else:

            results.append({
                "document": document_name,
                "status": "Missing"
            })

    return results


# ============================================================
# TOOL 6: IDENTIFY UPLOADED DOCUMENT
# ============================================================

def identify_document_type(text):

    lower = text.lower()

    patterns = {

        "Birth Certificate": [
            "birth certificate",
            "date of birth",
            "registration of birth"
        ],

        "Community Certificate": [
            "community certificate",
            "caste certificate"
        ],

        "Nativity Certificate": [
            "nativity certificate",
            "nativity"
        ],

        "Income Certificate": [
            "income certificate",
            "annual family income",
            "annual income"
        ],

        "Aadhaar": [
            "aadhaar",
            "uidai",
            "unique identification"
        ],

        "Entrance-exam marks/score": [
            "entrance examination",
            "entrance exam",
            "entrance score",
            "entrance marks"
        ],

        "Admission order": [
            "admission order",
            "order of admission"
        ],

        "Bonafide certificate": [
            "bonafide certificate",
            "bonafide student"
        ],

        "Institution identity card": [
            "identity card",
            "student id",
            "institution id",
            "college id"
        ],

        "+2 Mark sheet": [
            "higher secondary",
            "12th standard",
            "12th marks",
            "plus two",
            "+2 mark",
            "higher secondary marks"
        ],

        "Bank passbook": [
            "passbook",
            "account number",
            "ifsc",
            "bank account"
        ],

        "Fees paid receipts": [
            "fee receipt",
            "fees paid",
            "tuition fees",
            "fee payment",
            "fees receipt"
        ]
    }

    scores = {}

    for document_type, keywords in patterns.items():

        score = 0

        for keyword in keywords:

            if keyword in lower:
                score += 1

        if score > 0:
            scores[document_type] = score

    if not scores:
        return "Unknown document"

    return max(
        scores,
        key=scores.get
    )


# ============================================================
# TOOL 7: ANALYZE UPLOADED DOCUMENTS
# ============================================================

def analyze_uploaded_documents(
    uploaded_documents
):

    results = []

    for item in uploaded_documents:

        document_type = identify_document_type(
            item["text"]
        )

        results.append({
            "filename": item["filename"],
            "identified_as": document_type
        })

    return results


# ============================================================
# TOOL REGISTRY
# ============================================================

TOOL_DESCRIPTIONS = {

    "extract_deadlines":
        "Find dates and possible deadlines in the document.",

    "extract_requirements":
        "Find requirements, eligibility conditions and mandatory actions.",

    "build_document_checklist":
        "Identify supporting documents required by the document.",

    "get_document_stats":
        "Calculate basic document statistics.",

    "analyze_uploaded_documents":
        "Identify what uploaded supporting documents appear to represent."
}