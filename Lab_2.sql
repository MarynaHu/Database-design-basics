-- Table: public.Company vehicles

--DROP TABLE IF EXISTS public."сompany_vehicles";

--DROP TABLE public."company_vehicles";

CREATE TABLE IF NOT EXISTS public."company_vehicles"
(
	-- Primary Key: автоматично генерує унікальний ID
    id INT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    
    -- Not Null: марка та модель
    make VARCHAR(50) NOT NULL,
    model VARCHAR(50) NOT NULL,
    
    -- Unique: номерний знак не може повторюватися в базі
    license_plate VARCHAR(20) NOT NULL UNIQUE,
    
    -- Check: рік випуску не може бути меншим за 1990 і більшим за поточний
    year INT NOT NULL CHECK (year >= 2010 AND year <= EXTRACT(YEAR FROM CURRENT_DATE) + 1),
    
    -- Default + Check: пробіг за замовчуванням 0
    mileage INT NOT NULL DEFAULT 0 CHECK (mileage >= 0),
    
    -- Default + Check: статус
    status VARCHAR(20) NOT NULL DEFAULT 'Active' 
        CHECK (status IN ('Active', 'In Repair', 'Decommissioned')),
    
    -- Null: додаткові нотатки можуть бути порожніми
    notes TEXT NULL,
    
    -- Computed column (Згенерована колонка): автоматично склеює марку та модель
    full_name VARCHAR(100) GENERATED ALWAYS AS (make || ' ' || model) STORED
);

-- Додавання запису
INSERT INTO company_vehicles (make, model, license_plate, year, mileage, status, notes)
VALUES ('Ford', 'Transit', 'KA4213EB', 2019, 125000, 'Active', 'Основний робочий фургон');

DO $$
DECLARE -- Оголошення змінних
    i INT := 1;
    n INT := 10; -- кількість нових записів
BEGIN
    WHILE i <= n LOOP
        INSERT INTO company_vehicles (make, model, license_plate, year, mileage)
        VALUES (
            'Brand_' || i, 
            'Model_X', 
            'KA' || LPAD(i::text, 4, '0') || 'EE', -- Генерація номерів
            2010 + (i % 16),                        -- Роки випуску
            i * 15000                              -- Генерація пробігу
        );
        i := i + 1;
    END LOOP;
END $$;
	
-- 1. Простий SELECT: Отримати всі активні авто
SELECT * FROM company_vehicles WHERE status = 'Active';

-- 2. FETCH (аналог TOP): Отримати 3 авто з найбільшим пробігом
SELECT * FROM company_vehicles ORDER BY mileage DESC FETCH FIRST 3 ROWS ONLY;

-- 3. OFFSET + FETCH (Пейджинг): Пропустити 2 найстаріші авто і показати наступні 3
SELECT * FROM company_vehicles ORDER BY year ASC OFFSET 2 ROWS FETCH NEXT 3 ROWS ONLY;

-- 4. LIKE: Знайти всі авто, марка яких починається на 'Brand_'
SELECT * FROM company_vehicles WHERE make LIKE 'Brand_%';

-- 5. IN: Знайти авто конкретних років випуску
SELECT * FROM company_vehicles WHERE year IN (2018, 2019, 2020);

-- 6. IS NULL: Знайти авто, у яких немає жодних нотаток
SELECT * FROM company_vehicles WHERE notes IS NULL;

-- 7. IS NOT NULL: Знайти авто, у яких є записи в нотатках
SELECT * FROM company_vehicles WHERE notes IS NOT NULL;

-- 8. AND: Автомобілі з пробігом менше 50000 і статусом 'Active'
SELECT full_name, license_plate FROM company_vehicles WHERE mileage < 50000 AND status = 'Active';

-- 9. OR: Автомобілі, які в ремонті АБО старші за 2017 рік
SELECT * FROM company_vehicles WHERE status = 'In Repair' OR year < 2017;

-- 10. BETWEEN: Автомобілі з пробігом у певному діапазоні
SELECT * FROM company_vehicles WHERE mileage BETWEEN 50000 AND 100000;

-- 11. NOT: Всі авто, крім списаних (Decommissioned)
SELECT * FROM company_vehicles WHERE NOT status = 'Decommissioned';

-- 12. Комбінація (LIKE, AND, ORDER BY): Пошук за номером, сортування за віком
SELECT * FROM company_vehicles 
WHERE license_plate LIKE '%EE' AND status = 'Active' 
ORDER BY year DESC;

-- 13. Складний SELECT (IN, OR, FETCH):
SELECT full_name, mileage FROM company_vehicles 
WHERE (year IN (2021, 2022) OR mileage = 0) 
ORDER BY id ASC FETCH FIRST 5 ROWS ONLY;

-- 14. Простий UPDATE: Збільшити пробіг конкретному авто
UPDATE company_vehicles SET mileage = mileage + 500 WHERE id = 1;

-- 15. UPDATE з IN: Відправити в ремонт авто за списком ID
UPDATE company_vehicles SET status = 'In Repair' WHERE id IN (3, 5, 7);

-- 16. UPDATE з BETWEEN та IS NULL: Додати нотатку старим авто, якщо її ще немає
UPDATE company_vehicles 
SET notes = 'Потребує ТО' 
WHERE year BETWEEN 2015 AND 2018 AND notes IS NULL;

-- 17. UPDATE з LIKE: Змінити статус для тестово згенерованих машин
UPDATE company_vehicles 
SET status = 'Decommissioned' 
WHERE make LIKE 'Brand_8%';

-- 18. Простий DELETE: Видалити авто за ID
DELETE FROM company_vehicles WHERE id = 2;

-- 19. DELETE з IN: Видалити всі списані машини
DELETE FROM company_vehicles WHERE status IN ('Decommissioned');

-- 20. DELETE з комбінацією (OR, AND, LIKE): Видалення за складною умовою
DELETE FROM company_vehicles 
WHERE (mileage > 300000 OR year < 2010) AND make NOT LIKE 'Ford%';
