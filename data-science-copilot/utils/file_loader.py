"""
Step 6a: File loading.

Turns an uploaded file (CSV, Excel, or JSON) into a clean pandas
DataFrame, with clear error messages instead of cryptic pandas
tracebacks when a file is malformed.
"""

import pandas as pd


class UnsupportedFileError(Exception):
    """Raised when the uploaded file's extension isn't supported."""
    pass


class FileParsingError(Exception):
    """Raised when the file extension is fine but the content can't be parsed."""
    pass


def load_dataframe(uploaded_file) -> pd.DataFrame:
    """
    Takes a Streamlit UploadedFile object and returns a pandas DataFrame.
    Supports .csv, .xlsx, .xls, and .json.

    Raises UnsupportedFileError or FileParsingError with a clear,
    user-facing message on failure -- these get shown directly in
    the Streamlit UI rather than a raw traceback.
    """
    filename = uploaded_file.name.lower()

    try:
        if filename.endswith(".csv"):
            df = pd.read_csv(uploaded_file)

        elif filename.endswith((".xlsx", ".xls")):
            df = pd.read_excel(uploaded_file)

        elif filename.endswith(".json"):
            df = pd.read_json(uploaded_file)

        else:
            raise UnsupportedFileError(
                f"'{uploaded_file.name}' isn't a supported file type. "
                "Please upload a .csv, .xlsx, .xls, or .json file."
            )

    except UnsupportedFileError:
        raise

    except Exception as e:
        raise FileParsingError(
            f"Couldn't read '{uploaded_file.name}'. The file may be "
            f"corrupted, empty, or in an unexpected format.\n\nDetails: {e}"
        )

    if df.empty:
        raise FileParsingError(
            f"'{uploaded_file.name}' was read successfully but contains no data."
        )

    return df