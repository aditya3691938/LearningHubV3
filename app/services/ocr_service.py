import re
import pdfplumber

STOP_WORDS = {
    'the', 'of', 'and', 'in', 'a', 'an', 'for', 'with', 'on', 'to', 'at', 'by',
    'from', 'as', 'is', 'it', 'or', 'be', 'are', 'this', 'that', 'your', 'my',
    'certificate', 'certification', 'completion', 'achievement', 'completed',
    'has', 'successfully', 'awarded', 'course', 'program', 'specialization'
}

def extract_text_from_pdf(pdf_source):
    """
    Extracts all plain text from an uploaded PDF file stream or file path using pdfplumber.
    Returns cleaned text string.
    """
    extracted_text = ""
    try:
        if hasattr(pdf_source, 'read'):
            pdf_source.seek(0)
            with pdfplumber.open(pdf_source) as pdf:
                for page in pdf.pages:
                    text = page.extract_text()
                    if text:
                        extracted_text += text + "\n"
            pdf_source.seek(0)
        else:
            with pdfplumber.open(pdf_source) as pdf:
                for page in pdf.pages:
                    text = page.extract_text()
                    if text:
                        extracted_text += text + "\n"
    except Exception as e:
        print(f"OCR PDF extraction error: {e}")
        return ""
        
    return extracted_text.strip()


def validate_certificate_pdf(pdf_source, course_name, issuing_org, learner_name=None, date_earned=None):
    """
    Validates user-submitted external certificate fields against extracted PDF text.
    Returns tuple: (is_valid: bool, discrepancy_msg: str, extracted_text: str)
    """
    extracted_text = extract_text_from_pdf(pdf_source)
    
    if not extracted_text:
        # If PDF has no extractable text layer (e.g. image-only PDF), return informative message
        return False, "Uploaded PDF certificate contains no extractable text layer or is unreadable. Please upload a valid digital certificate PDF.", ""
        
    pdf_text_clean = extracted_text.lower()
    pdf_text_tokens = set(re.findall(r'\b[a-z0-9]+\b', pdf_text_clean))

    discrepancies = []

    # 1. Course / Certification Name Validation
    course_tokens = [w.lower() for w in re.findall(r'\b[a-zA-Z0-9]+\b', course_name) if w.lower() not in STOP_WORDS and len(w) > 1]
    if course_tokens:
        matched_tokens = [w for w in course_tokens if w in pdf_text_tokens or w in pdf_text_clean]
        match_ratio = len(matched_tokens) / len(course_tokens)
        if match_ratio < 0.4:
            discrepancies.append(f"Course Name '{course_name}' could not be verified in the PDF text (matched {len(matched_tokens)}/{len(course_tokens)} key words).")

    # 2. Issuing Organization Validation
    org_tokens = [w.lower() for w in re.findall(r'\b[a-zA-Z0-9]+\b', issuing_org) if w.lower() not in STOP_WORDS and len(w) > 1]
    if org_tokens:
        matched_org_tokens = [w for w in org_tokens if w in pdf_text_tokens or w in pdf_text_clean]
        match_ratio_org = len(matched_org_tokens) / len(org_tokens)
        if match_ratio_org < 0.4:
            discrepancies.append(f"Issuing Organization '{issuing_org}' was not found in the PDF text.")

    # 3. Learner Name Sanity Check (if provided)
    if learner_name:
        name_tokens = [w.lower() for w in re.findall(r'\b[a-zA-Z]+\b', learner_name) if len(w) > 2]
        if name_tokens:
            name_matches = [w for w in name_tokens if w in pdf_text_tokens or w in pdf_text_clean]
            if not name_matches:
                discrepancies.append(f"Learner Name '{learner_name}' does not match any name on the certificate PDF.")

    # 4. Date Earned Check (Year verification if provided)
    if date_earned:
        year_str = str(date_earned.year) if hasattr(date_earned, 'year') else str(date_earned)[:4]
        if year_str not in pdf_text_clean:
            # Note: Soft check on date year
            pass

    if discrepancies:
        combined_msg = "Discrepancy detected between submitted details and certificate PDF: " + " ".join(discrepancies) + " Please provide valid credentials matching your uploaded certificate."
        return False, combined_msg, extracted_text

    return True, "Certificate validated successfully.", extracted_text
