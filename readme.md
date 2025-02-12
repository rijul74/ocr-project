/*This project automates the extraction of structured data from patient assessment forms (scanned images or PDFs) using OCR (Optical Character Recognition) and stores the extracted data into a PostgreSQL database.

Key Features:

Uses Tesseract OCR & EasyOCR for text extraction.
Extracts structured fields like patient details, medical data, difficulty ratings, and pain symptoms.
Converts extracted text into a structured JSON format.
Stores the data in a PostgreSQL database for future analysis.
Provides querying capabilities to fetch patient history and medical records.







Tech Stack
Backend: Python (psycopg2, pytesseract, easyocr, opencv, json, re)
Database: PostgreSQL
Tools: pgAdmin, VS Code, GitHub
Libraries: psycopg2, pytesseract, opencv-python, easyocr
 Project Structure







graphql

OCR_Project/
│── ocr_extraction.py      # Extracts text from images/PDFs using OCR
│── database.py            # Stores extracted data into PostgreSQL
│── db_operations.py       # Manages database queries and operations
│── processed_form.json    # Sample JSON output after OCR processing
│── requirements.txt       # List of required dependencies
│── README.md              # Project documentation
│── sample_form.jpg        # Sample input form for OCR processing




 Step 1: Setup & Installation
1️⃣ Install Dependencies
Run the following command to install required libraries:

bash

pip install -r requirements.txt
OR install them manually:

bash

pip install pytesseract opencv-python easyocr psycopg2



Install PostgreSQL
Download from PostgreSQL Official Website

During installation:

Set a password for postgres user
Use default port 5432
Install pgAdmin for database management
Verify installation:

bash
Copy
Edit
psql --version
Start PostgreSQL Service (Windows Command Prompt):
bash



net start postgresql-x64-17
(Replace 17 with your PostgreSQL version.)

Step 2: Configure the Database
 Open psql and Create a Database
Run:

bash

psql -U postgres
Enter the password and create the database:

sql
Copy
Edit
CREATE DATABASE ocr_db;
Switch to the database:

sql

ocr_db;

 Create Required Tables
sql

CREATE TABLE patients (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    dob DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE form_data (
    id SERIAL PRIMARY KEY,
    patient_id INTEGER REFERENCES patients(id),
    difficulty_ratings JSONB,
    pain_symptoms JSONB,
    medical_data JSONB,
    processed_at TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE patient_changes (
    id SERIAL PRIMARY KEY,
    form_data_id INTEGER REFERENCES form_data(id),
    change_type VARCHAR(50),
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


Step 3: Extract Data from Patient Forms
1️⃣ Run OCR Extraction
Make sure the sample form image (sample_form.jpg) is placed in the project folder.

Run:

bash
Copy
Edit
python ocr_extraction.py


This will:

Extract text from the image using OCR
Convert extracted data into structured JSON
Save the output in processed_form.json
Example JSON Output:

json
Copy
Edit
{
    "patient_name": "John Doe",
    "dob": "1985-10-25",
    "difficulty_ratings": {
        "bending": 3,
        "walking": 2
    },
    "pain_symptoms": {
        "pain": 4,
        "numbness": 1
    },
    "medical_assistant_data": {
        "blood_pressure": "120/80",
        "hr": 80
    }
}


Step 4: Insert Data into PostgreSQL
Run:

bash


python database.py
✅ This will:

Insert extracted OCR data into the PostgreSQL database
Store patient details, medical records, and changes


 Step 5: Fetch Patient Data
1 View Inserted Data in PostgreSQL
Run:

bash

psql -U postgres -d ocr_db
Then check:

sql

SELECT * FROM patients;
SELECT * FROM form_data;
SELECT * FROM patient_changes;
2

 Fetch All Data for a Specific Patient
Run this SQL query to get patient details, form data, and medical changes:

sql

SELECT 
    p.id AS patient_id,
    p.name AS patient_name,
    p.dob AS date_of_birth,
    f.id AS form_id,
    f.difficulty_ratings,
    f.pain_symptoms,
    f.medical_data,
    f.processed_at,
    pc.change_type,
    pc.description
FROM patients p
LEFT JOIN form_data f ON p.id = f.patient_id
LEFT JOIN patient_changes pc ON f.id = pc.form_data_id
WHERE p.id = 5;
(Replace 5 with the actual patient ID.)
*/
