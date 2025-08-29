import psycopg2
from psycopg2 import sql
from contextlib import closing
from werkzeug.security import generate_password_hash

# Настройки для подключения к БД
DB_CONFIG = {
    'dbname': 'postgres',
    'user': 'postgres',
    'password': 'postgres',
    'host': 'localhost',
    'port': '5432',
}

def get_connection():
    """Возвращает соединение с базой данных PostgreSQL."""
    return psycopg2.connect(**DB_CONFIG)


def add_client_account(full_name, phone, password):
    """Добавляет новые регистрации в БД"""
    hashed_password = generate_password_hash(password)

    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("""
                INSERT INTO kurs_2.client_auth (full_name, phone, password)
                VALUES (%s, %s, %s)
            """, (full_name, phone, hashed_password))

def get_client_by_phone(phone):
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT id, full_name, password FROM kurs_2.client_auth WHERE phone = %s", (phone,))
            return cursor.fetchone()

def check_phone_exists(phone):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id FROM client_auth WHERE phone = %s", (phone,))
            return cur.fetchone() is not None

def update_password(phone, new_password):
    password_hash = generate_password_hash(new_password)
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("UPDATE client_auth SET password = %s WHERE phone = %s", (password_hash, phone))
        conn.commit()


def get_employees():
    """Получает список всех сотрудников (тренеров)."""
    with closing(get_connection()) as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM kurs_2.employees ORDER BY full_name;")
            return cursor.fetchall()

def add_employee(full_name, phone, specialization, passport, birthday):
    """Добавляет нового тренера."""
    with closing(get_connection()) as conn:
        with conn.cursor() as cursor:
            try:
                cursor.execute("""
                    INSERT INTO kurs_2.employees (full_name, phone, specialization, passport, birthday)
                    VALUES (%s, %s, %s, %s, %s);
                """, (full_name, phone, specialization, passport, birthday)
                )
                conn.commit()
            except psycopg2.IntegrityError as e:
                conn.rollback()
                raise e

def del_employee(full_name, phone, specialization, passport, birthday):
    """Удаляет данные о тренере."""
    with closing(get_connection()) as conn:
        with conn.cursor() as cursor:
            try:
                cursor.execute(
                    "DELETE FROM kurs_2.employees WHERE full_name = %s AND phone = %s AND specialization = %s AND passport = %sAND birthday = %s",
                    (full_name, phone, specialization, passport, birthday)
                )
                conn.commit()
            except psycopg2.IntegrityError as e:
                conn.rollback()
                raise e

# Функции для работы с таблицей clients (клиенты)

def get_clients():
    """Получает список всех клиентов."""
    with closing(get_connection()) as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM kurs_2.clients ORDER BY full_name;")
            return cursor.fetchall()

def client_exists(phone):
    """Проверяет, существует ли клиент с таким номером телефона."""
    with closing(get_connection()) as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT id FROM kurs_2.clients WHERE phone = %s", (phone,))
            result = cursor.fetchone()
            return result is not None

def add_client(full_name, phone):
    """Добавляет нового клиента."""
    with closing(get_connection()) as conn:
        with conn.cursor() as cursor:
            try:
                cursor.execute(
                    "INSERT INTO kurs_2.clients (full_name, phone) VALUES (%s, %s)",
                    (full_name, phone)
                )
                conn.commit()
            except psycopg2.IntegrityError as e:
                conn.rollback()
                raise e

def del_client(full_name, phone):
    """Удаляет данные о клиенте."""
    with closing(get_connection()) as conn:
        with conn.cursor() as cursor:
            try:
                cursor.execute(
                    "DELETE FROM kurs_2.clients WHERE full_name = %s AND phone = %s",
                    (full_name, phone)
                )
                conn.commit()
            except psycopg2.IntegrityError as e:
                conn.rollback()
                raise e

def change_client(full_name, phone):
    """Изменяет данные о клиенте."""
    with closing(get_connection()) as conn:
        with conn.cursor() as cursor:
            try:
                cursor.execute(
                    "DELETE FROM kurs_2.clients WHERE full_name = %s AND phone = %s",
                    (full_name, phone)
                )
                conn.commit()
            except psycopg2.IntegrityError as e:
                conn.rollback()
                raise e



# Функции для работы с таблицей price_list (прайс-лист)

def get_price_list():
    """Получает список всех цен."""
    with closing(get_connection()) as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM kurs_2.price_list ORDER BY id;")
            return cursor.fetchall()


def add_price_list(membership_type, price):
    """Добавляет новоый абонемент."""
    with closing(get_connection()) as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                "INSERT INTO kurs_2.price_list (membership_type, price) VALUES (%s, %s)",
                (membership_type, price))
            conn.commit()


def update_ticket_price(membership_type, new_price):
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute(
                "UPDATE kurs_2.price_list SET price = %s WHERE membership_type = %s;",
                (new_price, membership_type)
            )
            conn.commit()

def get_all_ticket_types():
    with get_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT membership_type FROM kurs_2.price_list ORDER BY id;")
            return [row[0] for row in cursor.fetchall()]

# Функции для работы с таблицей schedule (расписание)

def get_schedule():
    """Получает расписание всех занятий."""
    with closing(get_connection()) as conn:
        with conn.cursor() as cursor:
            cursor.execute("""
                            SELECT * FROM kurs_2.schedule
                            ORDER BY 
                                CASE day_of_week
                                    WHEN 'Пн' THEN 1
                                    WHEN 'Вт' THEN 2
                                    WHEN 'Ср' THEN 3
                                    WHEN 'Чт' THEN 4
                                    WHEN 'Пт' THEN 5
                                    WHEN 'Сб' THEN 6
                                    WHEN 'Вс' THEN 7
                                END,
                                start_time;  -- Дополнительно сортируем по времени начала занятия
                        """)
            return cursor.fetchall()

def add_schedule(day_of_week, start_time, duration, specialization, instructor_name, free_spots):
    """Добавляет новое расписание занятия."""
    with closing(get_connection()) as conn:
        with conn.cursor() as cursor:
            cursor.execute("""
                            INSERT INTO kurs_2.schedule (day_of_week, start_time, duration, specialization, instructor_name, free_spots)
                            VALUES (%s, %s, %s, %s, %s, %s);
                        """, (day_of_week, start_time, duration, specialization, instructor_name, free_spots))
            conn.commit()

def update_free_spots(schedule_id, new_free_spots):
    """Обновляет количество свободных мест на занятии по его ID."""
    with closing(get_connection()) as conn:
        with conn.cursor() as cursor:
            cursor.execute("""
                UPDATE kurs_2.schedule SET free_spots = %s WHERE id = %s;
            """, (new_free_spots, schedule_id))
            conn.commit()


def book_schedule_spot(schedule_id):
    """Уменьшить количество свободных мест на занятии"""
    with get_connection() as conn:
        with conn.cursor() as cursor:
            # Проверяем, есть ли свободные места
            cursor.execute("SELECT free_spots FROM kurs_2.schedule WHERE id = %s", (schedule_id,))
            result = cursor.fetchone()

            if result and result[0] > 0:
                cursor.execute("""
                    UPDATE kurs_2.schedule
                    SET free_spots = free_spots - 1
                    WHERE id = %s
                """, (schedule_id,))
                return True
            return False


def get_filtered_schedule(day=None):
    with get_connection() as conn:
        with conn.cursor() as cursor:
            if day:
                cursor.execute("""
                    SELECT * FROM kurs_2.schedule
                    WHERE day_of_week = %s
                    ORDER BY day_of_week, start_time
                """, (day,))
            else:
                cursor.execute("""
                    SELECT * FROM kurs_2.schedule
                    ORDER BY day_of_week, start_time
                """)
            return cursor.fetchall()



# Функции для работы с лк клиента

def get_client_attendance(client_id):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("""
                SELECT r.date_class, s.day_of_week, s.start_time, s.specialization, s.instructor_name, r.attended
                FROM kurs_2.registrations r
                JOIN kurs_2.schedule s ON r.schedule_id = s.id
                WHERE r.client_id = %s
                ORDER BY s.start_time DESC;
            """, (client_id,))
            return cur.fetchall()
