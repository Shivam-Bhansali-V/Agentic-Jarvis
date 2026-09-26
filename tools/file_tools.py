"""File management tools for the ReAct agent: read_file and write_code_file."""

import os
from pathlib import Path
from typing import Union
from langchain_core.tools import tool

# Supported text extensions
TEXT_EXTENSIONS = {
    ".txt", ".md", ".py", ".json", ".csv", ".xml", ".html", ".css",
    ".js", ".ts", ".yml", ".yaml", ".ini", ".cfg", ".log", ".env"
}


@tool
def read_file(path: str) -> str:
    """Reads and returns the contents of a local file (.txt, .md, .py, .pdf, .docx, .xlsx).
    
    Args:
        path: Relative or absolute path to the file to read.
        
    Returns:
        The text content of the file, or a descriptive error message if reading fails.
    """
    try:
        file_path = Path(path).resolve()
        
        if not file_path.exists():
            return f"Error: File not found at path '{path}'."
            
        if not file_path.is_file():
            return f"Error: Path '{path}' is a directory, not a file."
            
        suffix = file_path.suffix.lower()
        
        # 1. Plain text / code / markdown files
        if suffix in TEXT_EXTENSIONS or suffix == "":
            try:
                return file_path.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                return file_path.read_text(encoding="latin-1", errors="replace")
                
        # 2. PDF documents
        if suffix == ".pdf":
            import pdfplumber
            extracted_text = []
            with pdfplumber.open(file_path) as pdf:
                for i, page in enumerate(pdf.pages):
                    page_text = page.extract_text() or ""
                    extracted_text.append(f"--- Page {i + 1} ---\n{page_text}")
            return "\n\n".join(extracted_text) if extracted_text else "Note: PDF was empty or contained only images."

        # 3. DOCX documents
        if suffix == ".docx":
            import docx
            doc = docx.Document(file_path)
            paragraphs = [p.text for p in doc.paragraphs if p.text.strip()]
            return "\n".join(paragraphs) if paragraphs else "Note: DOCX file was empty."

        # 4. Excel spreadsheets
        if suffix in [".xlsx", ".xls"]:
            import openpyxl
            wb = openpyxl.load_workbook(file_path, data_only=True)
            output = []
            for sheet_name in wb.sheetnames:
                sheet = wb[sheet_name]
                output.append(f"=== Sheet: {sheet_name} ===")
                for row in sheet.iter_rows(values_only=True):
                    row_vals = [str(c) if c is not None else "" for c in row]
                    if any(row_vals):
                        output.append("\t".join(row_vals))
            return "\n".join(output) if output else "Note: Spreadsheet was empty."

        return f"Error: Unsupported file format '{suffix}' for reading."

    except Exception as e:
        return f"Error reading file '{path}': {str(e)}"


@tool
def write_code_file(filepath: str, code_content: str) -> str:
    """Generates or overwrites a code/text file at the specified path.
    
    Args:
        filepath: Relative or absolute path where the file should be saved.
        code_content: The full content/source code to write to the file.
        
    Returns:
        Success confirmation message with path and byte size, or an error message.
    """
    try:
        target_path = Path(filepath).resolve()
        
        # Ensure parent directories exist
        target_path.parent.mkdir(parents=True, exist_ok=True)
        
        target_path.write_text(code_content, encoding="utf-8")
        byte_size = target_path.stat().st_size
        return f"Success: File '{filepath}' written successfully ({byte_size} bytes)."
        
    except Exception as e:
        return f"Error writing file '{filepath}': {str(e)}"
