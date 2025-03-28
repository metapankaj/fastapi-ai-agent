from langchain_community.document_loaders import PyPDFLoader

def extract_pdf_text(pdf_path):
    extract_text = PyPDFLoader(pdf_path)
    extraction=extract_text.load()
    extracted_text = "\n".join([page.page_content for page in extraction])
    
    return extracted_text

