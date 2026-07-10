"""
Step 2: The core agent.

Given a pandas DataFrame and a plain-English question, this asks Gemini
to write a Python function that computes the answer.

We don't execute anything here yet — that's Step 3 (the sandbox).
This file's only job is: question + data shape -> generated code (as text).
"""

import os
import pandas as pd
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

llm = ChatGoogleGenerativeAI(
    model="gemini-flash-latest",
    google_api_key=os.getenv("GOOGLE_API_KEY"),
    temperature=0,  # deterministic code generation, not creative writing
)


CODE_GEN_PROMPT = """You are a senior data analyst who writes clean, correct Python/Pandas code.

You will be given:
1. The columns and data types of a pandas DataFrame called `df`
2. A sample of the first few rows
3. A question in plain English

Your job: write a Python function called `analyze(df)` that answers the question.

Rules:
- The function MUST be named `analyze` and take one argument `df`.
- Return a dictionary with exactly these keys:
    - "result": the computed answer (a number, string, or small DataFrame)
    - "chart_type": one of "bar", "line", "none"
    - "chart_data": a pandas DataFrame or Series suitable for plotting (or None if chart_type is "none")
- Use ONLY pandas, numpy, and built-in Python. Do not import anything else.
- Do NOT read files or access the network. `df` is already loaded and passed in.
- Do NOT include explanations, markdown, or comments outside the function.
- Output ONLY the raw Python code, nothing else — no ```python fences, no prose.

DataFrame columns and types:
{schema}

Sample rows:
{sample}

Question: {question}
"""


def _extract_text(response) -> str:
    """
    Different Gemini model versions return response.content in different
    shapes: sometimes a plain string, sometimes a list of content blocks
    (e.g. [{"type": "text", "text": "..."}]). This normalizes both into
    a plain string so the rest of the code doesn't need to care which
    model version is behind the alias.
    """
    content = response.content

    if isinstance(content, str):
        return content.strip()

    if isinstance(content, list):
        parts = []
        for block in content:
            if isinstance(block, str):
                parts.append(block)
            elif isinstance(block, dict) and "text" in block:
                parts.append(block["text"])
        return "".join(parts).strip()

    # Fallback: whatever it is, stringify it rather than crash
    return str(content).strip()


def _strip_imports(code: str) -> str:
    """
    The model sometimes adds `import pandas as pd` / `import numpy as np`
    despite instructions not to. Our sandbox already provides pd and np
    as globals and blocks __import__ for safety, so these lines would
    otherwise cause an avoidable ImportError. Strip them here rather
    than wasting a whole self-correction cycle on something trivial.
    """
    lines = code.split("\n")
    cleaned = [
        line for line in lines
        if not line.strip().startswith("import ")
        and not line.strip().startswith("from ")
    ]
    return "\n".join(cleaned).strip()


def generate_code(df: pd.DataFrame, question: str) -> str:
    """
    Ask Gemini to write an `analyze(df)` function that answers `question`.
    Returns the generated code as a plain string (not yet executed).
    """
    schema = "\n".join(f"- {col}: {dtype}" for col, dtype in df.dtypes.items())
    sample = df.head(3).to_string()

    prompt = CODE_GEN_PROMPT.format(schema=schema, sample=sample, question=question)

    response = llm.invoke(prompt)
    code = _extract_text(response)

    # Safety net: strip markdown fences if the model adds them despite instructions
    if code.startswith("```"):
        code = code.split("```")[1]
        if code.startswith("python"):
            code = code[len("python"):]
        code = code.strip()

    code = _strip_imports(code)

    return code


FIX_PROMPT = """You are a senior data analyst debugging your own Python/Pandas code.

Your previous code failed. You will be given:
1. The DataFrame's columns and types
2. The original question
3. The code you wrote that failed
4. The exact error it produced
5. Relevant excerpts from the official Pandas documentation to help you fix it

Your job: write a corrected `analyze(df)` function that fixes the error and correctly
answers the question.

Rules (same as before):
- The function MUST be named `analyze` and take one argument `df`.
- Return a dictionary with exactly these keys: "result", "chart_type", "chart_data".
- Use ONLY pandas, numpy, and built-in Python. No other imports.
- Do NOT read files or access the network.
- Output ONLY the raw Python code, nothing else -- no ```python fences, no prose, no comments.

DataFrame columns and types:
{schema}

Question: {question}

Code that failed:
{previous_code}

Error it produced:
{error}

Relevant Pandas documentation:
{doc_context}
"""


def fix_code(df: pd.DataFrame, question: str, previous_code: str,
             error: str, retrieved_docs: list[dict]) -> str:
    """
    Asks Gemini to rewrite `previous_code`, using the captured error
    and RAG-retrieved documentation as context. Returns new code as
    a plain string (not yet executed).
    """
    schema = "\n".join(f"- {col}: {dtype}" for col, dtype in df.dtypes.items())
    doc_context = "\n\n".join(
        f"[from {d['source']}]\n{d['content']}" for d in retrieved_docs
    )

    prompt = FIX_PROMPT.format(
        schema=schema,
        question=question,
        previous_code=previous_code,
        error=error,
        doc_context=doc_context,
    )

    response = llm.invoke(prompt)
    code = _extract_text(response)

    if code.startswith("```"):
        code = code.split("```")[1]
        if code.startswith("python"):
            code = code[len("python"):]
        code = code.strip()

    code = _strip_imports(code)

    return code


if __name__ == "__main__":
    # Quick manual test with a tiny fake dataset
    sample_df = pd.DataFrame({
        "region": ["North", "South", "East", "West", "North", "South"],
        "sales": [1200, 950, 1100, 800, 1300, 1000],
    })

    question = "Which region has the highest total sales?"
    generated_code = generate_code(sample_df, question)

    print("\n--- Generated code ---")
    print(generated_code)
    print("----------------------\n")