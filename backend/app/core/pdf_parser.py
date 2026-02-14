import pdfplumber

def parse_invoice(path):
    with pdfplumber.open(path) as pdf:
        text = pdf.pages[0].extract_text()
    return text
