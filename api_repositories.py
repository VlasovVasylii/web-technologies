from db_utils import get_connection
from api_models import (
    Car, CarCreate, CarUpdate,
    Dealer, DealerCreate, DealerUpdate,
)


# =============================== CARS ===============================

class CarRepository:

    def get_all(self) -> list[Car]:
        conn = get_connection()
        try:
            cur = conn.execute("SELECT * FROM cars ORDER BY id")
            return [Car(**dict(row)) for row in cur.fetchall()]
        finally:
            conn.close()

    def get_by_id(self, car_id: int) -> Car | None:
        conn = get_connection()
        try:
            cur = conn.execute("SELECT * FROM cars WHERE id = ?", (car_id,))
            row = cur.fetchone()
            return Car(**dict(row)) if row else None
        finally:
            conn.close()

    def create(self, data: CarCreate) -> Car:
        """INSERT. Возвращает созданную машину с присвоенным id."""
        conn = get_connection()
        try:
            cur = conn.execute("""
                INSERT INTO cars (firm, model, year, power, color, price, dealer_id)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (data.firm, data.model, data.year, data.power,
                  data.color, data.price, data.dealer_id))
            conn.commit()
            new_id = cur.lastrowid
            cur = conn.execute("SELECT * FROM cars WHERE id = ?", (new_id,))
            return Car(**dict(cur.fetchone()))
        finally:
            conn.close()

    def update(self, car_id: int, data: CarUpdate) -> Car | None:
        """UPDATE (полная замена). None, если строки нет."""
        conn = get_connection()
        try:
            cur = conn.execute("SELECT id FROM cars WHERE id = ?", (car_id,))
            if cur.fetchone() is None:
                return None
            conn.execute("""
                UPDATE cars
                SET firm = ?, model = ?, year = ?, power = ?,
                    color = ?, price = ?, dealer_id = ?
                WHERE id = ?
            """, (data.firm, data.model, data.year, data.power,
                  data.color, data.price, data.dealer_id, car_id))
            conn.commit()
            cur = conn.execute("SELECT * FROM cars WHERE id = ?", (car_id,))
            return Car(**dict(cur.fetchone()))
        finally:
            conn.close()

    def delete(self, car_id: int) -> bool:
        """DELETE. True, если строка была удалена."""
        conn = get_connection()
        try:
            cur = conn.execute("SELECT id FROM cars WHERE id = ?", (car_id,))
            if cur.fetchone() is None:
                return False
            conn.execute("DELETE FROM cars WHERE id = ?", (car_id,))
            conn.commit()
            return True
        finally:
            conn.close()


# ============================== DEALERS =============================

class DealerRepository:

    def get_all(self) -> list[Dealer]:
        conn = get_connection()
        try:
            cur = conn.execute("SELECT * FROM dealers ORDER BY id")
            return [Dealer(**dict(row)) for row in cur.fetchall()]
        finally:
            conn.close()

    def get_by_id(self, dealer_id: int) -> Dealer | None:
        conn = get_connection()
        try:
            cur = conn.execute("SELECT * FROM dealers WHERE id = ?", (dealer_id,))
            row = cur.fetchone()
            return Dealer(**dict(row)) if row else None
        finally:
            conn.close()

    def create(self, data: DealerCreate) -> Dealer:
        conn = get_connection()
        try:
            cur = conn.execute("""
                INSERT INTO dealers (name, city, address, area, rating)
                VALUES (?, ?, ?, ?, ?)
            """, (data.name, data.city, data.address, data.area, data.rating))
            conn.commit()
            new_id = cur.lastrowid
            cur = conn.execute("SELECT * FROM dealers WHERE id = ?", (new_id,))
            return Dealer(**dict(cur.fetchone()))
        finally:
            conn.close()

    def update(self, dealer_id: int, data: DealerUpdate) -> Dealer | None:
        conn = get_connection()
        try:
            cur = conn.execute("SELECT id FROM dealers WHERE id = ?", (dealer_id,))
            if cur.fetchone() is None:
                return None
            conn.execute("""
                UPDATE dealers
                SET name = ?, city = ?, address = ?, area = ?, rating = ?
                WHERE id = ?
            """, (data.name, data.city, data.address,
                  data.area, data.rating, dealer_id))
            conn.commit()
            cur = conn.execute("SELECT * FROM dealers WHERE id = ?", (dealer_id,))
            return Dealer(**dict(cur.fetchone()))
        finally:
            conn.close()

    def delete(self, dealer_id: int) -> bool:
        conn = get_connection()
        try:
            cur = conn.execute("SELECT id FROM dealers WHERE id = ?", (dealer_id,))
            if cur.fetchone() is None:
                return False
            conn.execute("DELETE FROM dealers WHERE id = ?", (dealer_id,))
            conn.commit()
            return True
        finally:
            conn.close()
