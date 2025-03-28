from app.services.ocr_service import ocr_path
from app.services.summarization import extract_pdf_text
from app.services.embedding_service import embedding_vectorstore
from app.services.transcription import transcribe_audio
import os

def file_identification(filepath, file_extension):
    if isinstance(file_extension, bytes):
        file_extension = file_extension.decode('utf-8', errors='ignore')
    elif not isinstance(file_extension, str):
        raise ValueError(f"Invalid file_extension type: {type(file_extension)}")
    
    file_extension = file_extension.lower()
    print(f"Debug - filepath: {filepath}, file_extension: {file_extension}")
    
    if file_extension in [".img", ".png", ".jpg", ".jpeg"]:
        data = ocr_path(filepath)
        embedding_vectorstore(data)
        return data
    elif file_extension in [".mp3", ".wav"]:
        data = transcribe_audio(filepath)
        embedding_vectorstore(data)
        return data
    elif file_extension == ".pdf":
        data = extract_pdf_text(filepath)
        embedding_vectorstore(data)
        return {"successfully processed"}
    raise ValueError(f"unsupported file type: {file_extension}")