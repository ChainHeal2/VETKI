esquema = [
'DROP SCHEMA IF EXISTS vetki CASCADE;',
'CREATE SCHEMA vetki;',
'SET search_path TO vetki;',
"""

-- 1. USUARIOS DEL SISTEMA (Dueños del entorno lógico)
CREATE TABLE vetki.user_data (
    user_id SERIAL PRIMARY KEY,
    user_google_id VARCHAR(255) UNIQUE,
    user_names VARCHAR(40) NOT NULL,
    user_email VARCHAR(100) NULL,
    user_rut VARCHAR(20) NULL,
    user_password VARCHAR(255) NULL,
    user_role VARCHAR(20) DEFAULT 'veterinario'
);

-- 2. ENTIDADES PRINCIPALES (MASCOTAS Y TUTORES)
CREATE TABLE pet_data (
    pet_id SERIAL PRIMARY KEY,
    pet_user_id INTEGER,
    pet_species_name VARCHAR(50),
    pet_names VARCHAR(100) NOT NULL,
    pet_race VARCHAR(50),
    pet_datebirth DATE,
    pet_microchip VARCHAR(50),
    pet_gender VARCHAR(20),
    pet_color VARCHAR(50),
    pet_reproductive_status VARCHAR(50),
    pet_tutor_name VARCHAR(50),
    pet_tutor_address VARCHAR(50) NULL,
    pet_tutor_phone VARCHAR(15) NULL,
    CONSTRAINT fk_pet_user FOREIGN KEY (pet_user_id) 
        REFERENCES vetki.user_data(user_id) ON DELETE CASCADE
);
-- 3. AGENDA MÉDICA
CREATE TABLE vetki.appointments (
    appointment_id SERIAL PRIMARY KEY,
    appointment_google_event_id VARCHAR(255) NULL,
    pet_id INTEGER REFERENCES vetki.pet_data(pet_id) ON DELETE CASCADE,
    appointment_date TIMESTAMP NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 4. FICHA MÉDICA
CREATE TABLE vetki.medical_records (
    medical_record_id SERIAL PRIMARY KEY,
    medical_record_reason VARCHAR(20) NOT NULL,
    medical_record_weight DOUBLE PRECISION NULL,
    medical_record_temperature DOUBLE PRECISION NULL,
    medical_record_heart DOUBLE PRECISION NULL,
    medical_record_respiratory DOUBLE PRECISION NULL,
    medical_record_water DOUBLE PRECISION NULL,
    medical_record_capillary DOUBLE PRECISION NULL,
    medical_record_arterial DOUBLE PRECISION NULL,
    medical_record_date DATE NOT NULL,
    medical_record_medical_history TEXT NULL,
    medical_record_signals TEXT NULL,
    medical_record_diagnosis TEXT NULL,
    medical_record_treatment TEXT NULL,
    medical_record_pet_id INTEGER REFERENCES vetki.pet_data(pet_id) ON DELETE CASCADE,
    medical_record_user_id INTEGER REFERENCES vetki.user_data(user_id) ON DELETE CASCADE,
    medical_record_appointment_id INTEGER NULL REFERENCES vetki.appointments(appointment_id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 5. HISTORIAL DE VACUNACIÓN
CREATE TABLE vetki.vaccinations (
    id SERIAL PRIMARY KEY,
    pet_id INTEGER NOT NULL REFERENCES vetki.pet_data(pet_id) ON DELETE CASCADE,
    vaccine_name VARCHAR(120) NOT NULL,
    application_date DATE NOT NULL,
    next_due_date DATE NULL,
    lot_number VARCHAR(80) NULL,
    veterinarian_notes TEXT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    CONSTRAINT vaccination_due_after_application
        CHECK (next_due_date IS NULL OR next_due_date >= application_date)
);

-- Casos agregados para el dashboard epidemiológico.
CREATE TABLE vetki.disease_cases (
    id SERIAL PRIMARY KEY,
    disease_name VARCHAR(80) NOT NULL,
    report_date DATE NOT NULL,
    case_count INTEGER NOT NULL CHECK (case_count >= 0)
);

--6. VISTAS PARA CONSULTAS
CREATE OR REPLACE VIEW vetki.vw_medical_history AS
SELECT r.medical_record_id, r.medical_record_reason, r.medical_record_weight, r.medical_record_temperature,
       r.medical_record_heart, r.medical_record_respiratory, r.medical_record_water, r.medical_record_capillary, r.medical_record_arterial,
       r.medical_record_date, r.medical_record_medical_history, r.medical_record_diagnosis, r.medical_record_treatment,
       r.medical_record_pet_id, r.medical_record_user_id, r.medical_record_appointment_id,
       p.pet_names, p.pet_species_name
FROM vetki.medical_records r
JOIN vetki.pet_data p ON r.medical_record_pet_id = p.pet_id;

CREATE OR REPLACE VIEW vw_pet_tutor AS
SELECT p.pet_id,p.pet_user_id,p.pet_names, p.pet_species_name,pet_race, p.pet_datebirth, p.pet_microchip, p.pet_gender, p.pet_color, p.pet_reproductive_status,
         p.pet_tutor_name, p.pet_tutor_address, p.pet_tutor_phone from vetki.pet_data p
JOIN vetki.user_data u ON p.pet_user_id = u.user_id;

"""]
