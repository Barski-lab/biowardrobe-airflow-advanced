CREATE TABLE `ems`.`advancedtype` (
  `id`             int(11) NOT NULL AUTO_INCREMENT,
  `atype`          varchar(100) DEFAULT NULL,
  `workflow`       varchar(255) DEFAULT NULL,
  `template`       text DEFAULT NULL,
  `upload_rules`   text DEFAULT NULL,
  `job_dispatcher` varchar(255) DEFAULT NULL,
  `job_gatherer`   varchar(255) DEFAULT NULL,
  `pool`           varchar(100) DEFAULT NULL,
  `etype_id`       varchar(100) NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `atype` (`atype`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8;