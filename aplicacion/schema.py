esquema = [
    # En Postgres usamos CASCADE para borrar el esquema y todo su contenido (tablas, índices) de una vez
    "DROP SCHEMA IF EXISTS vetki CASCADE;",
    "CREATE SCHEMA vetki;",
    # Establecemos el camino de búsqueda para no tener que escribir 'vetki.' antes de cada tabla
    "SET search_path TO vetki;",

    # Tabla User (Usamos comillas dobles porque 'user' es una palabra reservada en Postgres)
    """
    CREATE TABLE "user_personal" (
      user_id SERIAL PRIMARY KEY,
      username VARCHAR(45) NOT NULL UNIQUE,
      password VARCHAR(168) NULL,
      email_user VARCHAR(50) NULL,
      level_user INT NULL
    );
    """,

    # Tabla Personal Data
    """  
    CREATE TABLE personal_data (
      personal_id SERIAL PRIMARY KEY,
      run_personal VARCHAR(13) NULL,
      names_personal VARCHAR(45) NULL,
      surnames VARCHAR(45) NULL,
      phone_personal VARCHAR(45) NULL,
      user_id INT NOT NULL,
      CONSTRAINT fk_personal_data_user
        FOREIGN KEY (user_id)
        REFERENCES "user_personal" (user_id)
        ON DELETE NO ACTION
        ON UPDATE NO ACTION
    );
    """,

    # Tabla Tutor
    """
    CREATE TABLE tutor (
      tutor_id SERIAL PRIMARY KEY,
      tutor_run VARCHAR(12) NULL UNIQUE,
      names_tutor VARCHAR(45) NULL,
      surnames_tutor VARCHAR(45) NULL,
      phone_tutor INT NULL,
      address_tutor VARCHAR(60) NULL,
      email_tutor VARCHAR(45) NULL
    );
    """,

    # Tabla Species
    """
    CREATE TABLE species (
      species_id SERIAL PRIMARY KEY,
      name_species VARCHAR(45) NULL
    );
    """,

    # Tabla Pet
    """
    CREATE TABLE pet (
      pet_id SERIAL PRIMARY KEY,
      names_pet VARCHAR(45) NOT NULL,
      race_pet VARCHAR(45) NULL,
      date_birth DATE NULL,
      microchip VARCHAR(45) NULL,
      gender VARCHAR(45) NULL,
      color VARCHAR(45) NULL,
      reproductive_status VARCHAR(45) NULL,
      species_species_id INT NOT NULL,
      CONSTRAINT fk_pet_species1
        FOREIGN KEY (species_species_id)
        REFERENCES species (species_id)
        ON DELETE NO ACTION
        ON UPDATE NO ACTION
    );
    """,

    # Tabla Pet_Tutor (Intermedia)
    """
    CREATE TABLE pet_tutor (
      pet_pet_id INT NOT NULL,
      tutor_tutor_id INT NOT NULL,
      type_tutor INT NULL,
      date_register VARCHAR(45) NULL,
      CONSTRAINT fk_pet_tutor_pet1
        FOREIGN KEY (pet_pet_id)
        REFERENCES pet (pet_id),
      CONSTRAINT fk_pet_tutor_tutor1
        FOREIGN KEY (tutor_tutor_id)
        REFERENCES tutor (tutor_id)
    );
    """,

    # Tabla Medical History
    """
    CREATE TABLE medical_history (
      history_id SERIAL,
      date_history VARCHAR(45) NULL,
      reason_history VARCHAR(45) NULL,
      history_note VARCHAR(200) NULL,
      pet_pet_id INT NOT NULL,
      personal_data_personal_id INT NOT NULL,
      PRIMARY KEY (history_id, personal_data_personal_id),
      CONSTRAINT fk_medical_history_pet1
        FOREIGN KEY (pet_pet_id)
        REFERENCES pet (pet_id),
      CONSTRAINT fk_medical_history_personal_data1
        FOREIGN KEY (personal_data_personal_id)
        REFERENCES personal_data (personal_id)
    );
    """,

    # Tabla Vaccination
    """
    CREATE TABLE vaccination (
      vacci_id SERIAL,
      name_vacci VARCHAR(45) NULL,
      date_vacci DATE NULL,
      lote VARCHAR(45) NULL,
      pet_pet_id INT NOT NULL,
      PRIMARY KEY (vacci_id, pet_pet_id),
      CONSTRAINT fk_vaccination_pet1
        FOREIGN KEY (pet_pet_id)
        REFERENCES pet (pet_id)
    );
    """,

    # Tabla Alergies
    """
    CREATE TABLE alergies (
      alergies_id SERIAL,
      alergeno VARCHAR(45) NULL,
      severidad VARCHAR(45) NULL,
      reaccion VARCHAR(45) NULL,
      pet_pet_id INT NOT NULL,
      PRIMARY KEY (alergies_id, pet_pet_id),
      CONSTRAINT fk_alergies_pet1
        FOREIGN KEY (pet_pet_id)
        REFERENCES pet (pet_id)
    );
    """
]