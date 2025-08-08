import cv2
import numpy as np
import easyocr
import re
from rapidfuzz import fuzz
import os
from datetime import datetime

def preprocess_image_enhanced(image_path, resize_factor=2.5):
    image = cv2.imread(image_path)
    
    if image is None:
        raise FileNotFoundError(f"Image not found at {image_path}")
    
    if resize_factor != 1.0:
        image = cv2.resize(image, None, fx=resize_factor, fy=resize_factor, interpolation=cv2.INTER_CUBIC)
    
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    denoised = cv2.fastNlMeansDenoising(gray, None, 10, 7, 21)
    
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    enhanced = clahe.apply(denoised)
    
    kernel = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]])
    sharpened = cv2.filter2D(enhanced, -1, kernel)
    
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 1))
    morphed = cv2.morphologyEx(sharpened, cv2.MORPH_CLOSE, kernel)
    
    final_image = cv2.cvtColor(morphed, cv2.COLOR_GRAY2BGR)
    
    return image, final_image

def extract_text_with_multiple_configs(image):
    reader = easyocr.Reader(['en'], gpu=False)
    
    all_results = []
    
    try:
        results1 = reader.readtext(image, detail=1, paragraph=False)
        all_results.extend(results1)
    except Exception as e:
        print(f"Config 1 failed: {e}")
    
    try:
        results2 = reader.readtext(
            image, 
            detail=1, 
            paragraph=False,
            width_ths=0.5,
            height_ths=0.5,
            decoder='beamsearch',
            beamWidth=5
        )
        all_results.extend(results2)
    except Exception as e:
        print(f"Config 2 failed: {e}")
    
    filtered_results = []
    for result in all_results:
        bbox, text, confidence = result[:3]
        text_clean = text.strip()
        
        if len(text_clean) > 0 and confidence > 0.3:
            is_duplicate = False
            for existing in filtered_results:
                existing_text = existing[1].strip()
                existing_bbox = existing[0]
                
                text_similarity = fuzz.ratio(text_clean.lower(), existing_text.lower())
                
                pos1 = np.array(bbox[0])
                pos2 = np.array(existing_bbox[0])
                distance = np.linalg.norm(pos1 - pos2)
                
                if text_similarity > 80 and distance < 50:
                    is_duplicate = True
                    if confidence > existing[2]:
                        filtered_results.remove(existing)
                        break
                    else:
                        is_duplicate = True
                        break
            
            if not is_duplicate:
                filtered_results.append(result)
    
    filtered_results.sort(key=lambda x: x[2], reverse=True)
    
    print(f"Raw OCR extracted {len(all_results)} results, filtered to {len(filtered_results)}")
    
    for i, result in enumerate(filtered_results):
        bbox, text, confidence = result[:3]
        print(f"Result {i+1}: '{text.strip()}' (confidence: {confidence:.3f})")
    
    return filtered_results

def draw_all_detections(image, results, output_path):
    output_image = image.copy()
    
    for i, result in enumerate(results):
        bbox, text, confidence = result[:3]
        
        if confidence > 0.8:
            color = (0, 255, 0) 
        elif confidence > 0.5:
            color = (0, 255, 255)
        else:
            color = (0, 0, 255) 
        
        pts = np.array(bbox).astype(int)
        cv2.polylines(output_image, [pts], isClosed=True, color=color, thickness=2)
        
        x, y = pts[0]
        label = f"{i+1}: {text[:15]} ({confidence:.2f})"
        cv2.putText(output_image, label, (x, max(y-5, 15)), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.4, color, 1)
    
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    cv2.imwrite(output_path, output_image)
    print(f"Detection visualization saved to: {output_path}")
