-- create the databases
CREATE DATABASE IF NOT EXISTS 'app_db';

-- create the users for each database
CREATE USER 'app_usr'@'%' IDENTIFIED BY 'LocalPassword';
GRANT SELECT ON `app_db`.* TO 'app_usr'@'%';

FLUSH PRIVILEGES;