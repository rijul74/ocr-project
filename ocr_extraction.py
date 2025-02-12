import cv2
import pytesseract
import numpy as np
import json
from datetime import datetime
from PIL import Image

class FormProcessor:
    def __init__(self, image_path):
        self.image_path = image_path
        self.image = cv2.imread(image_path)
        if self.image is None:
            raise FileNotFoundError(f"Could not open image: {image_path}")
        self.processed_data = {}

        # Ensure Tesseract path is set correctly (Windows only)
        pytesseract.pytesseract.tesseract_cmd = r"C:\\Program Files\\Tesseract-OCR\\tesseract.exe"

    def preprocess_image(self):
        """Preprocess image for better OCR results"""
        gray = cv2.cvtColor(self.image, cv2.COLOR_BGR2GRAY)
        denoised = cv2.fastNlMeansDenoising(gray, h=30)
        _, binary = cv2.threshold(denoised, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        return binary

    def get_field_roi(self, y1, y2, x1, x2):
        """Extract Region of Interest (ROI) from image"""
        return self.image[y1:y2, x1:x2]

    def extract_text_field(self, roi):
        """Extract text from an image region"""
        text = pytesseract.image_to_string(roi, config='--psm 6').strip()
        return text if text else "N/A"

    def extract_patient_info(self):
        """Extract patient information"""
        try:
            name_roi = self.get_field_roi(100, 130, 200, 400)
            dob_roi = self.get_field_roi(100, 130, 500, 600)
            self.processed_data['patient_name'] = self.extract_text_field(name_roi)
            self.processed_data['dob'] = self.extract_text_field(dob_roi)
        except Exception as e:
            print(f"Error extracting patient info: {str(e)}")

    def extract_difficulty_ratings(self):
        """Extract difficulty ratings"""
        ratings = {}
        tasks = ['bending', 'putting_on_shoes', 'sleeping', 'standing',
                 'stairs', 'walking', 'driving', 'preparing_meal', 'yard_work', 'picking_up_items']
        
        y_start = 150
        y_increment = 30
        for i, task in enumerate(tasks):
            try:
                roi = self.get_field_roi(y_start + i*y_increment, y_start + (i+1)*y_increment, 400, 500)
                value = int(self.extract_text_field(roi)) if self.extract_text_field(roi).isdigit() else 0
                ratings[task] = value
            except Exception:
                ratings[task] = 0
        
        self.processed_data['difficulty_ratings'] = ratings

    def extract_pain_symptoms(self):
        """Extract pain symptoms"""
        symptoms = {}
        pain_types = ['pain', 'numbness', 'tingling', 'burning', 'tightness']
        
        y_start = 700
        for i, pain_type in enumerate(pain_types):
            try:
                roi = self.get_field_roi(y_start, y_start + 30, 200 + i*100, 250 + i*100)
                value = int(self.extract_text_field(roi)) if self.extract_text_field(roi).isdigit() else 0
                symptoms[pain_type] = value
            except Exception:
                symptoms[pain_type] = 0
        
        self.processed_data['pain_symptoms'] = symptoms

    def extract_medical_data(self):
        """Extract medical assistant data"""
        medical_data = {}
        fields = ['blood_pressure', 'hr', 'weight', 'height']
        
        y_start = 800
        for i, field in enumerate(fields):
            try:
                roi = self.get_field_roi(y_start, y_start + 30, 200 + i*100, 250 + i*100)
                value = self.extract_text_field(roi)
                medical_data[field] = value
            except Exception:
                medical_data[field] = "N/A"
        
        self.processed_data['medical_assistant_data'] = medical_data

    def process_form(self):
        """Process entire form"""
        print("Processing form...")
        preprocessed = self.preprocess_image()
        self.extract_patient_info()
        self.extract_difficulty_ratings()
        self.extract_pain_symptoms()
        self.extract_medical_data()
        
        self.processed_data['processed_at'] = datetime.now().isoformat()
        return self.processed_data

    def save_to_json(self, output_path='processed_form.json'):
        """Save processed data to JSON file"""
        try:
            with open(output_path, 'w') as f:
                json.dump(self.processed_data, f, indent=4)
            print(f"Data saved to {output_path}")
        except Exception as e:
            print(f"Error saving JSON file: {str(e)}")


def main():
    try:
        processor = FormProcessor('sample_form.jpg')
        data = processor.process_form()
        processor.save_to_json()
        print("Form processed successfully!")
        print(json.dumps(data, indent=4))
    except FileNotFoundError as fnf_error:
        print(f"File error: {str(fnf_error)}")
    except Exception as e:
        print(f"Error processing form: {str(e)}")


if __name__ == "__main__":
    main()
