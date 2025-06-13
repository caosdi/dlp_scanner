# Done with Github copilot - I did some little bits.
# Will add more functionalities
 
import os
import sys
import re
import tempfile
import pandas as pd
import csv
from email import policy
from email.parser import BytesParser
from docx import Document
import PyPDF2
import argparse
from bs4 import BeautifulSoup
import json

# --- Load Dictionary Terms from json file ---
def load_dlp_dict(json_path):
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    dlp_dict = {}
    for category, terms in data.items():
        for term in terms:
            dlp_dict[term.strip()] = category
    return dlp_dict

# --- Dictionary-based term search ---
def find_dlp_terms(text, dlp_dict):
    found = []
    for term, category in dlp_dict.items():
        # Remove word boundaries to allow matching terms with special characters
        pattern = re.compile(re.escape(term), re.IGNORECASE)
        if pattern.search(text):
            found.append((term, category))
    return found

# --- Enhanced SSN detection ---
def find_ssn(text):
    formatted = re.findall(r'\b(?!666|000|9\d{2})\d{3}-(?!00)\d{2}-(?!0000)\d{4}\b', text)
    unformatted = re.findall(r'\b(?!666|000|9\d{2})\d{9}\b', text)
    excluded_range = set(str(i) for i in range(87654320, 87654330))
    filtered_unformatted = [ssn for ssn in unformatted if ssn not in excluded_range]
    return list(set(formatted + filtered_unformatted))

# --- Luhn Algorithm for Credit Cards ---
def luhn_check(card_number):
    digits = [int(d) for d in card_number if d.isdigit()]
    checksum = 0
    reverse_digits = digits[::-1]
    for i, d in enumerate(reverse_digits):
        if i % 2 == 1:
            doubled = d * 2
            checksum += doubled - 9 if doubled > 9 else doubled
        else:
            checksum += d
    return checksum % 10 == 0

def find_credit_cards(text):
    cc_patterns = [
        r'\b3[47]\d{13}\b',                     # Amex
        r'\b3(0[0-5]|[68]\d)\d{11}\b',          # Diners Club
        r'\b6011\d{12}\b',                      # Discover
        r'\b5[1-5]\d{14}\b',                    # MasterCard
        r'\b62\d{14}\b',                        # Union Pay
        r'\b4\d{12}(\d{3})?\b'                  # Visa
    ]
    found = set()
    for pattern in cc_patterns:
        for match in re.findall(pattern, text):
            match_str = ''.join(match) if isinstance(match, tuple) else match
            if luhn_check(match_str):
                found.add(match_str)
    return list(found)

# --- Basic US Driver License detection ---
def find_us_driver_license(text):
    patterns = [
        r'\b\d{5,13}\b',
        r'\b[A-Z]{1,2}\d{5,13}\b'
    ]
    found = set()
    for pattern in patterns:
        found.update(re.findall(pattern, text))
    return list(found)

# --- File type handlers ---
def extract_docx_text(path):
    doc = Document(path)
    return "\n".join([para.text for para in doc.paragraphs])

def extract_pdf_text(path):
    text = ""
    with open(path, "rb") as f:
        reader = PyPDF2.PdfReader(f)
        for page in reader.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + "\n"
    return text

def process_attachment(filename, payload):
    ext = filename.lower().split('.')[-1]
    with tempfile.NamedTemporaryFile(delete=False, suffix='.'+ext, mode='wb') as tmp:
        tmp.write(payload)
        tmp_path = tmp.name

    try:
        if ext == 'docx':
            return extract_docx_text(tmp_path)
        elif ext == 'pdf':
            return extract_pdf_text(tmp_path)
        elif ext in ['xlsx', 'xls']:
            return extract_xlsx_text(tmp_path)
        elif ext == 'csv':
            df = pd.read_csv(tmp_path, dtype=str)
            return df.fillna("").to_string()
        elif ext in ['htm', 'html']:
            with open(tmp_path, 'r', encoding='utf-8', errors='ignore') as f:
                soup = BeautifulSoup(f, 'html.parser')
                return soup.get_text(separator='\n')
        elif ext == 'rtf':
            with open(tmp_path, 'r', encoding='utf-8', errors='ignore') as f:
                raw = f.read()
                # Basic RTF text cleaner: remove RTF control words
                return re.sub(r'{\\[^{}]+}|\\[a-z]+\d* ?|[{}]', '', raw)
        elif ext == 'txt':
            with open(tmp_path, 'r', encoding='utf-8', errors='ignore') as f:
                return f.read()
        else:
            return ""
    except Exception:
        return ""

# --- EML email processing ---
def process_eml(eml_path, dlp_dict, check_dict=True, check_ssn=True, check_cc=True, check_dl=True):
    results = []
    with open(eml_path, 'rb') as f:
        msg = BytesParser(policy=policy.default).parse(f)
    subject = msg['subject'] or ""
    body = ""
    if msg.is_multipart():
        for part in msg.walk():
            if part.get_content_type() == "text/plain":
                body += part.get_content()
    else:
        body = msg.get_content()
    email_text = f"{subject}\n{body}"
    results += scan_text(email_text, "[EMAIL_BODY]", dlp_dict, check_dict, check_ssn, check_cc, check_dl)
    for part in msg.iter_attachments():
        filename = part.get_filename()
        if not filename:
            continue
        payload = part.get_payload(decode=True)
        attachment_text = process_attachment(filename, payload)
        results += scan_text(attachment_text, filename, dlp_dict, check_dict, check_ssn, check_cc, check_dl)
    return results

# --- Standalone file processing ---
def process_standalone_file(file_path, dlp_dict, check_dict=True, check_ssn=True, check_cc=True, check_dl=True):
    ext = file_path.lower().split('.')[-1]
    with open(file_path, 'rb') as f:
        payload = f.read()
    text = process_attachment(file_path, payload)
    return scan_text(text, os.path.basename(file_path), dlp_dict, check_dict, check_ssn, check_cc, check_dl)

# --- Central scan function for all text blocks ---
def scan_text(text, label, dlp_dict, check_dict=True, check_ssn=True, check_cc=True, check_dl=True):
    results = []
    if check_dict and dlp_dict:
        dlp_terms = find_dlp_terms(text, dlp_dict)
        if dlp_terms:
            results.append({"where": label, "matches": dlp_terms})
    if check_ssn:
        for ssn in find_ssn(text):
            results.append({"where": label, "matches": [(ssn, "SSN")]})
    if check_cc:
        for cc in find_credit_cards(text):
            results.append({"where": label, "matches": [(cc, "CreditCard")]})
    if check_dl:
        for lic in find_us_driver_license(text):
            results.append({"where": label, "matches": [(lic, "US Driver License")]})
    return results

# --- Main driver ---
def print_matches(filename, results):
    if results:
        print(f"\n{filename}")
        for item in results:
            for term, category in item['matches']:
                print(f"  {item['where']}: {term}  [category: {category}]")

def parse_args():
    parser = argparse.ArgumentParser(
        description="DLP Email/File Scanner",
        usage="dlp_email_scanner.py [dict_path] input_path [--scan [{ssn,cc,dl,dict} ...]]"
    )
    parser.add_argument("dict_path", nargs="?", help="dlp_terms.json (required if scanning for dict terms)")
    parser.add_argument("input_path", help="emails_folder_or_eml_file_or_attachment")
    parser.add_argument("--scan", nargs="*", choices=["ssn", "cc", "dl", "dict"], help="What to scan for (default: all)")
    args = parser.parse_args()

    # Determine what to scan for
    if args.scan is not None and len(args.scan) > 0:
        check_dict = "dict" in args.scan
        check_ssn = "ssn" in args.scan
        check_cc = "cc" in args.scan
        check_dl = "dl" in args.scan
    else:
        check_dict = check_ssn = check_cc = check_dl = True

    # If dict scan is requested, dict_path must be provided
    if check_dict and not args.dict_path:
        parser.error("Dictionary path is required when scanning for dict terms (--scan dict)")

    return args, check_dict, check_ssn, check_cc, check_dl

def main():
    args, check_dict, check_ssn, check_cc, check_dl = parse_args()
    dlp_dict = load_dlp_dict(args.dict_path) if check_dict and args.dict_path else {}
    input_path = args.input_path
    if os.path.isdir(input_path):
        all_files = [os.path.join(input_path, f) for f in os.listdir(input_path)]
        eml_files = [f for f in all_files if f.lower().endswith('.eml')]
        other_files = [f for f in all_files if not f.lower().endswith('.eml')]
    elif os.path.isfile(input_path):
        if input_path.lower().endswith('.eml'):
            eml_files = [input_path]
            other_files = []
        else:
            eml_files = []
            other_files = [input_path]
    else:
        print("Invalid input path.")
        sys.exit(1)
    for eml_file in eml_files:
        results = process_eml(eml_file, dlp_dict, check_dict, check_ssn, check_cc, check_dl)
        print_matches(os.path.basename(eml_file), results)
    for file in other_files:
        results = process_standalone_file(file, dlp_dict, check_dict, check_ssn, check_cc, check_dl)
        print_matches(os.path.basename(file), results)

if __name__ == "__main__":
    main()