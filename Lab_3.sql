-- Таблиця для ведення історії (аудиту)
CREATE TABLE IF NOT EXISTS vehicles_history (
    history_id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    vehicle_id INT,
    action_type VARCHAR(10), -- 'INSERT', 'UPDATE', 'DELETE'
    old_data JSONB,         -- Дані до змін у форматі JSON
    change_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Функція для тригера
CREATE OR REPLACE FUNCTION vehicle_audit_func()
RETURNS TRIGGER AS $$
BEGIN
    IF (TG_OP = 'DELETE') THEN
        INSERT INTO vehicles_history (vehicle_id, action_type, old_data)
        VALUES (OLD.id, 'DELETE', to_jsonb(OLD));
        RETURN OLD;
    ELSIF (TG_OP = 'UPDATE') THEN
        INSERT INTO vehicles_history (vehicle_id, action_type, old_data)
        VALUES (NEW.id, 'UPDATE', to_jsonb(OLD));
        RETURN NEW;
    ELSIF (TG_OP = 'INSERT') THEN
        INSERT INTO vehicles_history (vehicle_id, action_type, old_data)
        VALUES (NEW.id, 'INSERT', to_jsonb(NEW));
        RETURN NEW;
    END IF;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

-- Сам тригер
DROP TRIGGER IF EXISTS trg_vehicle_audit ON company_vehicles;
CREATE TRIGGER trg_vehicle_audit
AFTER INSERT OR UPDATE OR DELETE ON company_vehicles
FOR EACH ROW EXECUTE FUNCTION vehicle_audit_func();

-- 1. VIEW: Стан автопарку (тільки активні машини з пробігом)
CREATE OR REPLACE VIEW view_active_fleet AS
SELECT full_name, license_plate, mileage, year
FROM company_vehicles
WHERE status = 'Active' AND mileage > 0;

-- 2. Скалярна функція: Розрахунок податку на основі віку авто
CREATE OR REPLACE FUNCTION calculate_vehicle_tax(v_year INT)
RETURNS DECIMAL AS $$
DECLARE
    age INT;
BEGIN
    age := EXTRACT(YEAR FROM CURRENT_DATE) - v_year;
    IF age < 5 THEN RETURN 1000.00;
    ELSIF age < 10 THEN RETURN 2500.00;
    ELSE RETURN 5000.00;
    END IF;
END;
$$ LANGUAGE plpgsql;

-- 3. Таблична функція: Пошук авто за діапазоном пробігу
CREATE OR REPLACE FUNCTION get_vehicles_by_mileage(min_mil INT, max_mil INT)
RETURNS TABLE(v_name VARCHAR, v_plate VARCHAR, v_mileage INT) AS $$
BEGIN
    RETURN QUERY
    SELECT full_name, license_plate, mileage
    FROM company_vehicles
    WHERE mileage BETWEEN min_mil AND max_mil;
END;
$$ LANGUAGE plpgsql;

-- Процедура для генерації даних
CREATE OR REPLACE PROCEDURE generate_vehicles(n INT DEFAULT 5)
AS $$
DECLARE
    i INT := 1;
BEGIN
    WHILE i <= n LOOP
        INSERT INTO company_vehicles (make, model, license_plate, year, mileage)
        VALUES (
            'Gen_Brand_' || i, 
            'Model_Z', 
            'CB' || LPAD((random()*9999)::int::text, 4, '0') || 'HT',
            2010 + (i % 15),
            (random() * 50000)::int
        );
        i := i + 1;
    END LOOP;
END;
$$ LANGUAGE plpgsql;

-- Виклик процедури
--CALL generate_vehicles(7);

-- Вивести назву, номер та статус (діючий або видалений)
SELECT full_name, license_plate, 'Current' as source_status
FROM company_vehicles

UNION ALL

SELECT (old_data->>'full_name')::varchar, (old_data->>'license_plate')::varchar, 'Deleted'
FROM vehicles_history
WHERE action_type = 'DELETE'

ORDER BY source_status;