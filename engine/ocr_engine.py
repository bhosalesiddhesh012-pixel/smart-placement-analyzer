"""
Document Vault & Automated OCR Proof Verification Engine
Extracts academic percentages, board certifications, and hackathon awards
from student-uploaded PDFs (using pdfplumber/pypdf) and image documents.
Part of Smart Campus Placement Analyser | VIT Pune
"""
import os
import re
import json
import logging
from PIL import Image

logger = logging.getLogger(__name__)

# Optional pytesseract import
try:
    import pytesseract
    HAS_PYTESSERACT = True
except ImportError:
    HAS_PYTESSERACT = False

# PDF extraction libraries
try:
    import pdfplumber
    HAS_PDFPLUMBER = True
except ImportError:
    HAS_PDFPLUMBER = False

try:
    from pypdf import PdfReader
    HAS_PYPDF = True
except ImportError:
    HAS_PYPDF = False


def extract_raw_text(file_path):
    """
    Extracts text from PDF or image using available parsers (pdfplumber, pypdf, pytesseract).
    Returns (raw_text, parser_used).
    """
    ext = os.path.splitext(file_path)[1].lower()
    raw_text = ""
    parser_used = "none"

    if ext == '.pdf':
        # 1. Try pdfplumber first
        if HAS_PDFPLUMBER:
            try:
                with pdfplumber.open(file_path) as pdf:
                    pages_text = []
                    for page in pdf.pages:
                        pt = page.extract_text()
                        if pt:
                            pages_text.append(pt)
                        # Also scan tables if available
                        tables = page.extract_tables() or []
                        for table in tables:
                            for row in table:
                                if row:
                                    row_str = " | ".join(str(cell) for cell in row if cell)
                                    pages_text.append(row_str)
                    raw_text = "\n".join(pages_text).strip()
                    if raw_text:
                        return raw_text, "pdfplumber"
            except Exception as e:
                logger.warning(f"pdfplumber extraction failed on {file_path}: {e}")

        # 2. Fallback to pypdf
        if HAS_PYPDF and not raw_text:
            try:
                reader = PdfReader(file_path)
                pages_text = []
                for page in reader.pages:
                    pt = page.extract_text()
                    if pt:
                        pages_text.append(pt)
                raw_text = "\n".join(pages_text).strip()
                if raw_text:
                    return raw_text, "pypdf"
            except Exception as e:
                logger.warning(f"pypdf extraction failed on {file_path}: {e}")

    elif ext in ('.png', '.jpg', '.jpeg'):
        if HAS_PYTESSERACT:
            try:
                img = Image.open(file_path)
                raw_text = pytesseract.image_to_string(img).strip()
                if raw_text:
                    return raw_text, "pytesseract"
            except Exception as e:
                logger.warning(f"pytesseract extraction failed on {file_path}: {e}")

    # Fallback / simulated extraction if plain text file or unparsed binary with plain strings
    if not raw_text:
        try:
            with open(file_path, 'rb') as f:
                content = f.read(200000)
                # Extract printable ASCII strings
                printable = re.findall(rb'[A-Za-z0-9\s:.,/%()-]{4,}', content)
                raw_text = " ".join([p.decode('latin-1', errors='ignore') for p in printable])
                parser_used = "binary_stream_regex"
        except Exception:
            pass

    return raw_text, parser_used


def parse_academic_marksheet(text, doc_type='10TH_MARKSHEET'):
    """
    Parses marksheet text for percentages, total marks ratio, CGPA, and board name.
    Works for Maharashtra State Board (SSC/HSC), CBSE, ICSE, and MSBTE Diploma.
    """
    result = {
        'extracted': False,
        'percentage': None,
        'board': 'Unknown Examination Board',
        'obtained_marks': None,
        'total_marks': None,
        'raw_snippet': text[:400] if text else "",
        'detection_details': []
    }

    if not text:
        return result

    # 1. Detect Education Board
    text_upper = text.upper()
    if 'MAHARASHTRA' in text_upper or 'MSBSHSE' in text_upper or 'STATE BOARD' in text_upper:
        result['board'] = 'Maharashtra State Board of Secondary & Higher Secondary Education'
    elif 'CENTRAL BOARD' in text_upper or 'CBSE' in text_upper:
        result['board'] = 'Central Board of Secondary Education (CBSE)'
    elif 'COUNCIL FOR THE INDIAN' in text_upper or 'ICSE' in text_upper or 'ISC' in text_upper:
        result['board'] = 'Council for the Indian School Certificate Examinations (ICSE)'
    elif 'TECHNICAL EDUCATION' in text_upper or 'MSBTE' in text_upper or 'DIPLOMA' in text_upper:
        result['board'] = 'Maharashtra State Board of Technical Education (MSBTE Diploma)'

    # 2. Priority Pattern: Direct Percentage
    # Example: "Percentage: 91.40%", "Percentage of Marks: 88.50", "Aggregate: 85%"
    pct_patterns = [
        r'(?:percentage\s*of\s*marks|percentage|aggregate\s*percentage|total\s*percentage|aggregate)[\s:=]*([0-9]{2}(?:\.[0-9]{1,2})?)\s*%?',
        r'([0-9]{2}\.[0-9]{1,2})\s*%',
        r'(?:result|marks)[\s:=]+(?:pass|distinction|first\s*class)?[\s:=]*([0-9]{2}\.[0-9]{1,2})'
    ]

    for pat in pct_patterns:
        match = re.search(pat, text, re.IGNORECASE)
        if match:
            try:
                val = float(match.group(1))
                if 35.0 <= val <= 100.0:
                    result['percentage'] = round(val, 2)
                    result['extracted'] = True
                    result['detection_details'].append(f"Direct percentage regex match: {result['percentage']}%")
                    return result
            except ValueError:
                pass

    # 3. Ratio Pattern: Total Marks Obtained out of Max Marks
    # Example: "Total Marks: 457 / 500", "Grand Total: 520 out of 600", "Marks: 450/500"
    ratio_patterns = [
        r'(?:total\s*marks|grand\s*total|marks\s*obtained|total)[\s:=]*([0-9]{2,4})\s*(?:out\s*of|\/)\s*([0-9]{2,4})',
        r'([0-9]{3,4})\s*\/\s*([0-9]{3,4})'
    ]

    for pat in ratio_patterns:
        matches = re.finditer(pat, text, re.IGNORECASE)
        for m in matches:
            try:
                obt = float(m.group(1))
                tot = float(m.group(2))
                if tot >= 300 and obt <= tot:
                    computed_pct = round((obt / tot) * 100.0, 2)
                    if 35.0 <= computed_pct <= 100.0:
                        result['obtained_marks'] = obt
                        result['total_marks'] = tot
                        result['percentage'] = computed_pct
                        result['extracted'] = True
                        result['detection_details'].append(
                            f"Calculated from marks ratio ({int(obt)}/{int(tot)}): {computed_pct}%"
                        )
                        return result
            except ValueError:
                pass

    # 4. CGPA Pattern (e.g. CBSE 10th CGPA 9.2 -> 9.2 * 9.5 = 87.4%)
    cgpa_match = re.search(r'(?:cgpa|grade\s*point)[\s:=]*([0-9]\.[0-9]{1,2})', text, re.IGNORECASE)
    if cgpa_match:
        try:
            cgpa_val = float(cgpa_match.group(1))
            if 4.0 <= cgpa_val <= 10.0:
                conv_pct = round(cgpa_val * 9.5, 2)
                result['percentage'] = conv_pct
                result['extracted'] = True
                result['detection_details'].append(f"Converted from CGPA ({cgpa_val} x 9.5): {conv_pct}%")
                return result
        except ValueError:
            pass

    return result


def parse_hackathon_certificate(text):
    """
    Parses hackathon or competition certificates to verify winning achievements.
    Detects Winner, 1st/2nd/3rd prize, Hackathon, and Event metadata.
    """
    result = {
        'extracted': False,
        'is_winner': False,
        'achievement_title': 'Competition Certificate',
        'event_name': 'Technical Hackathon',
        'raw_snippet': text[:400] if text else "",
        'keywords_detected': []
    }

    if not text:
        return result

    text_lower = text.lower()

    winning_keywords = [
        'winner', '1st prize', 'first prize', '1st place', 'first place',
        'runner up', '2nd prize', 'second prize', '2nd place',
        '3rd prize', 'third prize', '3rd place', 'champion',
        'secured 1st', 'secured 2nd', 'secured 3rd', 'certificate of excellence',
        'certificate of merit', 'best project', 'hackathon winner'
    ]

    for kw in winning_keywords:
        if kw in text_lower:
            result['keywords_detected'].append(kw)
            result['is_winner'] = True
            result['extracted'] = True

    event_keywords = ['hackathon', 'ideathon', 'coding contest', 'techfest', 'datathon', 'project competition']
    for ekw in event_keywords:
        if ekw in text_lower:
            result['event_name'] = ekw.capitalize()
            break

    if result['is_winner']:
        result['achievement_title'] = f"Winning Achievement ({', '.join(result['keywords_detected'][:2]).title()})"
    elif 'certificate' in text_lower or 'participation' in text_lower:
        result['extracted'] = True
        result['achievement_title'] = "Participation / Technical Certificate"

    return result


def process_and_verify_document(file_path, doc_type):
    """
    Master pipeline: extracts text and parses marksheet or certificate.
    Returns parsed dictionary ready to be persisted into student_documents.
    """
    raw_text, parser = extract_raw_text(file_path)

    if doc_type in ('10TH_MARKSHEET', '12TH_MARKSHEET'):
        parsed = parse_academic_marksheet(raw_text, doc_type)
        parsed['doc_type'] = doc_type
        parsed['parser_engine'] = parser
        return parsed

    elif doc_type == 'HACKATHON_CERTIFICATE':
        parsed = parse_hackathon_certificate(raw_text)
        parsed['doc_type'] = doc_type
        parsed['parser_engine'] = parser
        return parsed

    else:
        return {
            'extracted': bool(raw_text.strip()),
            'doc_type': doc_type,
            'parser_engine': parser,
            'raw_snippet': raw_text[:400]
        }
