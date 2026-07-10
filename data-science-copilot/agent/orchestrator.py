"""
Step 5: The orchestrator -- the full self-correction loop.

This is the actual "Autonomous Data Science Co-Pilot" behavior:

    generate code -> run in sandbox -> success? done.
                                     -> failure? retrieve docs,
                                        rewrite code, try again
                                        (capped at MAX_ATTEMPTS)

Every attempt is logged into a trace list, which is exactly what
the Streamlit UI (Step 6) will display to make the self-correction
visible to the user instead of hidden.
"""

import pandas as pd

from agent.core import generate_code, fix_code
from agent.sandbox import run_generated_code
from rag.retriever import retrieve_relevant_docs

MAX_ATTEMPTS = 3


def run_agent(df: pd.DataFrame, question: str) -> dict:
    """
    Full pipeline: question -> code -> execute -> self-correct if needed.

    Returns:
        {
            "success": bool,
            "result": {...} or None,
            "attempts": [
                {
                    "attempt_number": 1,
                    "code": "...",
                    "outcome": "success" | "error",
                    "error": "..." (if failed),
                    "retrieved_docs": [...] (if this attempt triggered retrieval),
                },
                ...
            ]
        }
    """
    trace = []
    code = generate_code(df, question)

    for attempt_number in range(1, MAX_ATTEMPTS + 1):
        outcome = run_generated_code(code, df)

        if outcome["success"]:
            trace.append({
                "attempt_number": attempt_number,
                "code": code,
                "outcome": "success",
            })
            return {"success": True, "result": outcome["result"], "attempts": trace}

        # Failed -- retrieve relevant docs for this specific error
        error = outcome["error"]
        retrieved_docs = retrieve_relevant_docs(error, k=3)

        trace.append({
            "attempt_number": attempt_number,
            "code": code,
            "outcome": "error",
            "error": error,
            "retrieved_docs": retrieved_docs,
        })

        if attempt_number == MAX_ATTEMPTS:
            break  # out of attempts, stop here

        # Rewrite the code using the error + retrieved docs, then loop again
        code = fix_code(df, question, code, error, retrieved_docs)

    return {"success": False, "result": None, "attempts": trace}


if __name__ == "__main__":
    # Deliberately tricky dataset: the question uses "Region" (capitalized)
    # but the real column is lowercase "region" -- this should force at
    # least one failed attempt and one self-correction.
    sample_df = pd.DataFrame({
        "region": ["North", "South", "East", "West", "North", "South"],
        "sales": [1200, 950, 1100, 800, 1300, 1000],
    })

    question = "Which Region has the highest total sales?"

    result = run_agent(sample_df, question)

    print(f"\n=== Test 1 (column casing) -- Final success: {result['success']} ===\n")

    for a in result["attempts"]:
        print(f"--- Attempt {a['attempt_number']}: {a['outcome']} ---")
        print(a["code"])
        if a["outcome"] == "error":
            print("\nError:")
            print(a["error"])
        print()

    if result["success"]:
        print("Final result:", result["result"])

    # -----------------------------------------------------------------
    # Test 2: genuinely dirty data that WILL cause a real pandas error
    # (a string mixed into a numeric column breaks .sum()). This is the
    # test that actually proves the self-correction loop can recover
    # from a real failure, not just succeed on the first try.
    # -----------------------------------------------------------------
    dirty_df = pd.DataFrame({
        "region": ["North", "South", "East", "West", "North", "South"],
        "sales": [1200, 950, "N/A", 800, 1300, 1000],  # dirty value on purpose
    })

    dirty_question = "What is the total sales per region?"

    print("\n" + "=" * 60)
    print("Test 2: dirty data (forces a real error)")
    print("=" * 60)

    dirty_result = run_agent(dirty_df, dirty_question)

    print(f"\n=== Test 2 (dirty data) -- Final success: {dirty_result['success']} ===\n")

    for a in dirty_result["attempts"]:
        print(f"--- Attempt {a['attempt_number']}: {a['outcome']} ---")
        print(a["code"])
        if a["outcome"] == "error":
            print("\nError:")
            print(a["error"])
        print()

    if dirty_result["success"]:
        print("Final result:", dirty_result["result"])