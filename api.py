import tempfile
from typing import Optional

from fastapi import FastAPI, File, Form, UploadFile
from fastapi.responses import JSONResponse

from document_parser import extract_text
from agent import analyze_document


app = FastAPI(
    title="Doc2Action API",
    description=(
        "Agentic document-to-action assistant "
        "for converting complex documents into "
        "actionable plans."
    ),
    version="1.0.0"
)


# ============================================================
# ROOT
# ============================================================

@app.get("/")
def root():

    return {
        "name": "Doc2Action",
        "description": (
            "Agentic document-to-action assistant"
        ),
        "status": "online",
        "endpoint": "/analyze"
    }


# ============================================================
# HEALTH CHECK
# ============================================================

@app.get("/health")
def health():

    return {
        "status": "healthy"
    }


# ============================================================
# MAIN ANALYSIS ENDPOINT
# ============================================================

@app.post("/analyze")
async def analyze(

    # --------------------------------------------------------
    # MAIN REQUIREMENT DOCUMENT
    # --------------------------------------------------------

    requirement_document: UploadFile = File(...),

    # --------------------------------------------------------
    # DOCUMENTS USER SAYS THEY ALREADY HAVE
    # --------------------------------------------------------

    available_documents: str = Form(
        default=""
    ),

    # --------------------------------------------------------
    # OPTIONAL SUPPORTING DOCUMENTS
    #
    # Using separate fields avoids Swagger/OpenAPI
    # representing UploadFile lists incorrectly.
    # --------------------------------------------------------

    supporting_document_1: Optional[
        UploadFile
    ] = File(default=None),

    supporting_document_2: Optional[
        UploadFile
    ] = File(default=None),

    supporting_document_3: Optional[
        UploadFile
    ] = File(default=None),

    supporting_document_4: Optional[
        UploadFile
    ] = File(default=None),

    supporting_document_5: Optional[
        UploadFile
    ] = File(default=None)
):

    try:

        # ====================================================
        # VALIDATE MAIN REQUIREMENT DOCUMENT
        # ====================================================

        if not requirement_document.filename:

            return JSONResponse(
                status_code=400,
                content={
                    "status": "error",
                    "error": (
                        "Requirement document "
                        "filename is missing."
                    )
                }
            )


        if not requirement_document.filename.lower().endswith(
            ".pdf"
        ):

            return JSONResponse(
                status_code=400,
                content={
                    "status": "error",
                    "error": (
                        "Requirement document "
                        "must be a PDF."
                    )
                }
            )


        # ====================================================
        # READ REQUIREMENT DOCUMENT
        # ====================================================

        requirement_bytes = (
            await requirement_document.read()
        )


        if not requirement_bytes:

            return JSONResponse(
                status_code=400,
                content={
                    "status": "error",
                    "error": (
                        "Requirement document "
                        "is empty."
                    )
                }
            )


        # ====================================================
        # EXTRACT REQUIREMENT DOCUMENT TEXT
        # ====================================================

        requirement_file = (
            tempfile.SpooledTemporaryFile()
        )

        requirement_file.write(
            requirement_bytes
        )

        requirement_file.seek(0)


        requirement_text = extract_text(
            requirement_file
        )


        if not requirement_text.strip():

            return JSONResponse(
                status_code=422,
                content={
                    "status": "error",
                    "error": (
                        "Could not extract text "
                        "from the requirement document."
                    )
                }
            )


        # ====================================================
        # PARSE MANUALLY SELECTED DOCUMENTS
        # ====================================================

        user_documents = []


        if available_documents:

            user_documents = [

                item.strip()

                for item in
                available_documents.split(",")

                if item.strip()
            ]


        # ====================================================
        # COLLECT SUPPORTING DOCUMENTS
        # ====================================================

        supporting_files = [

            supporting_document_1,

            supporting_document_2,

            supporting_document_3,

            supporting_document_4,

            supporting_document_5
        ]


        uploaded_documents = []


        # ====================================================
        # PROCESS EACH SUPPORTING DOCUMENT
        # ====================================================

        for supporting_file in supporting_files:

            if supporting_file is None:
                continue


            if not supporting_file.filename:
                continue


            # Only PDFs are accepted.

            if not supporting_file.filename.lower().endswith(
                ".pdf"
            ):
                continue


            supporting_bytes = (
                await supporting_file.read()
            )


            if not supporting_bytes:
                continue


            # ------------------------------------------------
            # Create temporary file
            # ------------------------------------------------

            supporting_temp = (
                tempfile.SpooledTemporaryFile()
            )


            supporting_temp.write(
                supporting_bytes
            )


            supporting_temp.seek(0)


            # ------------------------------------------------
            # Extract text / OCR
            # ------------------------------------------------

            supporting_text = extract_text(
                supporting_temp
            )


            # ------------------------------------------------
            # Store extracted document
            # ------------------------------------------------

            if supporting_text.strip():

                uploaded_documents.append(
                    {
                        "filename":
                            supporting_file.filename,

                        "text":
                            supporting_text
                    }
                )


        # ====================================================
        # RUN DOC2ACTION AGENT
        # ====================================================

        result = analyze_document(

            text=requirement_text,

            user_documents=user_documents,

            uploaded_documents=uploaded_documents
        )


        # ====================================================
        # RETURN API RESPONSE
        # ====================================================

        return {

            "status": "success",

            "agent": "Doc2Action",

            "result": result
        }


    except Exception as e:

        # ====================================================
        # UNEXPECTED ERROR
        # ====================================================

        return JSONResponse(

            status_code=500,

            content={

                "status": "error",

                "error": str(e)
            }
        )