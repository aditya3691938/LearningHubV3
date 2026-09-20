import re
import pdfplumber

STOP_WORDS = {
    'the', 'of', 'and', 'in', 'a', 'an', 'for', 'with', 'on', 'to', 'at', 'by',
    'from', 'as', 'is', 'it', 'or', 'be', 'are', 'this', 'that', 'your', 'my',
    'certificate', 'certification', 'completion', 'achievement', 'completed',
    'has', 'successfully', 'awarded', 'course', 'program', 'specialization',
    'license', 'credential', 'verify', 'verified'
}

def extract_text_from_pdf(pdf_source):
    """
    Extracts all plain text from an uploaded PDF file stream or file path.
    Tries pdfplumber first, then falls back to pypdfium2 for high-reliability text extraction.
    """
    extracted_text = ""
    
    # 1. Try pdfplumber
    try:
        if hasattr(pdf_source, 'seek'):
            pdf_source.seek(0)
        with pdfplumber.open(pdf_source) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    extracted_text += text + "\n"
        if hasattr(pdf_source, 'seek'):
            pdf_source.seek(0)
    except Exception as e:
        print(f"pdfplumber extraction notice: {e}")

    # 2. Fallback to pypdfium2 if text is still empty
    if not extracted_text.strip():
        try:
            import pypdfium2
            if hasattr(pdf_source, 'seek'):
                pdf_source.seek(0)
            pdf = pypdfium2.PdfDocument(pdf_source)
            for page in pdf:
                textpage = page.get_textpage()
                text = textpage.get_text_range()
                if text:
                    extracted_text += text + "\n"
            if hasattr(pdf_source, 'seek'):
                pdf_source.seek(0)
        except Exception as e2:
            print(f"pypdfium2 extraction notice: {e2}")

    return extracted_text.strip()


def validate_certificate_pdf(pdf_source, course_name, issuing_org, learner_name=None, date_earned=None):
    """
    Validates user-submitted external certificate fields against extracted PDF text.
    Uses exact word token matching to prevent false positives from partial/substring matches.
    Returns tuple: (is_valid: bool, discrepancy_msg: str, extracted_text: str)
    """
    extracted_text = extract_text_from_pdf(pdf_source)
    
    if not extracted_text:
        return False, "Uploaded PDF certificate contains no extractable text layer or is unreadable. Please upload a valid digital certificate PDF.", ""
        
    pdf_text_clean = extracted_text.lower()
    # Exact word tokens extracted using regex word boundaries
    pdf_text_tokens = set(re.findall(r'\b[a-z0-9]+\b', pdf_text_clean))

    discrepancies = []

    # 1. Course / Certification Name Validation
    course_tokens = [w.lower() for w in re.findall(r'\b[a-zA-Z0-9]+\b', course_name) if w.lower() not in STOP_WORDS and len(w) > 1]
    if course_tokens:
        # Match exact word tokens in pdf_text_tokens
        matched_tokens = [w for w in course_tokens if w in pdf_text_tokens]
        match_ratio = len(matched_tokens) / len(course_tokens)
        if match_ratio < 0.4:
            discrepancies.append(f"Course Name '{course_name}' could not be verified in the PDF text (matched {len(matched_tokens)}/{len(course_tokens)} key words).")
    else:
        # Generic input with no valid tokens
        discrepancies.append(f"Course Name '{course_name}' is too short or invalid for verification.")

    # 2. Issuing Organization Validation
    org_tokens = [w.lower() for w in re.findall(r'\b[a-zA-Z0-9]+\b', issuing_org) if w.lower() not in STOP_WORDS and len(w) > 1]
    if org_tokens:
        matched_org_tokens = [w for w in org_tokens if w in pdf_text_tokens]
        match_ratio_org = len(matched_org_tokens) / len(org_tokens)
        if match_ratio_org < 0.4:
            discrepancies.append(f"Issuing Organization '{issuing_org}' was not found in the PDF text.")

    # 3. Learner Name Sanity Check (if provided)
    if learner_name:
        name_tokens = [w.lower() for w in re.findall(r'\b[a-zA-Z]+\b', learner_name) if len(w) > 2]
        if name_tokens:
            name_matches = [w for w in name_tokens if w in pdf_text_tokens]
            if not name_matches:
                discrepancies.append(f"Learner Name '{learner_name}' does not match any name on the certificate PDF.")

    if discrepancies:
        combined_msg = "Discrepancy detected between submitted details and certificate PDF: " + " ".join(discrepancies) + " Please check your entries or upload a matching certificate."
        return False, combined_msg, extracted_text

    return True, "Certificate validated successfully.", extracted_text
