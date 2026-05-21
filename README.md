# Лабораторна робота 4

Побудувно ще додатково декілька таблиць, які мають хоча б по одному вигляду кожного з співвідношень між собою на основі варіанту 6. Додано усі необхідні зовнішні ключі(foreign keys)

## Файл містить
- Створено таблицю `branches` (Філії) для реалізації зв'язку **1:M (Один до багатьох)** з головною таблицею `company_vehicles`.
- Створено таблицю `gps_trackers` (GPS-трекери) зі зв'язком **1:0..1 (Один до нуля або одного)** через обмеження `UNIQUE` на зовнішній ключ.
- Створено таблиці `drivers` (Водії) та проміжну таблицю `vehicle_assignments` (Призначення) для реалізації зв'язку **M:N (Багато до багатьох)**.
- Налаштовано логіку цілісності даних за допомогою зовнішніх ключів `FOREIGN KEY` та додано тестові дані для перевірки зв'язків.
- Написано SQL-запити з використанням `INNER JOIN` для об'єднання даних з декількох таблиць (наприклад, повний журнал призначень екіпажів).
- Написано підзапити з використанням `EXISTS` для пошуку філій з активним транспортом.
- Написано підзапити з використанням `NOT EXISTS` для пошуку резервних автомобілів без призначених водіїв.

## Запуск проєкту

### **Технології**:
- **Система управління базами даних**: PostgreSQL.
- **Інструментарій:** pgAdmin 4 або psql.

### **Використання**:

**1. З'єднання трьох таблиць (INNER JOIN):**
```sql
-- Показати список машин разом із містами, до яких вони приписані
SELECT 
    v.full_name AS "Транспорт", 
    v.license_plate AS "Номер", 
    b.city AS "Філія"
FROM company_vehicles v
INNER JOIN branches b ON v.branch_id = b.branch_id;
```

**2. Зв'язок "Один до Нуля/Одного" (INNER JOIN двох таблиць)**
```
-- Знайти тільки ті машини, на яких встановлено GPS-трекер
SELECT 
    v.license_plate, 
    v.status, 
    g.serial_number AS "Serial number GPS"
FROM company_vehicles v
INNER JOIN gps_trackers g ON v.id = g.vehicle_id;
```
**3.Зв'язок "Багато до Багатьох" (INNER JOIN трьох таблиць)**
```
-- Отримати повний звіт: який водій, на якій машині та коли працював
SELECT 
    d.first_name || ' ' || d.last_name AS "Driver",
    d.license_category AS "Category",
    v.make || ' ' || v.model AS "Car",
    a.assignment_date AS "Assignment date"
FROM drivers d
INNER JOIN vehicle_assignments a ON d.driver_id = a.driver_id
INNER JOIN company_vehicles v ON a.vehicle_id = v.id;
```
**4. Використання EXISTS (Підзапит)**
```
-- Знайти філії, в яких є хоча б одна активна машина з пробігом більше 100 000
SELECT b.city, b.address 
FROM branches b
WHERE EXISTS (
    SELECT 1 
    FROM company_vehicles v 
    WHERE v.branch_id = b.branch_id 
      AND v.mileage > 100000 
      AND v.status = 'Active'
);
```
**5. Використання NOT EXISTS (Підзапит)**
```
-- Знайти "вільні" машини — ті, на які наразі не призначено жодного водія
SELECT v.full_name, v.license_plate, v.status
FROM company_vehicles v
WHERE NOT EXISTS (
    SELECT 1 
    FROM vehicle_assignments a 
    WHERE a.vehicle_id = v.id
);
```
