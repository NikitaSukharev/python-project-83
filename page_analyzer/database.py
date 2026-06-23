import psycopg2
from psycopg2.extras import RealDictCursor
from contextlib import contextmanager


@contextmanager
def get_db(app):
    """Контекстный менеджер для подключения к базе данных"""
    conn = psycopg2.connect(app.config["DATABASE_URL"])
    try:
        yield conn
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def check_url_existence(app, url_name):
    """Проверяет наличие URL с заданным именем в базе данных"""
    with get_db(app) as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute("SELECT id FROM urls WHERE name = %s", (url_name,))
            result = cur.fetchone()
    return result['id'] if result else None


def add_urls(app, url_name):
    """Добавляет новый URL в базу данных и возвращает его ID"""
    with get_db(app) as conn:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO urls (name, created_at) "
                "VALUES (%s, NOW()) RETURNING id",
                (url_name,)
            )
            url_id = cur.fetchone()[0]
        conn.commit()
    return url_id


def get_one_url(app, url_id):
    """Получает информацию о URL по его ID"""
    with get_db(app) as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute('SELECT * FROM urls WHERE id = %s;', (url_id,))
            row = cur.fetchone()
    return row


def get_checks_for_url(app, url_id):
    """Получает все проверки для указанного URL, от новых к старым"""
    with get_db(app) as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                "SELECT * FROM url_checks WHERE url_id = %s "
                "ORDER BY id DESC",
                (url_id,)
            )
            checks = cur.fetchall()
    return checks


def get_all_urls(app):
    """Получает список всех URL с датой и кодом последней проверки"""
    with get_db(app) as conn:
        with conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(
                """
                SELECT
                    urls.id,
                    urls.name,
                    urls.created_at,
                    last_check.last_check_date,
                    last_check.status_code
                FROM urls
                LEFT JOIN (
                    SELECT
                        url_id,
                        created_at AS last_check_date,
                        status_code,
                        ROW_NUMBER() OVER (
                            PARTITION BY url_id
                            ORDER BY created_at DESC
                        ) AS rn
                    FROM url_checks
                ) AS last_check
                ON urls.id = last_check.url_id AND last_check.rn = 1
                ORDER BY urls.id DESC
                """
            )
            urls = cur.fetchall()
    return urls


def create_check_entry(app, url_id, status_code,
                       h1=None, title=None, description=None):
    """Создаёт новую запись проверки в базе данных"""
    with get_db(app) as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO url_checks (
                    url_id, status_code, h1, title, description, created_at
                ) VALUES (%s, %s, %s, %s, %s, NOW())
                """,
                (url_id, status_code, h1, title, description)
            )
        conn.commit()
