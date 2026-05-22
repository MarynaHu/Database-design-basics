--DROP TABLE IF EXISTS vehicle_assignments CASCADE;
--DROP TABLE IF EXISTS gps_trackers CASCADE;
--DROP TABLE IF EXISTS drivers CASCADE;
--DROP TABLE IF EXISTS branches CASCADE;

-- 1. Створюємо таблицю філій (1:M)
CREATE TABLE IF NOT EXISTS branches (
    branch_id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    city VARCHAR(50) NOT NULL,
    address VARCHAR(100) NOT NULL
);

-- Додаємо зовнішній ключ до існуючої таблиці машин
ALTER TABLE company_vehicles 
ADD COLUMN IF NOT EXISTS branch_id INT;

-- Безпечне додавання зв'язку
ALTER TABLE company_vehicles 
DROP CONSTRAINT IF EXISTS fk_vehicle_branch;

ALTER TABLE company_vehicles
ADD CONSTRAINT fk_vehicle_branch 
FOREIGN KEY (branch_id) REFERENCES branches(branch_id) ON DELETE SET NULL;


-- 2. Створюємо таблицю GPS-трекерів (1:0..1)
CREATE TABLE IF NOT EXISTS gps_trackers (
    tracker_id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    vehicle_id INT UNIQUE, -- UNIQUE робить зв'язок 1:1
    serial_number VARCHAR(50) NOT NULL UNIQUE,
    installation_date DATE DEFAULT CURRENT_DATE,
    CONSTRAINT fk_tracker_vehicle 
        FOREIGN KEY (vehicle_id) REFERENCES company_vehicles(id) ON DELETE CASCADE
);


-- 3. Створюємо таблицю водіїв (для M:N)
CREATE TABLE IF NOT EXISTS drivers (
    driver_id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    first_name VARCHAR(50) NOT NULL,
    last_name VARCHAR(50) NOT NULL,
    license_category VARCHAR(10) NOT NULL
);

-- 4. Створюємо проміжну таблицю для зв'язку (M:N)
CREATE TABLE IF NOT EXISTS vehicle_assignments (
    assignment_id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    vehicle_id INT NOT NULL,
    driver_id INT NOT NULL,
    assignment_date DATE DEFAULT CURRENT_DATE,
    CONSTRAINT fk_assignment_vehicle 
        FOREIGN KEY (vehicle_id) REFERENCES company_vehicles(id) ON DELETE CASCADE,
    CONSTRAINT fk_assignment_driver 
        FOREIGN KEY (driver_id) REFERENCES drivers(driver_id) ON DELETE CASCADE
);


---------- Додаємо данні ----------
-- 1. Додаємо філії
INSERT INTO branches (city, address) VALUES 
('Minneapolis, MN', '100 Northern Route'),
('Des Moines, IA', '250 Central Hub'),
('Dallas, TX', '777 Southern Hwy');

-- 2. Прив'язуємо існуючі машини до цих філій 
UPDATE company_vehicles SET branch_id = 1 WHERE id IN (1, 3, 4);
UPDATE company_vehicles SET branch_id = 2 WHERE id IN (5, 6, 7);
UPDATE company_vehicles SET branch_id = 3 WHERE id IN (8, 10);

-- 3. Додаємо GPS-трекери тільки на деякі машини (зв'язок 1:0..1)
INSERT INTO gps_trackers (vehicle_id, serial_number) VALUES 
(1, 'TRK-99001-MN'),
(3, 'TRK-99002-MN'),
(4, 'TRK-88001-IA'),
(7, 'TRK-77001-TX');

-- 4. Додаємо водіїв
INSERT INTO drivers (first_name, last_name, license_category) VALUES 
('John', 'Smith', 'CE'),
('Michael', 'Johnson', 'CE'),
('Sarah', 'Connor', 'C');


-- 5. Призначаємо водіїв на машини
INSERT INTO vehicle_assignments (vehicle_id, driver_id, assignment_date) VALUES 
(1, 1, '2026-05-10'), -- Джон їздить на машині 1
(3, 1, '2026-05-15'), -- Джон також їздив машині 2
(4, 2, '2026-05-18'), -- Майкл на машині 4
(7, 3, '2026-05-20'); -- Сара на машині 7


---------- Перевірка ----------
SELECT 
    v.full_name AS "Vehicle", 
    v.license_plate AS "License plate", 
    b.city AS "city"
FROM company_vehicles v
INNER JOIN branches b ON v.branch_id = b.branch_id;

SELECT 
    v.license_plate, 
    v.status, 
    g.serial_number AS "Serial number GPS"
FROM company_vehicles v
INNER JOIN gps_trackers g ON v.id = g.vehicle_id;

SELECT 
    d.first_name || ' ' || d.last_name AS "Driver",
    d.license_category AS "Category",
    v.make || ' ' || v.model AS "Car",
    a.assignment_date AS "Assignment date"
FROM drivers d
-- Спочатку приєднуємо проміжну таблицю призначень до водіїв
INNER JOIN vehicle_assignments a ON d.driver_id = a.driver_id
-- Потім приєднуємо машини до проміжної таблиці
INNER JOIN company_vehicles v ON a.vehicle_id = v.id;

SELECT b.city, b.address 
FROM branches b
WHERE EXISTS (
    SELECT 1 
    FROM company_vehicles v 
    WHERE v.branch_id = b.branch_id 
      AND v.mileage > 100000 
      AND v.status = 'Active'
);


SELECT v.full_name, v.license_plate, v.status
FROM company_vehicles v
WHERE NOT EXISTS (
    SELECT 1 
    FROM vehicle_assignments a 
    WHERE a.vehicle_id = v.id
);