CREATE DATABASE dhcp_leases_db;

CREATE USER 'dhcp_user'@'localhost' IDENTIFIED BY 'your_password_db';
GRANT ALL PRIVILEGES ON dhcp_leases_db.* TO 'dhcp_user'@'localhost';

FLUSH PRIVILEGES;

USE dhcp_leases_db;

CREATE TABLE active_leases (
    id INT AUTO_INCREMENT PRIMARY KEY,
    ip_address VARCHAR(15) NOT NULL UNIQUE,
    mac_address VARCHAR(17) NOT NULL,
    hostname VARCHAR(255),
    lease_start DATETIME NOT NULL,
    lease_end DATETIME NOT NULL,
    state VARCHAR(20) NOT NULL,
    last_update TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);