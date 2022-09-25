-- Adminer 4.7.6 MySQL dump

SET NAMES utf8;
SET time_zone = '+00:00';
SET foreign_key_checks = 0;
SET sql_mode = 'NO_AUTO_VALUE_ON_ZERO';

SET NAMES utf8mb4;

DROP TABLE IF EXISTS `tg_emails`;
CREATE TABLE `tg_emails` (
  `id` bigint unsigned NOT NULL AUTO_INCREMENT,
  `message_id` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_520_ci NOT NULL,
  `created_at` datetime NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `message_id` (`message_id`),
  KEY `created_at` (`created_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_520_ci;


DROP TABLE IF EXISTS `tg_mail_msg`;
CREATE TABLE `tg_mail_msg` (
  `id` bigint unsigned NOT NULL AUTO_INCREMENT,
  `email_id` bigint unsigned NOT NULL,
  `chat_id` bigint NOT NULL,
  `tg_msg_id` bigint unsigned NOT NULL,
  `created_at` datetime NOT NULL,
  PRIMARY KEY (`id`),
  KEY `email_id` (`email_id`),
  KEY `chat_id` (`chat_id`),
  KEY `tg_msg_id` (`tg_msg_id`),
  KEY `created_at` (`created_at`),
  CONSTRAINT `tg_mail_msg_ibfk_2` FOREIGN KEY (`email_id`) REFERENCES `tg_emails` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_520_ci;


DROP TABLE IF EXISTS `tg_atoms`;
CREATE TABLE `tg_atoms` (
  `id` bigint unsigned NOT NULL AUTO_INCREMENT,
  `url` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_520_ci NOT NULL,
  `created_at` datetime NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `url` (`url`),
  KEY `created_at` (`created_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_520_ci;


DROP TABLE IF EXISTS `tg_broadcasts`;
CREATE TABLE `tg_broadcasts` (
  `id` bigint unsigned NOT NULL AUTO_INCREMENT,
  `chat_id` bigint NOT NULL,
  `username` varchar(32),
  `name` varchar(64) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_520_ci NOT NULL,
  `type` varchar(32) NOT NULL,
  `link` varchar(64),
  `created_at` datetime NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `chat_id` (`chat_id`),
  KEY `created_at` (`created_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_520_ci;

-- [ SPLITTER ] ------------------------------------------------------------------------------

DROP TABLE IF EXISTS `dc_emails`;
CREATE TABLE `dc_emails` (
  `id` bigint unsigned NOT NULL AUTO_INCREMENT,
  `message_id` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_520_ci NOT NULL,
  `created_at` datetime NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `message_id` (`message_id`),
  KEY `created_at` (`created_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_520_ci;


DROP TABLE IF EXISTS `dc_mail_msg`;
CREATE TABLE `dc_mail_msg` (
  `id` bigint unsigned NOT NULL AUTO_INCREMENT,
  `email_id` bigint unsigned NOT NULL,
  `channel_id` bigint NOT NULL,
  `dc_msg_id` bigint unsigned NOT NULL,
  `created_at` datetime NOT NULL,
  PRIMARY KEY (`id`),
  KEY `email_id` (`email_id`),
  KEY `channel_id` (`channel_id`),
  KEY `dc_msg_id` (`dc_msg_id`),
  KEY `created_at` (`created_at`),
  CONSTRAINT `dc_mail_msg_ibfk_2` FOREIGN KEY (`email_id`) REFERENCES `dc_emails` (`id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_520_ci;


DROP TABLE IF EXISTS `dc_atoms`;
CREATE TABLE `dc_atoms` (
  `id` bigint unsigned NOT NULL AUTO_INCREMENT,
  `url` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_520_ci NOT NULL,
  `created_at` datetime NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `url` (`url`),
  KEY `created_at` (`created_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_520_ci;


DROP TABLE IF EXISTS `dc_broadcasts`;
CREATE TABLE `dc_broadcasts` (
  `id` bigint unsigned NOT NULL AUTO_INCREMENT,
  `guild_id` BIGINT UNSIGNED NOT NULL,
  `channel_id` BIGINT UNSIGNED NOT NULL,
  `channel_name` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_520_ci NOT NULL,
  `channel_link` varchar(255) CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_520_ci NOT NULL,
  `created_at` datetime NOT NULL,
  PRIMARY KEY (`id`),
  KEY `guild_id` (`guild_id`),
  UNIQUE KEY `channel_id` (`channel_id`),
  KEY `channel_name` (`channel_name`),
  KEY `channel_link` (`channel_link`),
  KEY `created_at` (`created_at`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_520_ci;

-- 2022-07-07 14:25:28
