import cv2
import numpy as np
import easyocr
import re
from rapidfuzz import fuzz
import os
from datetime import datetime
import arabic_reshaper
from bidi.algorithm import get_display
import tempfile
from fastapi import APIRouter, UploadFile, File, HTTPException
from pydantic import BaseModel, Field
from typing import Optional
from deep_translator import GoogleTranslator

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

def process_arabic_text(text):
    try:
        reshaped_text = arabic_reshaper.reshape(text)
        bidi_text = get_display(reshaped_text)
        return bidi_text
    except Exception as e:
        print(f"Arabic text processing failed: {e}")
        return text

def translate_to_arabic(text):
    try:
        cleaned_text = re.sub(r'[^\w\s]', '', text).strip()
        if not cleaned_text:
            return None
        
        result = GoogleTranslator(source='en', target='ar').translate(cleaned_text)
        return result
    except Exception as e:
        print(f"Translation failed: {e}")
        return None

def extract_text_with_multiple_configs(image):
    reader = easyocr.Reader(['ar', 'en'], gpu=False) 
    
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
        
    for i, result in enumerate(filtered_results):
        bbox, text, confidence = result[:3]
    
    return filtered_results

def extract_iqama_fields(results):
    extracted_data = {
        'iqama_number_arabic': None
    }
    
    sorted_results = sorted(results, key=lambda x: x[2], reverse=True)
    
    for i, result in enumerate(sorted_results):
        bbox, text, confidence = result[:3]
        text_clean = text.strip()
                
        if extracted_data['iqama_number_arabic'] is None:
            arabic_digits = re.findall(r'[٠-٩]+', text_clean)
            for digit_group in arabic_digits:
                if len(digit_group) == 10:  
                    extracted_data['iqama_number_arabic'] = digit_group
                    break
            
            if extracted_data['iqama_number_arabic']:
                break
    
    if extracted_data['iqama_number_arabic'] is None:
        all_text = ' '.join([result[1].strip() for result in sorted_results])
        arabic_numbers = re.findall(r'[٠-٩]{10}', all_text)
        if arabic_numbers:
            extracted_data['iqama_number_arabic'] = arabic_numbers[0]
    
    return extracted_data

def process_iqama_front(image_path):
    try:        
        original_image, processed_image = preprocess_image_enhanced(image_path)
        ocr_results = extract_text_with_multiple_configs(processed_image)
        
        if not ocr_results:
            print("No text detected in the image")
            return None
        
        extracted_data = extract_iqama_fields(ocr_results)
        
        filtered_data = {k: v for k, v in extracted_data.items() if v is not None}
        
        if not filtered_data:
            return None
            
        return filtered_data
        
    except Exception as e:
        print(f"Error processing Iqama: {str(e)}")
        raise e