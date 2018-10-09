ALTER TABLE `ems`.`genelist`
ADD COLUMN params text DEFAULT '{}' AFTER parent_id;