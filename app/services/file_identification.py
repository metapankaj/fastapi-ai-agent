import re
import os
from services.ocr_service import ocr_path
from services.summarization import extract_pdf_text
from services.embedding_service import embedding_vectorstore
from services.transcription import transcribe_audio

def file_identification(file_path):
    """
    Identifies file type by extension and processes it to extract and embed text.
    
    """
    if not isinstance(file_path, str):
        raise ValueError("File path must be a string")
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    # Regex patterns for file extensions
    image_pattern = r'[a-zA-Z0-9\-/_@ ]+\.(img|png|jpg|jpeg|tiff)$'
    audio_pattern = r'[a-zA-Z0-9\-/_@ ]+\.(mp3|wav|m4a)$'
    pdf_pattern = r'[a-zA-Z0-9\-/_@ ]+\.pdf$'

    try:
        if re.match(image_pattern, file_path, re.IGNORECASE):
            text = ocr_path(file_path)
            embedding_vectorstore(text)
            return text
        
        elif re.match(audio_pattern, file_path, re.IGNORECASE):
            text = transcribe_audio(file_path)
            embedding_vectorstore(text)
            return text
        
        elif re.match(pdf_pattern, file_path, re.IGNORECASE):
            text = extract_pdf_text(file_path)
            embedding_vectorstore(text)
            return text  
        
        else:
            raise ValueError(f"Unsupported file type: {file_path}")
    
    except Exception as e:
        raise ValueError(f"File processing failed: {str(e)}")
