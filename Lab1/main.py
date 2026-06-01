from models import Vehicle
from repository import InMemoryVehicleRepository, PostgresVehicleRepository, JsonVehicleRepository,RedisProtobufVehicleRepository, VehicleRepository


def test_repository(repo: VehicleRepository):
    print(f"\n{'='*40}")
    print(f"🚀 ТЕСТУВАННЯ: {repo.__class__.__name__}")
    print(f"{'='*40}")

    try:
        # 1. CREATE (Створення)
        print("[1/5] Тест CREATE...")
        # Припускаємо, що конструктор Vehicle виглядає так (адаптуйте під свій):
        new_vehicle = Vehicle(id=0, make="Ford", model="Transit", year=2022, license_plate="AA0000XX")
        saved_vehicle = repo.create(new_vehicle)
        print(f"  ✓ Створено авто з ID: {saved_vehicle.id}")

        # 2. READ (Отримання за ID)
        print("[2/5] Тест GET_BY_ID...")
        fetched_vehicle = repo.get_by_id(saved_vehicle.id)
        if fetched_vehicle:
            print(f"  ✓ Знайдено: {fetched_vehicle.make} {fetched_vehicle.model} ({fetched_vehicle.license_plate})")
        else:
            print("  ❌ Помилка: Авто не знайдено!")

        # 3. READ ALL (Отримання списку)
        print("[3/5] Тест GET_ALL...")
        all_vehicles = repo.get_all(limit=5)
        print(f"  ✓ Отримано записів: {len(all_vehicles)}")

        # 4. UPDATE (Оновлення)
        print("[4/5] Тест UPDATE...")
        fetched_vehicle.license_plate = "XX9999ZZ"
        repo.update(fetched_vehicle)
        updated_vehicle = repo.get_by_id(saved_vehicle.id)
        if updated_vehicle.license_plate == "XX9999ZZ":
            print(f"  ✓ Оновлено успішно. Новий номер: {updated_vehicle.license_plate}")
        else:
            print("  ❌ Помилка: Дані не оновилися!")

        # 5. DELETE (Видалення)
        print("[5/5] Тест DELETE...")
        is_deleted = repo.delete(saved_vehicle.id)
        check_deleted = repo.get_by_id(saved_vehicle.id)
        if is_deleted and check_deleted is None:
            print("  ✓ Видалено успішно. Запис більше не існує.")
        else:
            print("  ❌ Помилка при видаленні!")

    except Exception as e:
        print(f"\n❌ КРИТИЧНА ПОМИЛКА під час тестування:")
        print(e)
    
    print(f"{'='*40}\n")

def print_menu():
    print("\n--- Керування автопарком ---")
    print("1. Додати авто (Create)")
    print("2. Показати всі авто (Read - з пейджингом)")
    print("3. Оновити дані авто (Update)")
    print("4. Видалити авто (Delete)")
    print("0. Вихід")

def get_repository() -> VehicleRepository:
    print("Оберіть сховище:")
    print("1 - В оперативній пам'яті")
    print("2 - JSON файл")
    print("3 - Redis (Protobuf)")
    print("4 - SQL Server")
    
    choice = input("Ваш вибір: ")
    
    if choice == "1":
        return InMemoryVehicleRepository()
    elif choice == "2":
        return JsonVehicleRepository("vehicles.json")
    elif choice == "3":
        return RedisProtobufVehicleRepository()
    elif choice == "4":
        # Формат підключення до PostgreSQL
        # Замініть YOUR_PASSWORD та YOUR_DB_NAME на реальні дані
        conn_str = "dbname='company vehicles' user=postgres password=admin host=localhost port=5432"
        return PostgresVehicleRepository(conn_str)
    else:
        print("Невідомий вибір, завантажую In-Memory...")
        return InMemoryVehicleRepository()

def main():

    repo = get_repository()
    test_repository(repo)
    '''
    while True:
        print_menu()
        choice = input("Оберіть дію: ")

        if choice == '1':
            make = input("Марка: ")
            model = input("Модель: ")
            plate = input("Номерний знак: ")
            year = int(input("Рік випуску: "))
            new_vehicle = Vehicle(id=None, make=make, model=model, license_plate=plate, year=year)
            created = repo.create(new_vehicle)
            print(f"✅ Додано: {created}")

        elif choice == '2':
            limit = int(input("Скільки записів показати на сторінці? (наприклад, 10): "))
            offset = int(input("Скільки записів пропустити? (offset): "))
            vehicles = repo.get_all(limit=limit, offset=offset)
            print(f"\n--- Список авто (показано {len(vehicles)}) ---")
            for v in vehicles:
                print(v)

        elif choice == '3':
            v_id = int(input("ID авто для оновлення: "))
            existing = repo.get_by_id(v_id)
            if existing:
                print(f"Поточні дані: {existing}")
                make = input(f"Нова марка (або Enter щоб залишити {existing.make}): ") or existing.make
                model = input(f"Нова модель (або Enter щоб залишити {existing.model}): ") or existing.model
                plate = input(f"Новий номер (або Enter щоб залишити {existing.license_plate}): ") or existing.license_plate
                
                year_input = input(f"Новий рік (або Enter щоб залишити {existing.year}): ")
                year = int(year_input) if year_input else existing.year
                
                updated_vehicle = Vehicle(id=v_id, make=make, model=model, license_plate=plate, year=year)
                repo.update(updated_vehicle)
                print("✅ Запис оновлено!")
            else:
                print("❌ Авто з таким ID не знайдено.")

        elif choice == '4':
            v_id = int(input("ID авто для видалення: "))
            if repo.delete(v_id):
                print("✅ Запис видалено!")
            else:
                print("❌ Авто не знайдено.")

        elif choice == '0':
            print("Вихід...")
            break
        else:
            print("Невідома команда. Спробуйте ще раз.")'''

if __name__ == "__main__":
    main()