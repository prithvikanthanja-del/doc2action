# 📄 Doc2Action

### Don't just understand the document. Know what to do next.

Doc2Action is an agentic document-to-action assistant that converts complex official documents into actionable plans.

Instead of simply summarizing a document, Doc2Action:

- Understands the document
- Identifies important requirements
- Extracts dates and possible deadlines
- Builds a required-document checklist
- Inspects uploaded supporting documents
- Identifies missing evidence
- Flags documents that require verification
- Produces a prioritized action plan

---

## 🎯 Problem

Official documents such as scholarship notifications, application forms, college circulars, banking documents and other administrative documents often contain important eligibility conditions, deadlines, required documents and procedural instructions.

However, users still need to manually determine:

- What applies to them
- What documents they need
- What documents they already have
- What is missing
- Which conditions require attention
- What they should do next

This creates a gap between having access to information and being able to act on it effectively.

---

## 💡 Solution

Doc2Action uses an agentic workflow to transform a document into an actionable plan.

### Agent workflow

```text
                    USER
                      │
                      ▼
              Upload Document
                      │
                      ▼
              Document Parser
                Text + OCR
                      │
                      ▼
               AI AGENT
          Understand + Plan
                      │
          ┌───────────┼───────────┐
          ▼           ▼           ▼
      Deadline    Requirement   Document
        Tool         Tool       Checklist
          │           │           │
          └───────────┼───────────┘
                      │
                      ▼
           Supporting Documents
                      │
                      ▼
             Evidence Analyzer
                      │
                      ▼
               Gap Detection
                      │
          ┌───────────┼───────────┐
          ▼           ▼           ▼
       Available    Missing   Needs Verification
                      │
                      ▼
              Final Reasoning
                      │
                      ▼
             ACTION PLAN