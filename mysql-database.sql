SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='TRADITIONAL,ALLOW_INVALID_DATES';

CREATE SCHEMA IF NOT EXISTS `nlnog` DEFAULT CHARACTER SET latin1 ;
USE `nlnog` ;

-- -----------------------------------------------------
-- Table `nlnog`.`participants`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `nlnog`.`participants` (
  `id` INT(11) NOT NULL AUTO_INCREMENT,
  `company` VARCHAR(255) NOT NULL,
  `url` VARCHAR(255) NULL DEFAULT NULL,
  `contact` VARCHAR(255) NOT NULL,
  `email` VARCHAR(255) NOT NULL,
  `nocemail` VARCHAR(255) NOT NULL,
  `companydesc` VARCHAR(64000) NULL DEFAULT NULL,
  `public` INT(11) NULL DEFAULT NULL,
  `tstamp` INT(11) NULL DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE INDEX `company` (`company` ASC))
ENGINE = InnoDB
DEFAULT CHARACTER SET = latin1;


-- -----------------------------------------------------
-- Table `nlnog`.`users`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `nlnog`.`users` (
  `id` INT(11) NOT NULL AUTO_INCREMENT,
  `username` VARCHAR(255) NULL DEFAULT NULL,
  `userid` INT(11) NULL DEFAULT NULL,
  `active` INT(11) NULL DEFAULT NULL,
  `participant` INT(11) NOT NULL,
  `admin` INT(11) NULL DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE INDEX `username` (`username` ASC),
  INDEX `participant` (`participant` ASC),
  CONSTRAINT `users_ibfk_1`
    FOREIGN KEY (`participant`)
    REFERENCES `nlnog`.`participants` (`id`))
ENGINE = InnoDB
DEFAULT CHARACTER SET = latin1;


-- -----------------------------------------------------
-- Table `nlnog`.`machines`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `nlnog`.`machines` (
  `id` INT(11) NOT NULL AUTO_INCREMENT,
  `hostname` VARCHAR(255) NOT NULL,
  `v4` VARCHAR(255) NULL DEFAULT NULL,
  `v4active` TINYINT(2) NULL,
  `v6` VARCHAR(255) NULL DEFAULT NULL,
  `v6active` TINYINT(2) NULL,
  `autnum` INT(11) NOT NULL,
  `country` VARCHAR(2) NULL DEFAULT NULL,
  `state` VARCHAR(2) NULL DEFAULT NULL,
  `dc` VARCHAR(2048) NULL DEFAULT NULL,
  `geo` VARCHAR(255) NULL DEFAULT NULL,
  `owner` INT(11) NOT NULL,
  `tstamp` INT(11) NULL DEFAULT NULL,
  `active` TINYINT(1) NULL DEFAULT NULL,
  `deckardserver` TINYINT(1) NULL DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE INDEX `hostname` (`hostname` ASC),
  UNIQUE INDEX `v4` (`v4` ASC),
  UNIQUE INDEX `v6` (`v6` ASC),
  INDEX `owner` (`owner` ASC),
  CONSTRAINT `machines_ibfk_1`
    FOREIGN KEY (`owner`)
    REFERENCES `nlnog`.`users` (`id`))
ENGINE = InnoDB
DEFAULT CHARACTER SET = latin1;


-- -----------------------------------------------------
-- Table `nlnog`.`mremarks`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `nlnog`.`mremarks` (
  `id` INT(11) NOT NULL AUTO_INCREMENT,
  `remark` VARCHAR(64000) NULL DEFAULT NULL,
  `tstamp` INT(11) NULL DEFAULT NULL,
  `machine` INT(11) NOT NULL,
  PRIMARY KEY (`id`),
  INDEX `machine` (`machine` ASC),
  CONSTRAINT `mremarks_ibfk_1`
    FOREIGN KEY (`machine`)
    REFERENCES `nlnog`.`machines` (`id`))
ENGINE = InnoDB
DEFAULT CHARACTER SET = latin1;


-- -----------------------------------------------------
-- Table `nlnog`.`premarks`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `nlnog`.`premarks` (
  `id` INT(11) NOT NULL AUTO_INCREMENT,
  `remark` VARCHAR(64000) NULL DEFAULT NULL,
  `tstamp` INT(11) NULL DEFAULT NULL,
  `participant` INT(11) NOT NULL,
  PRIMARY KEY (`id`),
  INDEX `participant` (`participant` ASC),
  CONSTRAINT `premarks_ibfk_1`
    FOREIGN KEY (`participant`)
    REFERENCES `nlnog`.`participants` (`id`))
ENGINE = InnoDB
DEFAULT CHARACTER SET = latin1;


-- -----------------------------------------------------
-- Table `nlnog`.`sshkeys`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `nlnog`.`sshkeys` (
  `id` INT(11) NOT NULL AUTO_INCREMENT,
  `keytype` VARCHAR(255) NOT NULL,
  `sshkey` VARCHAR(2048) NOT NULL,
  `keyid` VARCHAR(255) NULL DEFAULT NULL,
  `user` INT(11) NOT NULL,
  PRIMARY KEY (`id`),
  INDEX `user` (`user` ASC),
  CONSTRAINT `sshkeys_ibfk_1`
    FOREIGN KEY (`user`)
    REFERENCES `nlnog`.`users` (`id`))
ENGINE = InnoDB
DEFAULT CHARACTER SET = latin1;


-- -----------------------------------------------------
-- Table `nlnog`.`machinestates`
-- -----------------------------------------------------
CREATE TABLE IF NOT EXISTS `nlnog`.`machinestates` (
  `master_id` INT(11) NOT NULL,
  `slave_id` INT(11) NOT NULL,
  `protocol` INT(8) NOT NULL COMMENT 'IANA protocol numbers\n4 = ipv4\n41 = ipv6\n',
  `active` TINYINT NOT NULL,
  `tstamp` INT(11) NOT NULL,
  PRIMARY KEY (`master_id`, `slave_id`, `protocol`),
  INDEX `fk_machinestates_machines2_idx` (`slave_id` ASC),
  CONSTRAINT `fk_machinestates_machines1`
    FOREIGN KEY (`master_id`)
    REFERENCES `nlnog`.`machines` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_machinestates_machines2`
    FOREIGN KEY (`slave_id`)
    REFERENCES `nlnog`.`machines` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;


SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;
