esquema = [
'DROP SCHEMA IF EXISTS vetki CASCADE;',
'CREATE SCHEMA vetki;',
'SET search_path TO vetki;',
"""

-- 4. USUARIOS DEL SISTEMA (Dueños del entorno lógico)
CREATE TABLE vetki.user_data (
    user_id SERIAL PRIMARY KEY,
    user_google_id VARCHAR(255) UNIQUE,
    user_names VARCHAR(40) NOT NULL,
    user_email VARCHAR(100) NULL,
    user_rut VARCHAR(20) NULL,
    user_password VARCHAR(255) NULL
);

-- 5. ENTIDADES PRINCIPALES (MASCOTAS Y TUTORES)
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
    pet_tutor_phone INTEGER NULL,
    CONSTRAINT fk_pet_user FOREIGN KEY (pet_user_id) 
        REFERENCES vetki.user_data(user_id) ON DELETE CASCADE
);
-- 6. AGENDA MÉDICA
CREATE TABLE vetki.appointments (
    appointment_id SERIAL PRIMARY KEY,
    appointment_google_id VARCHAR(255) UNIQUE,
    pet_id INTEGER REFERENCES vetki.pet_data(pet_id) ON DELETE CASCADE,
    appointment_date DATE NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 7. FICHA MÉDICA
CREATE TABLE vetki.medical_records (
    medical_record_id SERIAL PRIMARY KEY,
    medical_record_reason VARCHAR(20) NOT NULL,
    medical_record_weight INTEGER NULL,
    medical_record_date DATE NOT NULL,
    medical_record_diagnosis VARCHAR(255) NULL,
    medical_record_treatment VARCHAR(255) NULL,
    medical_record_pet_id INTEGER REFERENCES vetki.pet_data(pet_id) ON DELETE CASCADE,
    medical_record_user_id INTEGER REFERENCES vetki.user_data(user_id) ON DELETE CASCADE,
    medical_record_appointment_id INTEGER NULL REFERENCES vetki.appointments(appointment_id) ON DELETE CASCADE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


"""]
