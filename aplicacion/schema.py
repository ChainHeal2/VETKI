esquema = [
"DROP SCHEMA IF EXISTS `vetki`;",
"CREATE SCHEMA IF NOT EXISTS `vetki`;",
"USE `vetki`;",
"DROP TABLE IF EXISTS `vetki`.`user`;",

"""
CREATE TABLE IF NOT EXISTS `vetki`.`user` (
  `user_id` INT NOT NULL AUTO_INCREMENT,
  `username` VARCHAR(45) NOT NULL,
  `password` VARCHAR(168) NULL,
  `email_user` VARCHAR(50) NULL,
  `level_user` INT NULL,
  PRIMARY KEY (`user_id`),
  UNIQUE INDEX `username_UNIQUE` (`username` ASC) VISIBLE);
""",

"DROP TABLE IF EXISTS `vetki`.`personal_data` ;",
"""  
  CREATE TABLE IF NOT EXISTS `vetki`.`personal_data` (
  `personal_id` INT NOT NULL AUTO_INCREMENT,
  `run_personal` VARCHAR(13) NULL,
  `names_personal` VARCHAR(45) NULL,
  `surnames` VARCHAR(45) NULL,
  `phone_personal` VARCHAR(45) NULL,
  `user_id` INT NOT NULL,
  PRIMARY KEY (`personal_id`),
  INDEX `fk_user_id` (`user_id` ASC) VISIBLE,
  CONSTRAINT `fk_personal_data_user`
    FOREIGN KEY (`user_id`)
    REFERENCES `vetki`.`user` (`user_id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION);""",

"DROP TABLE IF EXISTS `vetki`.`tutor` ;",

"""
CREATE TABLE IF NOT EXISTS `vetki`.`tutor` (
  `tutor_id` INT NOT NULL AUTO_INCREMENT,
  `tutor_run` VARCHAR(12) NULL,
  `names_tutor` VARCHAR(45) NULL,
  `surnames_tutor` VARCHAR(45) NULL,
  `phone_tutor` INT NULL,
  `address_tutor` VARCHAR(60) NULL,
  `email_tutor` VARCHAR(45) NULL,
  PRIMARY KEY (`tutor_id`),
  UNIQUE INDEX `tutor_run_UNIQUE` (`tutor_run` ASC) VISIBLE);""",

"DROP TABLE IF EXISTS `vetki`.`species` ;",

"""
CREATE TABLE IF NOT EXISTS `vetki`.`species` (
  `species_id` INT NOT NULL AUTO_INCREMENT,
  `name_species` VARCHAR(45) NULL,
  PRIMARY KEY (`species_id`));""",

"DROP TABLE IF EXISTS `vetki`.`pet` ;",

"""
CREATE TABLE IF NOT EXISTS `vetki`.`pet` (
  `pet_id` INT NOT NULL AUTO_INCREMENT,
  `names_pet` VARCHAR(45) NOT NULL,
  `race_pet` VARCHAR(45) NULL,
  `date_birth` DATE NULL,
  `microchip` VARCHAR(45) NULL,
  `gender` VARCHAR(45) NULL,
  `color` VARCHAR(45) NULL,
  `reproductive_status` VARCHAR(45) NULL,
  `species_species_id` INT NOT NULL,
  PRIMARY KEY (`pet_id`),
  INDEX `fk_pet_species1_idx` (`species_species_id` ASC) VISIBLE,
  CONSTRAINT `fk_pet_species1`
    FOREIGN KEY (`species_species_id`)
    REFERENCES `vetki`.`species` (`species_id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION);
    """,

"DROP TABLE IF EXISTS `vetki`.`pet_tutor` ;",

"""
CREATE TABLE IF NOT EXISTS `vetki`.`pet_tutor` (
  `pet_pet_id` INT NOT NULL,
  `tutor_tutor_id` INT NOT NULL,
  `type_tutor` INT NULL,
  `date_register` VARCHAR(45) NULL,
  INDEX `fk_pet_tutor_pet1_idx` (`pet_pet_id` ASC) VISIBLE,
  INDEX `fk_pet_tutor_tutor1_idx` (`tutor_tutor_id` ASC) VISIBLE,
  CONSTRAINT `fk_pet_tutor_pet1`
    FOREIGN KEY (`pet_pet_id`)
    REFERENCES `vetki`.`pet` (`pet_id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_pet_tutor_tutor1`
    FOREIGN KEY (`tutor_tutor_id`)
    REFERENCES `vetki`.`tutor` (`tutor_id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION);
    """,

"DROP TABLE IF EXISTS `vetki`.`medical_history` ;",

"""
CREATE TABLE IF NOT EXISTS `vetki`.`medical_history` (
  `history_id` INT NOT NULL AUTO_INCREMENT,
  `date_history` VARCHAR(45) NULL,
  `reason_history` VARCHAR(45) NULL,
  `history_note` VARCHAR(200) NULL,
  `pet_pet_id` INT NOT NULL,
  `personal_data_personal_id` INT NOT NULL,
  PRIMARY KEY (`history_id`, `personal_data_personal_id`),
  INDEX `fk_medical_history_pet1_idx` (`pet_pet_id` ASC) VISIBLE,
  INDEX `fk_medical_history_personal_data1_idx` (`personal_data_personal_id` ASC) VISIBLE,
  CONSTRAINT `fk_medical_history_pet1`
    FOREIGN KEY (`pet_pet_id`)
    REFERENCES `vetki`.`pet` (`pet_id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_medical_history_personal_data1`
    FOREIGN KEY (`personal_data_personal_id`)
    REFERENCES `vetki`.`personal_data` (`personal_id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION);
    """,

"DROP TABLE IF EXISTS `vetki`.`vaccination` ;",

"""
CREATE TABLE IF NOT EXISTS `vetki`.`vaccination` (
  `vacci_id` INT NOT NULL AUTO_INCREMENT,
  `name_vacci` VARCHAR(45) NULL,
  `date_vacci` DATE NULL,
  `lote` VARCHAR(45) NULL,
  `pet_pet_id` INT NOT NULL,
  PRIMARY KEY (`vacci_id`, `pet_pet_id`),
  INDEX `fk_vaccination_pet1_idx` (`pet_pet_id` ASC) VISIBLE,
  CONSTRAINT `fk_vaccination_pet1`
    FOREIGN KEY (`pet_pet_id`)
    REFERENCES `vetki`.`pet` (`pet_id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION);
    """,

"DROP TABLE IF EXISTS `vetki`.`alergies` ;",

"""
CREATE TABLE IF NOT EXISTS `vetki`.`alergies` (
  `alergies_id` INT NOT NULL,
  `alergeno` VARCHAR(45) NULL,
  `severidad` VARCHAR(45) NULL,
  `reaccion` VARCHAR(45) NULL,
  `pet_pet_id` INT NOT NULL,
  PRIMARY KEY (`alergies_id`, `pet_pet_id`),
  INDEX `fk_alergies_pet1_idx` (`pet_pet_id` ASC) VISIBLE,
  CONSTRAINT `fk_alergies_pet1`
    FOREIGN KEY (`pet_pet_id`)
    REFERENCES `vetki`.`pet` (`pet_id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION);
    """
]