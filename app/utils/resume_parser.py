"""
Resume Parser Module
"""
import os
from PyPDF2 import PdfReader
from docx import Document
import re

def extract_text_from_pdf(file_path):
    try:
        text = []
        pdf_reader = PdfReader(file_path)
        for page in pdf_reader.pages:
            text.append(page.extract_text())
        return '\n'.join(text)
    except:
        return ""

def extract_text_from_docx(file_path):
    try:
        doc = Document(file_path)
        text = [para.text for para in doc.paragraphs if para.text.strip()]
        return '\n'.join(text)
    except:
        return ""

def extract_text_from_txt(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            return f.read()
    except:
        return ""

def extract_text_generic(file_path):
    ext = os.path.splitext(file_path)[1].lower()
    if ext == '.pdf':
        return extract_text_from_pdf(file_path)
    elif ext == '.docx':
        return extract_text_from_docx(file_path)
    elif ext == '.txt':
        return extract_text_from_txt(file_path)
    return ""

def extract_email(text):
    pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    matches = re.findall(pattern, text)
    return matches[0] if matches else None

def extract_phone(text):
    patterns = [r'\+?91?[-.]?\d{10}', r'\b\d{10}\b']
    for pattern in patterns:
        matches = re.findall(pattern, text)
        if matches:
            return matches[0]
    return None

def guess_name(text, fallback=""):
    lines = text.split('\n')[:5]
    for line in lines:
        line = line.strip()
        if 2 <= len(line.split()) <= 4 and len(line) < 50:
            return line
    return fallback
