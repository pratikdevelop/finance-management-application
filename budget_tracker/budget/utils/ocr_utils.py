"""
Utility functions for OCR (Optical Character Recognition) on receipt images
"""
import pytesseract
from PIL import Image
import cv2
import numpy as np
import re
from decimal import Decimal


def preprocess_image(image_path):
    """
    Preprocess image for better OCR results
    """
    # Read image
    img = cv2.imread(image_path)
    
    # Convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Apply thresholding to get black and white image
    _, thresh = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)
    
    # Denoise
    denoised = cv2.fastNlMeansDenoising(thresh)
    
    return denoised


def extract_text_from_receipt(image_path):
    """
    Extract text from receipt image using OCR
    """
    try:
        # Preprocess image
        processed_img = preprocess_image(image_path)
        
        # Perform OCR
        text = pytesseract.image_to_string(processed_img)
        
        return text
    except Exception as e:
        print(f"Error extracting text from receipt: {e}")
        return ""


def extract_amount_from_text(text):
    """
    Extract monetary amounts from OCR text
    """
    # Common patterns for amounts
    patterns = [
        r'total[:\s]*\$?(\d+[.,]\d{2})',  # Total: $XX.XX
        r'amount[:\s]*\$?(\d+[.,]\d{2})',  # Amount: $XX.XX
        r'\$(\d+[.,]\d{2})',  # $XX.XX
        r'(\d+[.,]\d{2})\s*(?:usd|eur|gbp)',  # XX.XX USD
    ]
    
    amounts = []
    for pattern in patterns:
        matches = re.findall(pattern, text.lower())
        for match in matches:
            try:
                # Replace comma with dot for decimal
                amount_str = match.replace(',', '.')
                amount = Decimal(amount_str)
                amounts.append(amount)
            except:
                continue
    
    # Return the largest amount found (usually the total)
    if amounts:
        return max(amounts)
    return None


def extract_date_from_text(text):
    """
    Extract date from OCR text
    """
    from datetime import datetime
    
    # Common date patterns
    patterns = [
        r'(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})',  # DD/MM/YYYY or MM/DD/YYYY
        r'(\d{4}[/-]\d{1,2}[/-]\d{1,2})',  # YYYY-MM-DD
    ]
    
    for pattern in patterns:
        matches = re.findall(pattern, text)
        for match in matches:
            try:
                # Try different date formats
                for fmt in ['%d/%m/%Y', '%m/%d/%Y', '%Y-%m-%d', '%d-%m-%Y']:
                    try:
                        date = datetime.strptime(match, fmt).date()
                        return date
                    except:
                        continue
            except:
                continue
    
    return None


def extract_merchant_from_text(text):
    """
    Extract merchant/store name from OCR text (first few lines usually contain merchant name)
    """
    lines = text.strip().split('\n')
    # Return first non-empty line as potential merchant name
    for line in lines[:5]:  # Check first 5 lines
        line = line.strip()
        if line and len(line) > 2:
            return line
    return ""


def process_receipt_image(image_path):
    """
    Process receipt image and extract relevant information
    """
    text = extract_text_from_receipt(image_path)
    
    result = {
        'raw_text': text,
        'amount': extract_amount_from_text(text),
        'date': extract_date_from_text(text),
        'merchant': extract_merchant_from_text(text),
    }
    
    return result
