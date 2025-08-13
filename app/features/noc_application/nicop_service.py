import cv2
import numpy as np
import easyocr
import re
from rapidfuzz import fuzz
import os
from datetime import datetime
from .Cleaning_OCR import preprocess_image_enhanced, extract_text_with_multiple_configs

def process_nicop_front_improved(image_path, output_image_path):
    try:
        if not os.path.exists(image_path):
            print(f"Error: Image file '{image_path}' not found!")
            return None
        
        original_image, processed_image = preprocess_image_enhanced(image_path, resize_factor=2.5)
        results = extract_text_with_multiple_configs(processed_image)
        
        if not results:
            print("No text extracted!")
            return None
        
        extracted_info = extract_nicop_fields_improved(results)

        return extracted_info
        
    except Exception as e:
        print(f"Error processing image: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

def extract_nicop_fields_improved(results):
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
                'confidence': confidence,
                'bbox': bbox
            })
    
    text_items.sort(key=lambda item: item['y'])
    
    all_texts = [item['text'] for item in text_items]
    full_text = ' '.join(all_texts)
  
    info = {
        'name': 'Not Found',
        'father_name': 'Not Found',
        'gender': 'Not Found',
        'country': 'Not Found',
        'cnic_number': 'Not Found',
        'date_of_birth': 'Not Found',
        'date_of_issue': 'Not Found',
        'date_of_expiry': 'Not Found'
    }
    
    cnic_candidates = re.findall(r'(\d{5}[^\d]?\d{7}[^\d]?\d{1})', full_text)

    for candidate in cnic_candidates:
        digits = re.sub(r'[^\d]', '', candidate)
        if len(digits) == 13:
            info['cnic_number'] = f"{digits[:5]}-{digits[5:12]}-{digits[12]}"
            break

    if info['cnic_number'] == 'Not Found':
        matches = re.findall(r'\b\d{13}\b', full_text)
        for match in matches:
            info['cnic_number'] = f"{match[:5]}-{match[5:12]}-{match[12]}"
            break

    date_pattern = r'(\d{1,2})(?:[.\-/, ]+)(\d{1,2})(?:[.\-/,]+)(\d{4})|(\d{8})'
    dates_found = []

    for match in re.finditer(date_pattern, full_text):
        date_str = match.group()
        
        if len(date_str) == 8 and date_str.isdigit():
            normalized = f"{date_str[:2]}.{date_str[2:4]}.{date_str[4:]}"
        else:
            normalized = re.sub(r'[.\-,/ ]+', '.', date_str)

        try:
            datetime.strptime(normalized, '%d.%m.%Y')
            dates_found.append(normalized)
        except:
            continue 

    unique_dates = list(dict.fromkeys(dates_found))

    if unique_dates:
        try:
            date_objs = [(d, datetime.strptime(d, '%d.%m.%Y')) for d in unique_dates]
            date_objs.sort(key=lambda x: x[1]) 

            if len(date_objs) == 1:
                info['date_of_birth'] = date_objs[0][0]

            elif len(date_objs) == 2:
                dob = date_objs[0]
                other = date_objs[1]
                diff_years = (other[1] - dob[1]).days / 365.25

                info['date_of_birth'] = dob[0]
                if 9 <= diff_years <= 11:
                    info['date_of_issue'] = dob[0]
                    info['date_of_expiry'] = other[0]
                else:
                    info['date_of_issue'] = other[0]

            elif len(date_objs) >= 3:
                dob = date_objs[0]
                middle = date_objs[1]
                last = date_objs[-1]

                diff_issue_expiry = (last[1] - middle[1]).days / 365.25

                info['date_of_birth'] = dob[0]
                if 9 <= diff_issue_expiry <= 11:
                    info['date_of_issue'] = middle[0]
                    info['date_of_expiry'] = last[0]
                else:
                    info['date_of_issue'] = middle[0]
                    info['date_of_expiry'] = last[0]

        except Exception as e:
            print(f"Date parsing error: {e}")


    for item in text_items:
        text_upper = item['text'].upper().strip()
        if text_upper in ['M', 'F', 'MALE', 'FEMALE']:
            info['gender'] = 'M' if text_upper in ['M', 'MALE'] else 'F'
            break
    
    country_mappings = {
        'saudi arabia': 'Saudi Arabia',
        'saudi': 'Saudi Arabia',
        'pakistan': 'Pakistan',
        'uae': 'UAE',
        'kuwait': 'Kuwait',
        'qatar': 'Qatar'
    }
    
    full_text_lower = full_text.lower()
    for country_key, country_value in country_mappings.items():
        if country_key in full_text_lower:
            info['country'] = country_value
            break
    
    name_found = False
    father_name_found = False
    
    for i, item in enumerate(text_items):
        text = item['text'].strip()
        
        skip_patterns = [
            r'\d', r'pakistan', r'national', r'identity', r'card', r'islamic',
            r'republic', r'gender', r'country', r'stay', r'number', r'birth',
            r'issue', r'expiry', r'holder', r'signature', r'present', r'permanent',
            r'address', r'registrar', r'ordinance', r'section'
        ]
        
        if any(re.search(pattern, text, re.IGNORECASE) for pattern in skip_patterns):
            continue
        
        words = text.split()
        if len(words) >= 2 and len(text) > 4:
            if all(word.replace("'", "").replace("-", "").isalpha() for word in words):
                if all(word[0].isupper() for word in words if word):
                    context_before = ""
                    context_after = ""
                    
                    if i > 0:
                        context_before = text_items[i-1]['text'].lower()
                    if i < len(text_items) - 1:
                        context_after = text_items[i+1]['text'].lower()
                    
                    if 'name' in context_before and 'father' not in context_before and not name_found:
                        info['name'] = text
                        name_found = True
                    elif 'father' in context_before or ('name' in context_before and name_found) and not father_name_found:
                        info['father_name'] = text
                        father_name_found = True
                    elif not name_found:
                        info['name'] = text
                        name_found = True
                    elif not father_name_found:
                        info['father_name'] = text
                        father_name_found = True
    
    return info


def process_nicop_back_improved(image_path, output_image_path):
    try:
        if not os.path.exists(image_path):
            print(f"Error: Image file '{image_path}' not found!")
            return None
        
        original_image, processed_image = preprocess_image_enhanced(image_path, resize_factor=2.5)
        
        results = extract_text_with_multiple_configs(processed_image)
        
        if not results:
            print("No text extracted from back!")
            return None
        
        text_items = []
        for result in results:
            bbox, text, confidence = result[:3]
            if confidence > 0.3:
                y = int(np.mean([point[1] for point in bbox]))
                text_items.append({
                    'text': text.strip(),
                    'y': y,
                    'confidence': confidence
                })
        
        text_items.sort(key=lambda item: item['y'])
        all_texts = [item['text'] for item in text_items]
        combined_text = ' '.join(all_texts)
                
        def clean_address(address):
            address = re.sub(r'^\s*\d{5}[-\s]?\d{7}[-\s]?\d\s*', '', address)
            address = re.sub(r'[\s;:,-]*\d{11,15}$', '', address)
            return address.strip()
        
        present_address = "Not Found"
        permanent_address = "Not Found"
        
        structured_text = ""
        for i, text in enumerate(all_texts):
            structured_text += text
            if i < len(all_texts) - 1:
                structured_text += " "
        
        present_patterns = [
            r'present\s+address\s*:?\s*(.*?)(?=permanent\s+address|the\s+holder|registrar|visa|$)',
            r'present\s+address\s*:?\s*(.*?)(?=\n.*permanent|\n.*the\s+holder|\n.*registrar|$)'
        ]
        
        for pattern in present_patterns:
            match = re.search(pattern, structured_text, re.IGNORECASE | re.DOTALL)
            if match:
                present_address = re.sub(r'\s+', ' ', match.group(1).strip())
                present_address = present_address.replace('H.No.', 'H.No.').replace('  ', ' ')
                present_address = clean_address(present_address)
                break
        
        permanent_patterns = [
            r'permanent\s+address\s*:?\s*(.*?)(?=the\s+holder|registrar|visa|issued|$)',
            r'permanent\s+address\s*:?\s*(.*?)(?=\n.*the\s+holder|\n.*registrar|$)'
        ]
        
        for pattern in permanent_patterns:
            match = re.search(pattern, structured_text, re.IGNORECASE | re.DOTALL)
            if match:
                permanent_address = re.sub(r'\s+', ' ', match.group(1).strip())
                permanent_address = permanent_address.replace('H.No.', 'H.No.').replace('  ', ' ')
                permanent_address = clean_address(permanent_address)
                break
     
        return {
            'present_address': present_address,
            'permanent_address': permanent_address,
        }
        
    except Exception as e:
        print(f"Error processing back image: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

def parse_date_variants(date_str):
    date_formats = [
        '%d.%m.%Y',    
        '%d,%m.%Y',    
        '%d/%m/%Y',    
        '%d-%m-%Y',    
        '%m.%d.%Y',    
        '%d.%m,%Y',    
        '%d,%m,%Y'
    ]
    
    for fmt in date_formats:
        try:
            return datetime.strptime(date_str, fmt)
        except ValueError:
            continue
    return None

def clean_ocr_text(text):
    replacements = {
        '@f': 'of',
        '@': 'a',
        '0f': 'of',
        'Expiny': 'Expiry',
        'ol': 'of',
        'Vile': 'Vide',
        'RAKISTAN': 'PAKISTAN',
        '{ree': 'free'
    }
    
    cleaned = text
    for wrong, correct in replacements.items():
        cleaned = cleaned.replace(wrong, correct)
    
    return cleaned