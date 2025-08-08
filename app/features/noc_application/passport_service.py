import cv2
import numpy as np
import easyocr
import re
from rapidfuzz import fuzz
import os
from datetime import datetime
from Cleaning_OCR import preprocess_image_enhanced, extract_text_with_multiple_configs, draw_all_detections

def extract_passport_fields(results):
    text_items = []
    for result in results:
        bbox, text, confidence = result[:3]
        if confidence > 0.3:
            x = int(np.mean([point[0] for point in bbox]))
            y = int(np.mean([point[1] for point in bbox]))
            text_items.append({
                'text': text.strip(),
                'x': x,
                'y': y,
                'confidence': confidence
            })
    
    text_items.sort(key=lambda item: item['y'])
    all_texts = [item['text'] for item in text_items]
    full_text = ' '.join(all_texts).upper()

    fields = {
        'type': 'Not Found',
        'country_code': 'Not Found',
        'passport_number': 'Not Found',
        'surname': 'Not Found',
        'given_names': 'Not Found',
        'nationality': 'Not Found',
        'citizenship_number': 'Not Found',
        'sex': 'Not Found',
        'date_of_birth': 'Not Found',
        'place_of_birth': 'Not Found',
        'father_name': 'Not Found',
        'date_of_issue': 'Not Found',
        'date_of_expiry': 'Not Found',
        'issuing_authority': 'Not Found',
        'tracking_number': 'Not Found',
        'booklet_number': 'Not Found',
        'mrz_lines': []
    }

    mrz_candidates = [t for t in all_texts if t.startswith('P<') or '<<' in t]
    if mrz_candidates:
        fields['mrz_lines'] = mrz_candidates

    passport_patterns = [
        r'\b([A-Z]{2,3}[0-9]{6,7})\b',  
        r'\b([A-Z][0-9]{8})\b',     
    ]
    for pattern in passport_patterns:
        passport_match = re.search(pattern, full_text)
        if passport_match:
            fields['passport_number'] = passport_match.group(1)
            break

    cnic_patterns = [
        r'(\d{5}[-\s]?\d{7}[-\s]?\d{1})',  
        r'(\d{13})',  
    ]
    for pattern in cnic_patterns:
        cnic_match = re.search(pattern, full_text)
        if cnic_match:
            cnic = cnic_match.group(1)
            if '-' not in cnic and len(cnic) == 13:
                cnic = f"{cnic[:5]}-{cnic[5:12]}-{cnic[12]}"
            fields['citizenship_number'] = cnic
            break

    booklet_match = re.search(r'\b([A-Z]{1}[0-9]{7})\b', full_text)
    if booklet_match:
        fields['booklet_number'] = booklet_match.group(1)

    tracking_match = re.search(r'\b(\d{11})\b', full_text)
    if tracking_match:
        fields['tracking_number'] = tracking_match.group(1)

    date_patterns = [
        r'\b(\d{2}\s[A-Z]{3}\s\d{4})\b', 
    ]
    
    found_dates = []
    for pattern in date_patterns:
        dates = re.findall(pattern, full_text)
        found_dates.extend(dates)
    
    sex_indicators = ['M', 'F', 'X']
    for idx, text_item in enumerate(text_items):
        text = text_item['text'].strip().upper()

        if text in sex_indicators:
            fields['sex'] = text
            break

    if 'PAKISTAN' in full_text or 'PAK' in full_text:
        fields['nationality'] = 'PAKISTANI'
        fields['country_code'] = 'PAK'
        fields['issuing_authority'] = 'PAKISTAN'

    if 'P' in [item['text'].strip() for item in text_items]:
        fields['type'] = 'P'

    for i, item in enumerate(text_items):
        text = item['text'].upper()

        if ('SURNAME' in text) and i+1 < len(text_items):
            fields['surname'] = text_items[i+1]['text']
        
        if ('GIVEN NAMES' in text or 'GIVEN NAME' in text or 'GIVEN' in text or 'NAME' in text) and i+1 < len(text_items):
            fields['given_names'] = text_items[i+1]['text']

        if (fuzz.partial_ratio(text, 'PLACE OF BIRTH') > 80 or 
            fuzz.partial_ratio(text, 'BIRTH PLACE') > 80) and i+1 < len(text_items):
            fields['place_of_birth'] = text_items[i+1]['text']

        if ('FATHER NAME' in text or 'FATHER' in text) and i+1 < len(text_items):
            fields['father_name'] = text_items[i+1]['text']

        field_map = {
            'date_of_birth': ['DATE OF BIRTH', 'BIRTH DATE', 'DOB'],
            'date_of_issue': ['DATE OF ISSUE', 'ISSUE DATE', 'ISSUED'],
            'date_of_expiry': ['DATE OF EXPIRY', 'EXPIRY DATE', 'EXPIRES', 'VALID UNTIL'],
        }

        for field_key, field_labels in field_map.items():
            for label in field_labels:
                if fuzz.partial_ratio(text, label) > 80 and i + 1 < len(text_items):
                    next_text = text_items[i + 1]['text'].upper()
                    
                    for pattern in date_patterns:
                        match = re.search(pattern, next_text)
                        if match:
                            fields[field_key] = match.group()
                            break
                    break

    
    if fields['surname'] == 'Not Found' or fields['given_names'] == 'Not Found':
        for line in fields['mrz_lines']:
            if line.startswith('P<PAK'):
                name_part = line[5:]
                name_parts = name_part.split('<<')
                if len(name_parts) >= 2:
                    if fields['surname'] == 'Not Found':
                        fields['surname'] = name_parts[0].replace('<', ' ').strip()
                    if fields['given_names'] == 'Not Found' and len(name_parts) > 1:
                        fields['given_names'] = name_parts[1].replace('<', ' ').strip()
                break

    if found_dates:
        found_dates = list(set(found_dates))  

        date_objects = []
        for date_str in found_dates:
            parsed_date = None
            for fmt in ['%d %b %Y', '%d %B %Y', '%d/%m/%Y', '%d-%m-%Y']:
                try:
                    parsed_date = datetime.strptime(date_str, fmt)
                    date_objects.append((parsed_date, date_str))
                    break
                except:
                    continue

        date_objects.sort(key=lambda x: x[0]) 

        for i, (parsed_date, date_str) in enumerate(date_objects):
            year = parsed_date.year

            if fields['date_of_birth'] == 'Not Found' and 1900 <= year <= datetime.now().year - 10:
                fields['date_of_birth'] = date_str
                continue

            if fields['date_of_birth'] != 'Not Found':
                try:
                    dob_obj = datetime.strptime(fields['date_of_birth'], '%d %b %Y')
                except:
                    try:
                        dob_obj = datetime.strptime(fields['date_of_birth'], '%d %B %Y')
                    except:
                        dob_obj = None

                if dob_obj and parsed_date > dob_obj:
                    if fields['date_of_issue'] == 'Not Found':
                        fields['date_of_issue'] = date_str
                        continue

                    if fields['date_of_issue'] != 'Not Found' and fields['date_of_expiry'] == 'Not Found':
                        try:
                            doi_obj = datetime.strptime(fields['date_of_issue'], '%d %b %Y')
                        except:
                            try:
                                doi_obj = datetime.strptime(fields['date_of_issue'], '%d %B %Y')
                            except:
                                doi_obj = None

                        if doi_obj:
                            year_diff = parsed_date.year - doi_obj.year
                            if 4 <= year_diff <= 11:
                                fields['date_of_expiry'] = date_str
                                continue

    if fields['place_of_birth'] == 'Not Found':
        for item in text_items:
            text = item['text'].upper().strip()
            if ',' in text:
                parts = [part.strip().replace('[', 'L').replace(']', '') for part in text.split(',')]
                if len(parts) == 2 and len(parts[1]) == 3 and parts[1].isalpha() and parts[1].isupper():
                    city_part = parts[0]
                    country_code = parts[1]
                    if len(city_part) > 2:
                        fields['place_of_birth'] = f"{city_part}, {country_code}"
                        break

    if fields['place_of_birth'] == 'Not Found':
        match = re.search(r'([A-Z\[\]]{3,}),\s*([A-Z]{3})', full_text.upper())
        if match:
            city = match.group(1).replace('[', 'L').replace(']', '')
            country = match.group(2)
            fields['place_of_birth'] = f"{city}, {country}"
            
    if fields['surname'] == 'Not Found' or fields['given_names'] == 'Not Found':
        potential_names = []
        for item in text_items:
            text = item['text'].strip()
            if (text.isalpha() and 2 <= len(text) <= 20 and 
                item['confidence'] > 0.6 and text not in ['PAKISTAN', 'PAKISTANI', 'PASSPORT']):
                potential_names.append(text)
        
        if len(potential_names) >= 2:
            if fields['surname'] == 'Not Found':
                fields['surname'] = potential_names[0]
            if fields['given_names'] == 'Not Found' and len(potential_names) > 1:
                fields['given_names'] = ' '.join(potential_names[1:3])  

    if fields['father_name'] == 'Not Found':
        for item in text_items:
            text = item['text'].strip()
            if (',' in text and any(part.isalpha() for part in text.split(',')) and 
                len(text) > 10 and item['confidence'] > 0.6):
                fields['father_name'] = text
                break

    return fields

def parse_date(text):
    formats = [
        '%d %b %Y', '%d %B %Y', '%d %b %y', '%d %B %y',
        '%d/%m/%Y', '%d-%m-%Y', '%d.%m.%Y',
        '%m/%d/%Y', '%m-%d-%Y'
    ]
    
    for fmt in formats:
        try:
            parsed = datetime.strptime(text, fmt)
            return parsed.strftime('%d %b %Y')
        except:
            continue
    return None

def process_passport_front(image_path, output_image_path):
    original_image, processed_image = preprocess_image_enhanced(image_path, resize_factor=2.5)
    results = extract_text_with_multiple_configs(processed_image)

    if not results:
        print("No text found in Passport image.")
        return None

    passport_info = extract_passport_fields(results)

    print("\n" + "="*70)
    print("         PASSPORT FRONT EXTRACTION RESULTS")
    print("="*70)
    for k, v in passport_info.items():
        print(f"{k.replace('_', ' ').title()}: {v}")
    print("="*70)

    return passport_info

# if __name__ == "__main__":
#     front_image_path = "Passport_Pictures/10.jpeg"
#     cleaned_output_path = "Passport_Results/Cleaned/10_cleaned.jpeg"
#     ocr_output_path = "Passport_Results/OCR_Visualized/10_ocr.jpeg"
#     text_output_path = "Passport_Results/Text/10_text.txt"

#     try:
#         print("Starting passport front image processing...")
#         original_image, cleaned_image = preprocess_image_enhanced(front_image_path, resize_factor=2.5)
        
#         os.makedirs(os.path.dirname(cleaned_output_path), exist_ok=True)
#         cv2.imwrite(cleaned_output_path, cleaned_image)
#         print(f"Cleaned image saved to: {cleaned_output_path}")
        
#         extracted_results = extract_text_with_multiple_configs(cleaned_image)
        
#         if not extracted_results:
#             print("No text detected in the passport image.")
#             exit()
        
#         os.makedirs(os.path.dirname(text_output_path), exist_ok=True)
#         with open(text_output_path, "w", encoding="utf-8") as f:
#             for i, result in enumerate(extracted_results):
#                 bbox, text, confidence = result[:3]
#                 f.write(f"{i+1}: {text.strip()} (confidence: {confidence:.3f})\n")
#         print(f"Extracted text saved to: {text_output_path}")
        
#         draw_all_detections(original_image, extracted_results, ocr_output_path)
#         print(f"OCR visualization saved to: {ocr_output_path}")
        
#         passport_info = extract_passport_fields(extracted_results)

#         print("\n" + "="*70)
#         print("         PASSPORT FRONT EXTRACTION RESULTS")
#         print("="*70)
#         for k, v in passport_info.items():
#             print(f"{k.replace('_', ' ').title()}: {v}")
#         print("="*70)
        
#     except Exception as e:
#         print(f"Passport processing pipeline failed: {e}")
