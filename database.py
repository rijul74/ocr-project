# db_operations.py

import psycopg2
from psycopg2.extras import Json
import json
from datetime import datetime
import logging

class DatabaseManager:
    def __init__(self, dbname, user, password, host, port):
        self.connection_params = {
            'dbname': dbname,
            'user': user,
            'password': password,
            'host': host,
            'port': port
        }
        self.setup_logging()

    def setup_logging(self):
        """Setup logging configuration"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            filename='db_operations.log'
        )
        self.logger = logging.getLogger(__name__)

    def connect(self):
        """Create database connection"""
        try:
            return psycopg2.connect(**self.connection_params)
        except psycopg2.Error as e:
            self.logger.error(f"Database connection error: {str(e)}")
            raise

    def create_tables(self):
        """Create necessary database tables"""
        conn = self.connect()
        cur = conn.cursor()
        
        try:
            # Patients table
            cur.execute("""
                CREATE TABLE IF NOT EXISTS patients (
                    id SERIAL PRIMARY KEY,
                    name VARCHAR(255) NOT NULL,
                    dob DATE,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)

            # Form data table
            cur.execute("""
                CREATE TABLE IF NOT EXISTS form_data (
                    id SERIAL PRIMARY KEY,
                    patient_id INTEGER REFERENCES patients(id),
                    difficulty_ratings JSONB,
                    pain_symptoms JSONB,
                    medical_data JSONB,
                    processed_at TIMESTAMP,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)

            # Patient changes table
            cur.execute("""
                CREATE TABLE IF NOT EXISTS patient_changes (
                    id SERIAL PRIMARY KEY,
                    form_data_id INTEGER REFERENCES form_data(id),
                    change_type VARCHAR(50),
                    description TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)

            conn.commit()
            self.logger.info("Database tables created successfully")
            
        except psycopg2.Error as e:
            conn.rollback()
            self.logger.error(f"Error creating tables: {str(e)}")
            raise
        finally:
            cur.close()
            conn.close()

    def insert_form_data(self, form_data):
        """Insert processed form data into database"""
        conn = self.connect()
        cur = conn.cursor()
        
        try:
            # Insert patient data
            cur.execute("""
                INSERT INTO patients (name, dob)
                VALUES (%s, %s)
                RETURNING id;
            """, (form_data['patient_name'], form_data['dob']))
            
            patient_id = cur.fetchone()[0]
            
            # Insert form data
            cur.execute("""
                INSERT INTO form_data 
                (patient_id, difficulty_ratings, pain_symptoms, medical_data, processed_at)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING id;
            """, (
                patient_id,
                Json(form_data['difficulty_ratings']),
                Json(form_data['pain_symptoms']),
                Json(form_data['medical_assistant_data']),
                datetime.now()
            ))
            
            form_data_id = cur.fetchone()[0]
            
            # Insert patient changes
            for change_type, description in form_data.get('patient_changes', {}).items():
                cur.execute("""
                    INSERT INTO patient_changes (form_data_id, change_type, description)
                    VALUES (%s, %s, %s);
                """, (form_data_id, change_type, description))
            
            conn.commit()
            self.logger.info(f"Form data inserted successfully for patient {patient_id}")
            return patient_id
            
        except psycopg2.Error as e:
            conn.rollback()
            self.logger.error(f"Error inserting form data: {str(e)}")
            raise
        finally:
            cur.close()
            conn.close()

    def get_patient_history(self, patient_id):
        """Retrieve patient's form history"""
        conn = self.connect()
        cur = conn.cursor()
        
        try:
            cur.execute("""
                SELECT 
                    f.processed_at,
                    f.difficulty_ratings,
                    f.pain_symptoms,
                    f.medical_data,
                    pc.change_type,
                    pc.description
                FROM form_data f
                LEFT JOIN patient_changes pc ON f.id = pc.form_data_id
                WHERE f.patient_id = %s
                ORDER BY f.processed_at DESC;
            """, (patient_id,))
            
            return cur.fetchall()
            
        except psycopg2.Error as e:
            self.logger.error(f"Error retrieving patient history: {str(e)}")
            raise
        finally:
            cur.close()
            conn.close()

def main():
    # Database connection parameters
    db_params = {
        'dbname': 'ocr_db',
        'user': 'postgres',
        'password': 'Rr@123',
        'host': 'localhost',
        'port': '5432'
    }
    
    try:
        # Initialize database manager
        db_manager = DatabaseManager(**db_params)
        
        # Create tables
        db_manager.create_tables()
        
        # Read processed form data
        with open('processed_form.json', 'r') as f:
            form_data = json.load(f)
        
        # Insert data into database
        patient_id = db_manager.insert_form_data(form_data)
        print(f"Data inserted successfully for patient ID: {patient_id}")
        
        # Retrieve patient history
        history = db_manager.get_patient_history(patient_id)
        print("Patient history:", history)
        
    except Exception as e:
        print(f"Error in database operations: {str(e)}")

if __name__ == "__main__":
    main()