from langchain.document_loaders import PyPDFLoader


def extract_text_from_document(file_path):
    loader = PyPDFLoader(file_path)
    return loader.page_content
