import random
import sqlite3
from db_utils import load_json, get_connection

# ==================================================================
# СОЗДАНИЕ СХЕМЫ (единая точка)
# ==================================================================


def create_schema(conn: sqlite3.Connection) -> None:
    """Создаёт обе таблицы в одной транзакции."""
    cur = conn.cursor()
    cur.execute("DROP TABLE IF EXISTS cars")     # сначала зависимая
    cur.execute("DROP TABLE IF EXISTS dealers")  # потом главная

    cur.execute("""
        CREATE TABLE dealers (
            id      INTEGER PRIMARY KEY AUTOINCREMENT,
            name    TEXT NOT NULL,
            city    TEXT,
            address TEXT,
            area    TEXT,
            rating  REAL
        )
    """)

    cur.execute("""
        CREATE TABLE cars (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            firm      TEXT    NOT NULL,
            model     TEXT    NOT NULL,
            year      INTEGER,
            power     INTEGER,
            color     TEXT,
            price     INTEGER,
            dealer_id INTEGER,
            FOREIGN KEY (dealer_id)
                REFERENCES dealers(id)
                ON DELETE SET NULL
                ON UPDATE CASCADE
        )
    """)

    conn.commit()   # единый коммит: обе таблицы создаются вместе


# ==================================================================
# ЛАБОРАТОРНАЯ РАБОТА №1: АВТОМОБИЛИ
# ==================================================================

def lab1(conn: sqlite3.Connection) -> None:
    print("\n" + "=" * 60)
    print("ЛАБОРАТОРНАЯ РАБОТА №1")
    print("=" * 60)

    try:
        cars = load_json('cars.json').get('cars', [])
    except Exception as e:
        print(f"Ошибка загрузки cars.json: {e}")
        return

    cur = conn.cursor()

    # Импорт машин: dealer_id = NULL (FK разрешает NULL)
    cur.executemany("""
        INSERT INTO cars (firm, model, year, power, color, price, dealer_id)
        VALUES (:firm, :model, :year, :power, :color, :price, NULL)
    """, cars)
    conn.commit()
    print(f"\n[Импорт] Загружено автомобилей: {len(cars)}")

    # Первые 20 записей из таблицы cars
    cur.execute("""
            SELECT id, firm, model, year, power, color, price, dealer_id
            FROM cars
            ORDER BY id
            LIMIT 20
        """)
    print("\nПервые 20 автомобилей в таблице cars:")
    print(f"   {'id':<4} {'firm':<15} {'model':<20} {'year':<6} "
          f"{'power':<7} {'color':<10} {'price':<10} {'dealer_id'}")
    print("   " + "-" * 85)
    for row in cur.fetchall():
        print(f"   {row['id']:<4} {row['firm']:<15} {row['model']:<20} "
              f"{row['year']:<6} {row['power']:<7} {row['color']:<10} "
              f"{row['price']:<10} {row['dealer_id']}")


# ==================================================================
# ЛАБОРАТОРНАЯ РАБОТА №2: ДИЛЕРЫ + FK-СВЯЗЬ
# ==================================================================

def link_cars_to_dealers(conn: sqlite3.Connection) -> int:
    """UPDATE cars: каждому авто — случайный dealer_id.
    SQLite проверит FK: dealer_id должен существовать в dealers."""
    cur = conn.cursor()
    cur.execute("SELECT id FROM dealers")
    dealer_ids = [r["id"] for r in cur.fetchall()]
    if not dealer_ids:
        return 0
    cur.execute("SELECT id FROM cars")
    car_ids = [r["id"] for r in cur.fetchall()]
    for car_id in car_ids:
        cur.execute(
            "UPDATE cars SET dealer_id = ? WHERE id = ?",
            (random.choice(dealer_ids), car_id)
        )
    conn.commit()
    return len(car_ids)


def lab2(conn: sqlite3.Connection) -> None:
    print("\n" + "=" * 60)
    print("ЛАБОРАТОРНАЯ РАБОТА №2")
    print("=" * 60)

    try:
        dealers = load_json('dealers.json')
    except Exception as e:
        print(f"Ошибка загрузки dealers.json: {e}")
        return

    cur = conn.cursor()

    # Импорт дилеров
    cur.executemany("""
        INSERT INTO dealers (name, city, address, area, rating)
        VALUES (:Name, :City, :Address, :Area, :Rating)
    """, dealers)
    conn.commit()
    print(f"\n[Импорт] Загружено дилеров: {len(dealers)}")

    # Связываем cars.dealer_id → dealers.id (FK теперь проверяется)
    linked = link_cars_to_dealers(conn)
    print(f"[Связь] Привязано автомобилей к дилерам: {linked}")

    # Первые 20 записей из таблицы dealers
    cur.execute("""
            SELECT id, name, city, address, area, rating
            FROM dealers
            ORDER BY id
            LIMIT 20
        """)
    print("\nПервые 20 дилеров в таблице dealers:")
    print(f"   {'id':<4} {'name':<18} {'city':<15} {'address':<30} "
          f"{'area':<22} {'rating'}")
    print("   " + "-" * 95)
    for row in cur.fetchall():
        print(f"   {row['id']:<4} {row['name']:<18} {row['city']:<15} "
              f"{row['address']:<30} {row['area']:<22} {row['rating']}")

    # ------- Демонстрация: FK действительно работает -------
    print("\n[Проверка FK] Попытка вставить машину с dealer_id = 999999:")
    try:
        cur.execute("""
            INSERT INTO cars (firm, model, year, power, color, price, dealer_id)
            VALUES ('Test', 'FK-Check', 2024, 100, 'black', 1, 999999)
        """)
        conn.commit()
        print("   ❌ FK НЕ работает — вставка прошла (это ошибка).")
    except sqlite3.IntegrityError as e:
        print(f"   ✅ FK работает — IntegrityError: {e}")


# ==================================================================
# ТОЧКА ВХОДА
# ==================================================================

if __name__ == "__main__":
    conn = get_connection()
    try:
        create_schema(conn)   # dealers → cars, один COMMIT
        lab1(conn)            # импорт машин + 2 запроса
        lab2(conn)            # импорт дилеров + связь + 2 запроса
    finally:
        conn.close()
