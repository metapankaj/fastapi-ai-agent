from .api_file_identification import file_identification
from app.services.rag_service import role_based_response

def rag_response(filepath, query, file_extension, current_user_role):
    try:
        is_valid = file_identification(filepath, file_extension) 
        
        if not is_valid:
            return {"error": "Unsupported file type"}

        return role_based_response(query, current_user_role)  

    except Exception as e:
        return {"error": str(e)} 
