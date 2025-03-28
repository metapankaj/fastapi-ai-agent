import easyocr

def ocr_path(img_path):
    reader = easyocr.Reader(['en'])
    results = reader.readtext(img_path)  
    text_list = [texts_extracting[1] for texts_extracting in results]
    final_text = " ".join(text_list)
    
    return final_text