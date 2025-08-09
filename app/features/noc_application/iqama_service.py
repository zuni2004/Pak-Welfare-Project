import cv2
import numpy as np
import easyocr
import re
from rapidfuzz import fuzz
import os
from datetime import datetime
import arabic_reshaper
from bidi.algorithm import get_display

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
    reshaped_text = arabic_reshaper.reshape(text)
    bidi_text = get_display(reshaped_text)
    return bidi_text

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
    
    print(f"Raw OCR extracted {len(all_results)} results, filtered to {len(filtered_results)}")
    
    for i, result in enumerate(filtered_results):
        bbox, text, confidence = result[:3]
        print(f"Result {i+1}: '{text.strip()}' (confidence: {confidence:.3f})")
    
    return filtered_results

def extract_iqama_fields(results):
    extracted_data = {
        'english_name': None,
        'iqama_number_arabic': None,
        'iqama_number_english': None,
        'issue_date': None,
        'expiry_date': None
    }
    
    sorted_results = sorted(results, key=lambda x: x[0][0][1])
    
    for i, result in enumerate(sorted_results):
        bbox, text, confidence = result[:3]
        text_clean = text.strip()
        
        print(f"Processing: '{text_clean}' (confidence: {confidence:.3f})")
        
        if extracted_data['english_name'] is None:
            english_name_pattern = r'^[A-Z][A-Z\s\.]+[A-Z]$'
            if re.match(english_name_pattern, text_clean) and len(text_clean) > 10:
                skip_headers = ['KINGDOM OF SAUDI ARABIA', 'MINISTRY OF INTERIOR', 'RESIDENT IDENTITY']
                if not any(header in text_clean for header in skip_headers):
                    extracted_data['english_name'] = text_clean
                    print(f"Found English Name: {text_clean}")
        
        if extracted_data['iqama_number_arabic'] is None:
            arabic_digits = re.findall(r'[٠-٩]+', text_clean)
            for digit_group in arabic_digits:
                if len(digit_group) >= 10: 
                    extracted_data['iqama_number_arabic'] = digit_group
                    print(f"Found Arabic Iqama Number: {digit_group}")
                    break
        
        if extracted_data['iqama_number_english'] is None:
            english_digits = re.findall(r'\d{10,}', text_clean)
            for digit_group in english_digits:
                if len(digit_group) == 10:
                    extracted_data['iqama_number_english'] = digit_group
                    print(f"Found English Iqama Number: {digit_group}")
                    break
        
        date_patterns = [
            r'(\d{4})/(\d{1,2})/(\d{1,2})',  
            r'(\d{1,2})/(\d{1,2})/(\d{4})',  
            r'(\d{4})\.(\d{1,2})\.(\d{1,2})', 
            r'(\d{1,2})\.(\d{1,2})\.(\d{4})'  
        ]
        
        for pattern in date_patterns:
            dates_found = re.findall(pattern, text_clean)
            if dates_found:
                for date_match in dates_found:
                    date_str = '/'.join(date_match)
                    
                    if extracted_data['issue_date'] is None:
                        extracted_data['issue_date'] = date_str
                        print(f"Found Issue Date: {date_str}")
                    elif extracted_data['expiry_date'] is None:
                        extracted_data['expiry_date'] = date_str
                        print(f"Found Expiry Date: {date_str}")
    
    all_text = ' '.join([result[1].strip() for result in sorted_results])
    
    if extracted_data['english_name'] is None:
        name_match = re.search(r'RESIDENT IDENTITY\s+([A-Z][A-Z\s\.]+[A-Z])', all_text)
        if name_match:
            extracted_data['english_name'] = name_match.group(1).strip()
            print(f"Found English Name (fallback): {extracted_data['english_name']}")
    
    return extracted_data

def draw_all_detections(image, results, output_path):
    output_image = image.copy()
    
    for i, result in enumerate(results):
        bbox, text, confidence = result[:3]
        
        if re.search(r'[\u0600-\u06FF]', text):
            text = process_arabic_text(text)
        
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

def save_extracted_data(extracted_data, output_path):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("=== EXTRACTED IQAMA DATA ===\n\n")
        f.write(f"English Name: {extracted_data['english_name'] or 'Not found'}\n")
        f.write(f"Iqama Number (Arabic): {extracted_data['iqama_number_arabic'] or 'Not found'}\n")
        f.write(f"Iqama Number (English): {extracted_data['iqama_number_english'] or 'Not found'}\n")
        f.write(f"Issue Date: {extracted_data['issue_date'] or 'Not found'}\n")
        f.write(f"Expiry Date: {extracted_data['expiry_date'] or 'Not found'}\n")
        f.write(f"\nExtraction completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    print(f"Extracted data saved to: {output_path}")

# if __name__ == "__main__":
#     front_image_path = "Iqama_Pictures/2.jpeg"
#     cleaned_output_path = "Iqama_Results/Cleaned/2_cleaned.jpeg"
#     ocr_output_path = "Iqama_Results/OCR_Visualized/2_ocr.jpeg"
#     text_output_path = "Iqama_Results/Text/2_text.txt"
#     structured_output_path = "Iqama_Results/Structured/2_structured.txt"

#     try:
#         # Step 1: Preprocess image
#         print("Step 1: Preprocessing image...")
#         original_image, cleaned_image = preprocess_image_enhanced(front_image_path)

#         os.makedirs(os.path.dirname(cleaned_output_path), exist_ok=True)
#         cv2.imwrite(cleaned_output_path, cleaned_image)
#         print(f"Cleaned image saved to: {cleaned_output_path}")

#         # Step 2: OCR extraction (Arabic + English)
#         print("\nStep 2: Performing OCR extraction...")
#         extracted_results = extract_text_with_multiple_configs(cleaned_image)

#         # Step 3: Save all extracted text to file
#         os.makedirs(os.path.dirname(text_output_path), exist_ok=True)
#         with open(text_output_path, "w", encoding="utf-8") as f:
#             for i, result in enumerate(extracted_results):
#                 bbox, text, confidence = result[:3]

#                 # Handle Arabic text reshaping for saved text
#                 if re.search(r'[\u0600-\u06FF]', text):
#                     text = process_arabic_text(text)

#                 f.write(f"{i+1}: {text.strip()} (confidence: {confidence:.3f})\n")
#         print(f"All extracted text saved to: {text_output_path}")

#         # Step 4: Extract specific Iqama fields
#         print("\nStep 3: Extracting specific Iqama fields...")
#         extracted_data = extract_iqama_fields(extracted_results)
        
#         # Print extracted data
#         print("\n=== EXTRACTED IQAMA DATA ===")
#         print(f"English Name: {extracted_data['english_name'] or 'Not found'}")
#         print(f"Iqama Number (Arabic): {extracted_data['iqama_number_arabic'] or 'Not found'}")
#         print(f"Iqama Number (English): {extracted_data['iqama_number_english'] or 'Not found'}")
#         print(f"Issue Date: {extracted_data['issue_date'] or 'Not found'}")
#         print(f"Expiry Date: {extracted_data['expiry_date'] or 'Not found'}")

#         # Step 5: Save structured data
#         save_extracted_data(extracted_data, structured_output_path)

#         # Step 6: Draw bounding boxes on the original image
#         print("\nStep 4: Creating visualization...")
#         draw_all_detections(original_image, extracted_results, ocr_output_path)

#         print("\n=== PROCESSING COMPLETE ===")

#     except Exception as e:
#         print(f"Pipeline failed: {e}")
#         import traceback
#         traceback.print_exc()