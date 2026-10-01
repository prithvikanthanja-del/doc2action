import os
import re

from groq import Groq
from dotenv import load_dotenv

from tools import (
    extract_deadlines,
    extract_requirements,
    get_document_stats,
    build_document_checklist,
    check_missing_documents,
    analyze_uploaded_documents,
    TOOL_DESCRIPTIONS
)


# ============================================================
# GROQ SETUP
# ============================================================

load_dotenv()

client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)

MODEL = "openai/gpt-oss-120b"


# ============================================================
# TOOL EXECUTION
# ============================================================

def execute_tool(
    tool_name,
    text,
    uploaded_documents
):

    if tool_name == "extract_deadlines":

        return extract_deadlines(
            text
        )

    if tool_name == "extract_requirements":

        return extract_requirements(
            text
        )

    if tool_name == "build_document_checklist":

        return build_document_checklist(
            text
        )

    if tool_name == "get_document_stats":

        return get_document_stats(
            text
        )

    if tool_name == "analyze_uploaded_documents":

        return analyze_uploaded_documents(
            uploaded_documents
        )

    return "Unknown tool."


# ============================================================
# AGENT TOOL DECISION
# ============================================================

def choose_next_tool(
    text,
    previous_results,
    has_uploaded_documents
):

    previous_tools = list(
        previous_results.keys()
    )

    available_tools = list(
        TOOL_DESCRIPTIONS.keys()
    )

    tool_text = "\n".join(
        [
            f"- {name}: {description}"
            for name, description
            in TOOL_DESCRIPTIONS.items()
        ]
    )

    previous_text = "\n".join(
        [
            f"- {name}"
            for name in previous_tools
        ]
    )

    if not previous_text:

        previous_text = "None"


    prompt = f"""
You are the planning component of Doc2Action.

You must decide what tool the agent should use next.

AVAILABLE TOOLS:

{tool_text}


TOOLS ALREADY USED:

{previous_text}


USER UPLOADED SUPPORTING DOCUMENTS:

{has_uploaded_documents}


DOCUMENT:

{text[:12000]}


Choose exactly ONE tool from this list:

extract_deadlines
extract_requirements
build_document_checklist
get_document_stats
analyze_uploaded_documents
DONE

Rules:

- Do not choose a tool that has already been used.
- If uploaded documents exist, analyze_uploaded_documents
  should be used.
- The agent should prioritize information needed to
  produce an actionable result.
- If all useful tools have been used, return DONE.

Return ONLY the tool name.
"""


    response = client.chat.completions.create(

        model=MODEL,

        messages=[
            {
                "role": "system",
                "content": (
                    "You are a tool-selection planner. "
                    "Return only one tool name."
                )
            },

            {
                "role": "user",
                "content": prompt
            }
        ],

        temperature=0,

        max_completion_tokens=50
    )


    answer = (
        response
        .choices[0]
        .message
        .content
        .strip()
    )


    # ----------------------------------------
    # Extract a valid tool name
    # ----------------------------------------

    for tool in available_tools:

        if tool in answer:

            return tool


    if "DONE" in answer.upper():

        return "DONE"


    return "DONE"


# ============================================================
# MAIN AGENT
# ============================================================

def analyze_document(
    text,
    user_documents=None,
    uploaded_documents=None
):

    if user_documents is None:
        user_documents = []

    if uploaded_documents is None:
        uploaded_documents = []


    # ========================================================
    # AGENT STATE
    # ========================================================

    tool_results = {}

    agent_log = []


    # ========================================================
    # AGENT LOOP
    # ========================================================

    max_steps = 5

    for step in range(max_steps):

        next_tool = choose_next_tool(
            text=text,
            previous_results=tool_results,
            has_uploaded_documents=bool(
                uploaded_documents
            )
        )


        # --------------------------------------------
        # Agent decides it is finished
        # --------------------------------------------

        if next_tool == "DONE":

            agent_log.append(
                f"Step {step + 1}: "
                "Agent decided no additional tool was needed."
            )

            break


        # --------------------------------------------
        # Execute selected tool
        # --------------------------------------------

        agent_log.append(
            f"Step {step + 1}: "
            f"Agent selected `{next_tool}`."
        )


        result = execute_tool(
            tool_name=next_tool,
            text=text,
            uploaded_documents=uploaded_documents
        )


        tool_results[next_tool] = result


        agent_log.append(
            f"Step {step + 1}: "
            f"Executed `{next_tool}` successfully."
        )


    # ========================================================
    # SAFETY FALLBACK
    # ========================================================

    # If the planner stopped early, make sure the
    # essential tools have still been executed.

    if "extract_deadlines" not in tool_results:

        tool_results["extract_deadlines"] = (
            extract_deadlines(text)
        )

        agent_log.append(
            "Fallback: deadline extraction executed."
        )


    if "extract_requirements" not in tool_results:

        tool_results["extract_requirements"] = (
            extract_requirements(text)
        )

        agent_log.append(
            "Fallback: requirement extraction executed."
        )


    if "build_document_checklist" not in tool_results:

        tool_results["build_document_checklist"] = (
            build_document_checklist(text)
        )

        agent_log.append(
            "Fallback: document checklist generated."
        )


    # ========================================================
    # REQUIRED DOCUMENTS
    # ========================================================

    checklist = tool_results[
        "build_document_checklist"
    ]


    # ========================================================
    # MANUAL DOCUMENT GAP CHECK
    # ========================================================

    manual_status = check_missing_documents(
        checklist,
        user_documents
    )


    # ========================================================
    # UPLOADED DOCUMENT ANALYSIS
    # ========================================================

    if uploaded_documents:

        if "analyze_uploaded_documents" in tool_results:

            uploaded_status = tool_results[
                "analyze_uploaded_documents"
            ]

        else:

            uploaded_status = analyze_uploaded_documents(
                uploaded_documents
            )

            agent_log.append(
                "Fallback: uploaded documents analyzed."
            )

    else:

        uploaded_status = []


    # ========================================================
    # DOCUMENT STATISTICS
    # ========================================================

    if "get_document_stats" in tool_results:

        stats = tool_results[
            "get_document_stats"
        ]

    else:

        stats = get_document_stats(
            text
        )


    # ========================================================
    # FORMAT RESULTS
    # ========================================================

    deadlines = tool_results[
        "extract_deadlines"
    ]

    requirements = tool_results[
        "extract_requirements"
    ]


    # Required documents

    if checklist:

        checklist_text = "\n".join(
            [
                f"- {item['document']}"
                for item in checklist
            ]
        )

    else:

        checklist_text = (
            "No predefined document "
            "checklist items detected."
        )


    # Manual documents

    if user_documents:

        manual_documents_text = "\n".join(
            [
                f"- {item}"
                for item in user_documents
            ]
        )

    else:

        manual_documents_text = (
            "No manually selected documents."
        )


    # Manual status

    if manual_status:

        manual_status_text = "\n".join(
            [
                f"- {item['document']}: "
                f"{item['status']}"
                for item in manual_status
            ]
        )

    else:

        manual_status_text = (
            "No manual comparison performed."
        )


    # Uploaded status

    if uploaded_status:

        uploaded_status_text = "\n".join(
            [
                f"- {item['filename']} "
                f"→ {item['identified_as']}"
                for item in uploaded_status
            ]
        )

    else:

        uploaded_status_text = (
            "No supporting documents uploaded."
        )


    # Uploaded content

    uploaded_text = ""

    for item in uploaded_documents:

        uploaded_text += f"""

FILE:
{item['filename']}

CONTENT:
{item['text']}

--------------------------------
"""


    # Agent log

    agent_log_text = "\n".join(
        [
            f"- {item}"
            for item in agent_log
        ]
    )


    # Tools actually used

    tools_used_text = "\n".join(
        [
            f"- {tool}"
            for tool in tool_results.keys()
        ]
    )


    # ========================================================
    # FINAL REASONING
    # ========================================================

    final_prompt = f"""
You are the final reasoning engine of Doc2Action.

The Doc2Action agent has already:

1. Read the document.
2. Decided which analysis tools to use.
3. Executed those tools.
4. Collected evidence.
5. Compared user-provided documents.

Now reason over all collected information and
produce the final actionable result.


========================================
ORIGINAL DOCUMENT
========================================

{text}


========================================
DEADLINES
========================================

{deadlines}


========================================
REQUIREMENTS
========================================

{requirements}


========================================
REQUIRED DOCUMENT CHECKLIST
========================================

{checklist_text}


========================================
MANUALLY SELECTED DOCUMENTS
========================================

{manual_documents_text}


========================================
MANUAL DOCUMENT STATUS
========================================

{manual_status_text}


========================================
UPLOADED DOCUMENTS
========================================

{uploaded_status_text}


========================================
UPLOADED DOCUMENT CONTENT
========================================

{uploaded_text}


========================================
DOCUMENT STATISTICS
========================================

{stats}


========================================
AGENT DECISION LOG
========================================

{agent_log_text}


========================================
TOOLS USED
========================================

{tools_used_text}


IMPORTANT RULES:

- Never invent facts.
- Never invent deadlines.
- Do not call an academic year a deadline.
- Do not claim a document is authentic.
- A recognized uploaded document is evidence only.
- If authenticity or validity cannot be determined,
  say "Needs Verification".
- If no supporting document was found,
  say "Missing".
- Preserve conditions from the original document.
- Distinguish explicit information from inference.


Return:


## 📄 Document

Identify the document.


## 📝 Summary

Explain its purpose.


## 📅 Deadlines

List dates and explain what each date represents.

If there is no explicit submission deadline:

**Submission deadline: Not specified.**


## 📋 Requirements

List important requirements.


## 📎 Required Documents

List required supporting documents.


## 🔍 Evidence Check

For each important document:

✅ Available

❌ Missing

⚠️ Needs Verification


## 📂 Uploaded Documents

Show each uploaded document and
what it appears to represent.


## ⚠️ Important Conditions

Highlight conditions that need attention.


## 🎯 Actions

Explain what the user should do.


## 🔥 Priority

### HIGH

Essential actions.

### MEDIUM

Important preparation or verification.

### LOW

Useful follow-up.


## ✅ Next Steps

Give a clear sequence of actions.


## 🤖 Agent Reasoning

Explain briefly:

1. What the agent decided to inspect.
2. Which tools it used.
3. What evidence it found.
4. How it identified gaps.
5. How it generated the action plan.

Do not claim that the agent performed
anything that is not present in the log.
"""


    # ========================================================
    # FINAL GROQ CALL
    # ========================================================

    response = client.chat.completions.create(

        model=MODEL,

        messages=[
            {
                "role": "system",
                "content": (
                    "You are the final reasoning engine "
                    "of Doc2Action. "
                    "Be accurate, cautious and practical."
                )
            },

            {
                "role": "user",
                "content": final_prompt
            }
        ],

        temperature=0.2,

        max_completion_tokens=4000
    )


    return response.choices[0].message.content