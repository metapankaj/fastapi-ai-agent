import whisper
import os

model = whisper.load_model("base")

def transcribe_audio(audio_file_path):
    """Transcribes an audio file to text"""
    
    if not os.path.exists(audio_file_path):
        raise FileNotFoundError(f"Audio file not found: {audio_file_path}")
    
    try:
        result = model.transcribe(audio_file_path)
        return result['text']
    except Exception as e:
        raise ValueError(f"Transcription failed: {str(e)}")

