--Кількість автомобілів у кожній філії
SELECT 
    b.city AS "City", 
    COUNT(v.id) AS "Number of cars"
FROM branches b
INNER JOIN company_vehicles v ON b.branch_id = v.branch_id
GROUP BY b.city
HAVING COUNT(v.id) > 1;

--Пошук малоактивних або нових філій
SELECT 
    b.city AS "City", 
    COUNT(v.id) AS "Number of cars"
FROM branches b
LEFT JOIN company_vehicles v ON b.branch_id = v.branch_id
GROUP BY b.city
HAVING COUNT(v.id) < 5;

--Середній пробіг машин за філіями
SELECT 
    b.city AS "City", 
    ROUND(AVG(v.mileage), 2) AS "Average mileage"
FROM branches b
INNER JOIN company_vehicles v ON b.branch_id = v.branch_id
GROUP BY b.city
HAVING AVG(v.mileage) > 10000;

--Рейтинг активності водіїв
SELECT 
    d.first_name || ' ' || d.last_name AS "Driver",
    COUNT(a.assignment_id) AS "Number of appointments"
FROM vehicle_assignments a
RIGHT JOIN drivers d ON a.driver_id = d.driver_id
GROUP BY d.first_name, d.last_name
HAVING COUNT(a.assignment_id) >= 1;

--Завантаженість конкретних автомобілів
SELECT 
    v.license_plate AS "License plate", 
    v.make || ' ' || v.model AS "Model",
    COUNT(a.driver_id) AS "Number of departures"
FROM company_vehicles v
LEFT JOIN vehicle_assignments a ON v.id = a.vehicle_id
GROUP BY v.license_plate, v.make, v.model
HAVING COUNT(a.driver_id) > 0;

--Аналіз встановлених GPS-трекерів по філіях
SELECT 
    b.city AS "City", 
    COUNT(g.tracker_id) AS "Trackers installed"
FROM branches b
INNER JOIN company_vehicles v ON b.branch_id = v.branch_id
INNER JOIN gps_trackers g ON v.id = g.vehicle_id
GROUP BY b.city
HAVING COUNT(g.tracker_id) > 0;

-- Останні призначення за категоріями водіїв
SELECT 
    d.license_category AS "License category",
    MAX(a.assignment_date) AS "Last assignment date"
FROM drivers d
INNER JOIN vehicle_assignments a ON d.driver_id = a.driver_id
INNER JOIN company_vehicles v ON a.vehicle_id = v.id
WHERE v.status = 'Active'
GROUP BY d.license_category
HAVING MAX(a.assignment_date) >= '2026-05-01';