"""
Syllabus Parser - Extracts structured data from PDF syllabi using LLM.
"""
import PyPDF2
import io


def extract_text_from_pdf(pdf_bytes: bytes) -> str:
    """Extract raw text from a PDF file."""
    reader = PyPDF2.PdfReader(io.BytesIO(pdf_bytes))
    text = ""
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + "\n\n"
    return text.strip()


def parse_syllabus(
    pdf_bytes: bytes,
    api_key: str = None,
    base_url: str = None,
    model: str = None,
) -> dict:
    """
    Parse a syllabus PDF and extract structured course data.

    Returns a dict with course_info, key_dates, topics, and policies.
    """
    from utils.llm_client import structured_output

    text = extract_text_from_pdf(pdf_bytes)

    if not text or len(text) < 50:
        raise ValueError("Could not extract meaningful text from the PDF. Try uploading a different file.")

    # Limit to reasonable length for the LLM
    if len(text) > 12000:
        text = text[:12000] + "\n\n[Truncated - syllabus continues...]"

    prompt = f"Parse this course syllabus and extract all structured information:\n\n{text}"

    result = structured_output(
        user_message=prompt,
        prompt_name="syllabus_parser",
        api_key=api_key,
        base_url=base_url,
        model=model,
    )

    return result
