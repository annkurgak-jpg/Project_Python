import pymysql
from pymysql.connections import Connection
from pymysql.cursors import Cursor
from typing import Optional, List, Dict, Callable, Any, Tuple
from config import MYSQL_CONFIG, DEFAULT_LIMIT


def connect_mysql() -> Optional[Connection]:
    """
    Устанавливает соединение с базой данных MySQL, используя параметры из конфигурации.

    :return: Объект соединения или None в случае ошибки подключения.
    """
    try:
        return pymysql.connect(
            host=MYSQL_CONFIG['host'],
            user=MYSQL_CONFIG['user'],
            password=MYSQL_CONFIG['password'],
            database=MYSQL_CONFIG['database'],
            cursorclass=pymysql.cursors.DictCursor
        )
    except pymysql.MySQLError as e:
        print(f"Connection error: {e}")
        return None


def with_mysql_connection(func: Callable[..., Any]) -> Callable[..., Any]:
    """
    Декоратор для функций, работающих с MySQL.
    Управляет подключением к базе данных и созданием курсора.

    :param func: Целевая функция, получающая курсор как первый аргумент.
    :return: Обёрнутая функция с автоматическим управлением соединением.
    """
    def wrapper(*args, **kwargs) -> Any:
        connection = connect_mysql()
        if not connection:
            return []

        try:
            with connection:
                with connection.cursor() as cursor:
                    return func(cursor, *args, **kwargs)
        except pymysql.MySQLError as e:
            print(f"MySQL error in {func.__name__}: {e}")
            return []

    return wrapper


@with_mysql_connection
def search_by_keyword(cursor: Cursor, keyword: str, offset: int = 0, limit: int = DEFAULT_LIMIT) -> List[Dict]:
    """
    Выполняет поиск фильмов по ключевому слову в названии.

    :param cursor: Курсор базы данных (автоматически передаётся декоратором).
    :param keyword: Ключевое слово для поиска в названии фильма.
    :param offset: Смещение для пагинации.
    :param limit: Количество фильмов для вывода (в config).
    :return: Список фильмов, удовлетворяющих критерию.
    """
    cursor.execute("""
        SELECT f.title, f.release_year, f.length, f.description,
               c.name AS genre,
               GROUP_CONCAT(CONCAT(a.first_name, ' ', a.last_name) SEPARATOR ', ') AS actors
        FROM film f
        LEFT JOIN film_category fc ON f.film_id = fc.film_id
        LEFT JOIN category c ON fc.category_id = c.category_id
        LEFT JOIN film_actor fa ON f.film_id = fa.film_id
        LEFT JOIN actor a ON fa.actor_id = a.actor_id
        WHERE f.title LIKE %s
        GROUP BY f.film_id
        LIMIT %s OFFSET %s
    """, (f'%{keyword}%', limit, offset))
    return cursor.fetchall()


@with_mysql_connection
def search_by_genre_and_years(
    cursor: Cursor,
    genre: str,
    year_from: int,
    year_to: int,
    offset: int = 0,
    limit: int = DEFAULT_LIMIT
) -> List[Dict]:
    """
    Ищет фильмы по жанру и диапазону лет.

    :param cursor: Курсор базы данных.
    :param genre: Название жанра.
    :param year_from: Начальный год диапазона.
    :param year_to: Конечный год диапазона.
    :param offset: Смещение (для постраничного вывода).
    :param limit: Лимит количества фильмов на страницу(в config).
    :return: Список фильмов по жанру и диапазону лет.
    """
    cursor.execute("""
        SELECT f.title, f.release_year, f.length, f.description,
               c.name AS genre,
               GROUP_CONCAT(CONCAT(a.first_name, ' ', a.last_name) SEPARATOR ', ') AS actors
        FROM film f
        JOIN film_category fc ON f.film_id = fc.film_id
        JOIN category c ON fc.category_id = c.category_id
        LEFT JOIN film_actor fa ON f.film_id = fa.film_id
        LEFT JOIN actor a ON fa.actor_id = a.actor_id
        WHERE c.name = %s AND f.release_year BETWEEN %s AND %s
        GROUP BY f.film_id
        LIMIT %s OFFSET %s
    """, (genre, year_from, year_to, limit, offset))
    return cursor.fetchall()


@with_mysql_connection
def get_all_genres(cursor: Cursor) -> List[Dict[str, Any]]:
    """
    Возвращает список всех жанров с номерами(ID).

    :param cursor: Курсор базы данных.
    :return: Список словарей с полями category_id и name.
    """
    cursor.execute("SELECT category_id, name FROM category ORDER BY name")
    return cursor.fetchall()


@with_mysql_connection
def get_min_max_years(cursor: Cursor) -> Tuple[Optional[int], Optional[int]]:
    """
    Определяет минимальный и максимальный год выпуска фильмов.

    :param cursor: Курсор базы данных.
    :return: Кортеж из минимального и максимального года (или None в случае ошибки).
    """
    cursor.execute("SELECT MIN(release_year) as min_year, MAX(release_year) as max_year FROM film")
    years = cursor.fetchone()
    return years['min_year'], years['max_year']
