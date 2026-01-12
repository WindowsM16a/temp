CREATE TABLE maintenance (
    id BIGINT UNSIGNED AUTO_INCREMENT PRIMARY KEY,

    car_id BIGINT UNSIGNED NOT NULL,
    employee_id BIGINT UNSIGNED,
    approved_by_id BIGINT UNSIGNED,

    scheduled_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    completed_date DATE,
    next_service_date DATE,
    next_service_mileage INT,

    service_type VARCHAR(50),
    title VARCHAR(200),
    status VARCHAR(20),
    priority VARCHAR(20),

    cost DECIMAL(10,2) DEFAULT 0,
    labor_cost DECIMAL(10,2),
    parts_cost DECIMAL(10,2),
    tax_amount DECIMAL(10,2),

    parts_used TEXT,
    parts_quantity TEXT,
    description TEXT,
    notes TEXT,

    mileage_at_service INT DEFAULT 0,
    warranty_period INT,
    warranty_expiry_date DATE,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        ON UPDATE CURRENT_TIMESTAMP,

    CONSTRAINT fk_maintenance_car
        FOREIGN KEY (car_id)
        REFERENCES car(id)
        ON DELETE CASCADE,

    CONSTRAINT fk_maintenance_employee
        FOREIGN KEY (employee_id)
        REFERENCES employee(id)
        ON DELETE SET NULL,

    CONSTRAINT fk_maintenance_approved_by
        FOREIGN KEY (approved_by_id)
        REFERENCES employee(id)
        ON DELETE SET NULL
);

