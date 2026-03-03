CREATE TABLE IF NOT EXISTS incidents_p (
    id INT AUTO_INCREMENT PRIMARY KEY,
    incident_code VARCHAR(50),
    service VARCHAR(100),
    severity VARCHAR(50),
    description TEXT,
    status VARCHAR(50),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);