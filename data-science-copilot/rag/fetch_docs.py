"""
Step 4a: Fetch real Pandas documentation pages for our RAG knowledge base.

Why these specific pages: they cover the errors an autonomous agent hits
most often when writing Pandas code from a natural-language question --
wrong column references, merge/join mistakes, missing data handling,
and groupby misuse.

Run this ONCE to build a local cache. It saves clean text files into
rag/docs/, so later steps (chunking + embedding) don't need the internet
every time you rebuild the index.

Usage:
    python rag/fetch_docs.py
"""

import os
import requests
from bs4 import BeautifulSoup

# Real official Pandas user-guide pages, chosen to match the error
# categories our sandbox is most likely to surface.
PANDAS_DOC_PAGES = {
    "indexing.txt": "https://pandas.pydata.org/docs/user_guide/indexing.html",
    "groupby.txt": "https://pandas.pydata.org/docs/user_guide/groupby.html",
    "merging.txt": "https://pandas.pydata.org/docs/user_guide/merging.html",
    "missing_data.txt": "https://pandas.pydata.org/docs/user_guide/missing_data.html",
    "reshaping.txt": "https://pandas.pydata.org/docs/user_guide/reshaping.html",
    "basics.txt": "https://pandas.pydata.org/docs/user_guide/basics.html",
}

OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "docs")


def extract_main_text(html: str) -> str:
    """
    Pandas docs are built with Sphinx. The real content lives inside
    <article role="main">. We strip everything else (nav bar, sidebar,
    footer, search box) so our RAG corpus isn't full of noise.
    """
    soup = BeautifulSoup(html, "html.parser")

    main = soup.find("article", {"role": "main"})
    if main is None:
        # fallback for older Sphinx themes
        main = soup.find("div", {"class": "body"})
    if main is None:
        main = soup  # last resort: whole page

    # Remove elements that add no value to a RAG corpus
    for tag in main.find_all(["script", "style", "nav", "footer"]):
        tag.decompose()

    # IMPORTANT: Sphinx wraps every syntax-highlighted code token in
    # its own <span> (e.g. one span for "df", one for ".", one for
    # "loc"). If we later ask BeautifulSoup to join all text with a
    # newline separator, it inserts a newline BETWEEN EVERY TOKEN,
    # turning "df.loc[df['Region']]" into a garbled one-token-per-line
    # mess. Fix: collapse each code block into a single plain string
    # first (its internal whitespace is already correct), so the
    # later whole-document extraction treats it as one atomic chunk.
    for pre in main.find_all("pre"):
        code_text = pre.get_text(separator="", strip=False)
        pre.clear()
        pre.append(code_text)

    text = main.get_text(separator="\n")

    # Collapse excessive blank lines
    lines = [line.strip() for line in text.split("\n")]
    lines = [line for line in lines if line]
    return "\n".join(lines)


def fetch_all():
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    for filename, url in PANDAS_DOC_PAGES.items():
        print(f"Fetching {url} ...")
        response = requests.get(url, timeout=15)
        response.raise_for_status()

        clean_text = extract_main_text(response.text)

        out_path = os.path.join(OUTPUT_DIR, filename)
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(clean_text)

        print(f"  saved -> {out_path} ({len(clean_text)} chars)")

    print("\nDone. All pages cached locally in rag/docs/")


if __name__ == "__main__":
    fetch_all()