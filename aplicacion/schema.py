esquema = [
'DROP SCHEMA IF EXISTS vetki CASCADE;',
'CREATE SCHEMA vetki;',
'SET search_path TO vetki;',
"""

-- 3. TABLAS MAESTRAS (CATÁLOGOS)
CREATE TABLE species_data (
    species_id SERIAL PRIMARY KEY,
    species_name VARCHAR(50) NOT NULL UNIQUE
);

-- 4. USUARIOS DEL SISTEMA (Dueños del entorno lógico)
CREATE TABLE vetki.user_data (
    user_id SERIAL PRIMARY KEY,
    user_rut VARCHAR(20) UNIQUE,
    user_email VARCHAR(100) NULL,
    user_names VARCHAR(40) NOT NULL,
    user_surnames VARCHAR(40),
    user_password VARCHAR(255) NOT NULL
);

-- 5. ENTIDADES PRINCIPALES (MASCOTAS Y TUTORES)
CREATE TABLE pet_data (
    pet_id SERIAL PRIMARY KEY,
    pet_user_id INTEGER,
    pet_species_id INTEGER,
    pet_names VARCHAR(100) NOT NULL,
    pet_race VARCHAR(50),
    pet_datebirth DATE,
    pet_microchip VARCHAR(50),
    pet_gender VARCHAR(20),
    pet_color VARCHAR(50),
    pet_reproductive_status VARCHAR(50),
    CONSTRAINT fk_pet_user FOREIGN KEY (pet_user_id) 
        REFERENCES vetki.user_data(user_id) ON DELETE CASCADE,
    CONSTRAINT fk_pet_species FOREIGN KEY (pet_species_id) 
        REFERENCES species_data(species_id) ON DELETE RESTRICT
);
-- 6. AGENDA MÉDICA
CREATE TABLE vetki.appointments (
    appointment_id SERIAL PRIMARY KEY,
    pet_id INTEGER REFERENCES vetki.pet_data(pet_id) ON DELETE CASCADE,
    appointment_date DATE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


"""]
