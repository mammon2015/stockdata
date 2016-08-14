/*
Navicat MySQL Data Transfer

Source Server         : MySQL - Local
Source Server Version : 50713
Source Host           : localhost:3306
Source Database       : stockdata

Target Server Type    : MYSQL
Target Server Version : 50713
File Encoding         : 65001

Date: 2016-08-13 18:41:38
*/

SET FOREIGN_KEY_CHECKS=0;

-- ----------------------------
-- Table structure for num_extend_data_copy
-- ----------------------------
DROP TABLE IF EXISTS `num_extend_data_copy`;
CREATE TABLE `num_extend_data_copy` (
  `code` char(6) NOT NULL,
  `type` char(4) DEFAULT NULL,
  `item` varchar(10) NOT NULL,
  `date` date NOT NULL,
  `value` decimal(20,4) DEFAULT NULL,
  PRIMARY KEY (`code`,`item`,`date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
