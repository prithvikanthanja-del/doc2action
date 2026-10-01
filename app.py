import streamlit as st

from document_parser import extract_text
from agent import analyze_document
from test_documents import create_all_test_documents


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="Doc2Action",
    page_icon="📄",
    layout="wide"
)


# ============================================================
# HEADER
# ============================================================

st.title("📄 Doc2Action")

st.subheader(
    "Turn confusing documents into clear actions."
)

st.write(
    "An agentic document assistant that "
    "understands requirements, inspects evidence, "
    "identifies gaps and creates an action plan."
)


# ============================================================
# TEST DOCUMENT GENERATOR
# ============================================================

with st.expander(
    "🧪 Generate test documents"
):

    st.write(
        "Don't have supporting documents? "
        "Generate clearly labelled fake PDFs "
        "for testing."
    )

    if st.button(
        "🧪 Generate Test Documents"
    ):

        try:

            generated = create_all_test_documents()

            st.success(
                "Test documents generated."
            )

            for path in generated:

                st.code(path)

            st.info(
                "Open the test_documents folder "
                "inside your project."
            )

        except Exception as e:

            st.error(
                "Could not generate test documents."
            )

            st.exception(e)


st.divider()


# ============================================================
# MAIN DOCUMENT
# ============================================================

file = st.file_uploader(
    "📄 Upload requirement document",
    type=["pdf"],
    key="main_document"
)


if file:

    st.success(
        f"Requirement document: {file.name}"
    )


    # --------------------------------------------------------
    # PARSE
    # --------------------------------------------------------

    with st.spinner(
        "Reading requirement document..."
    ):

        text = extract_text(
            file
        )


    if not text.strip():

        st.error(
            "Could not extract text from this document."
        )

        st.stop()


    # --------------------------------------------------------
    # PREVIEW
    # --------------------------------------------------------

    with st.expander(
        "📄 View extracted document"
    ):

        st.text_area(
            "Extracted text",
            text,
            height=300
        )


    st.divider()


    # ========================================================
    # MANUAL DOCUMENT SELECTION
    # ========================================================

    st.subheader(
        "📂 Documents you already have"
    )

    st.write(
        "Optional: manually select documents "
        "you already possess."
    )


    document_options = [

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


    user_documents = st.multiselect(
        "Select available documents",
        document_options
    )


    st.divider()


    # ========================================================
    # SUPPORTING DOCUMENT UPLOAD
    # ========================================================

    st.subheader(
        "📤 Upload supporting documents"
    )

    st.write(
        "Upload PDFs of certificates, marksheets, "
        "passbooks, receipts, etc."
    )


    supporting_files = st.file_uploader(
        "Supporting PDF documents",
        type=["pdf"],
        accept_multiple_files=True,
        key="supporting_documents"
    )


    uploaded_documents = []


    if supporting_files:

        st.info(
            f"{len(supporting_files)} "
            "supporting document(s) uploaded."
        )


        for supporting_file in supporting_files:

            with st.spinner(
                f"Reading {supporting_file.name}..."
            ):

                supporting_text = extract_text(
                    supporting_file
                )


            if supporting_text.strip():

                uploaded_documents.append(
                    {
                        "filename": supporting_file.name,
                        "text": supporting_text
                    }
                )

            else:

                st.warning(
                    f"Could not extract text from "
                    f"{supporting_file.name}"
                )


    st.divider()


    # ========================================================
    # AGENT STATUS
    # ========================================================

    st.subheader(
        "🤖 Agent"
    )

    st.write(
        "The agent will decide which analysis "
        "tools are useful before generating "
        "the final action plan."
    )


    # ========================================================
    # RUN AGENT
    # ========================================================

    if st.button(
        "🚀 Run Doc2Action Agent",
        type="primary",
        use_container_width=True
    ):

        with st.spinner(
            "Agent is understanding, planning, "
            "using tools and reasoning..."
        ):

            try:

                result = analyze_document(

                    text=text,

                    user_documents=user_documents,

                    uploaded_documents=uploaded_documents

                )

                st.success(
                    "Agent analysis complete!"
                )

                st.markdown(
                    result
                )

            except Exception as e:

                st.error(
                    "Something went wrong."
                )

                st.exception(e)