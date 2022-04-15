import os
from io import StringIO 
from pdfminer.high_level import extract_pages
from pdfminer.layout import LTTextContainer
from pickletools import OpcodeInfo

def extract_text(path, *args, **kwargs) -> list[dict]:
    """Take a file path as input, and return a list of text with headings."""

    paragraph_text = []
    for page_layout in extract_pages(path):
        for element in page_layout:
            if isinstance(element, LTTextContainer):
                paragraph_text.append(clean_paragraph(element.get_text()))
    title = os.path.splitext(path)[0].split("/")[-1]
    
    return to_json(title, paragraph_text) 


def clean_paragraph(paragraph_text):
    return " ".join(paragraph_text.split())


def to_json(title, paragraph_text):
    # paragraph_text = pdf_extractor(os.path.join(pdf_folder, pdf_name))
    contents = [{'tag': 'plain', 'text': text} for text in paragraph_text]
    pdf_json = {
        "title": title,
        "contents": contents
    }
    return pdf_json


if __name__ == '__main__':
    print('Write any tests or debugging code here.')
