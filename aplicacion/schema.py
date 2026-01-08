esquema = [

"DROP SCHEMA IF EXISTS `mibitacora` ;",
"CREATE SCHEMA IF NOT EXISTS `mibitacora` ;",
"USE `mibitacora`;",

"DROP TABLE IF EXISTS `mibitacora`.`user` ;",
"""
CREATE TABLE IF NOT EXISTS `mibitacora`.`user` (
  `id_user` INT NOT NULL AUTO_INCREMENT,
  `username` VARCHAR(45) NULL,
  `password` VARCHAR(162) NULL,
  PRIMARY KEY (`id_user`))
ENGINE = InnoDB;""",

"DROP TABLE IF EXISTS `mibitacora`.`task` ;",

"""CREATE TABLE IF NOT EXISTS `mibitacora`.`task` (
  `id_task` INT NOT NULL AUTO_INCREMENT,
  `title_task` VARCHAR(45) NOT NULL,
  `task` VARCHAR(45) NULL,
  `date_create_task` DATETIME NOT NULL,
  `date_end_task` DATE NULL,
  `fk_user_id` INT NULL,
  PRIMARY KEY (`id_task`),
  INDEX `fk_user_task_idx` (`fk_user_id` ASC) VISIBLE,
  CONSTRAINT `fk_user_task`
    FOREIGN KEY (`fk_user_id`)
    REFERENCES `mibitacora`.`user` (`id_user`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;"""]