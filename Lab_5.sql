INSERT INTO branches (city, address) 
VALUES ('Nashville, TN', '500 Music Gateway')

INSERT INTO drivers (first_name, last_name, license_category) 
VALUES ('James', 'Smith', 'C')


---- LEFT JOIN ----

--- Пошук автомобілів без GPS-трекерів
SELECT 
    v.id, 
    v.full_name, 
    v.license_plate, 
    g.serial_number AS "Serial number GPS"
FROM company_vehicles v
LEFT JOIN gps_trackers g ON v.id = g.vehicle_id;

--- Звіт по філіях та їхньому автопарку
SELECT 
    b.city AS "City", 
    b.address, 
    v.license_plate AS "License plate", 
    v.status
FROM branches b
LEFT JOIN company_vehicles v ON b.branch_id = v.branch_id;

--- Аналіз активності водіїв
SELECT 
    d.first_name || ' ' || d.last_name AS "Dtiver",
    d.license_category,
    a.assignment_date AS "Assignment date"
FROM drivers d
LEFT JOIN vehicle_assignments a ON d.driver_id = a.driver_id;

---- RIGHT JOIN ----

--- Пошук автомобілів серійного номера
SELECT 
    g.serial_number, 
    v.full_name, 
    v.license_plate
FROM gps_trackers g
RIGHT JOIN company_vehicles v ON g.vehicle_id = v.id;

--- Авто не закріплені за філіями
SELECT 
    b.city AS "Сity", 
    v.full_name AS "Vehicle", 
    v.license_plate
FROM branches b
RIGHT JOIN company_vehicles v ON b.branch_id = v.branch_id;

--- Перевірка призначень на неіснуючі ID водіїв
SELECT 
    a.assignment_id, 
    d.last_name AS "Driver's last name", 
    d.license_category
FROM vehicle_assignments a
RIGHT JOIN drivers d ON a.driver_id = d.driver_id;

---- CROSS JOIN ----

--- Матриця можливих відряджень водіїв
SELECT 
    d.first_name || ' ' || d.last_name AS "Driver", 
    b.city AS "Potential city"
FROM drivers d
CROSS JOIN branches b;

--- Комбінація кожної машини з кожним серійним номером трекера в системі
SELECT 
    v.license_plate, 
    g.serial_number
FROM company_vehicles v
CROSS JOIN gps_trackers g;

---- FULL JOIN ----

--- Повна інвентаризація зв'язку "Авто-Трекер"
SELECT 
    v.id AS "Car ID", 
    v.license_plate, 
    g.tracker_id AS "Tracker id", 
    g.serial_number
FROM company_vehicles v
FULL JOIN gps_trackers g ON v.id = g.vehicle_id;

--- Повний звіт взаємодії Філій та Автомобілів
SELECT 
    b.city, 
    v.id, 
    v.full_name
FROM branches b
FULL JOIN company_vehicles v ON b.branch_id = v.branch_id;