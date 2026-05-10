from models import Vehicle
from repository import InMemoryVehicleRepository

def print_menu():
    print("\n--- Керування автопарком ---")
    print("1. Додати авто (Create)")
    print("2. Показати всі авто (Read - з пейджингом)")
    print("3. Оновити дані авто (Update)")
    print("4. Видалити авто (Delete)")
    print("0. Вихід")

def main():
    # Ініціалізуємо наше сховище. 
    # В майбутньому тут буде: repo = PostgresVehicleRepository(db_connection)
    repo = InMemoryVehicleRepository()
    
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
            print("Невідома команда. Спробуйте ще раз.")

if __name__ == "__main__":
    main()