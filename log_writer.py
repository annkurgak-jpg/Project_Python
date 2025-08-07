from datetime import datetime
from pymongo import MongoClient
from pymongo.errors import PyMongoError
from typing import Callable, Any
from config import MONGODB_URI, MONGODB_DB, MONGODB_COLLECTION


def with_mongo_connection(func: Callable[..., Any]) -> Callable[..., Any]:
    """
    Декоратор, подключающийся к MongoDB и передающий коллекцию в функцию.

    Если подключение к MongoDB не удалось, выбрасывает RuntimeError и
    прерывает выполнение функции.

    :param func: Функция, ожидающая первым аргументом MongoDB-коллекцию.
    :return: Результат выполнения обёрнутой функции.
    :raises RuntimeError: При ошибке подключения к MongoDB.
    """
    def wrapper(*args, **kwargs) -> Any:
        try:
            with MongoClient(MONGODB_URI) as client:
                db = client[MONGODB_DB]
                collection = db[MONGODB_COLLECTION]
                return func(collection, *args, **kwargs)
        except PyMongoError as e:
            raise RuntimeError(f"MongoDB error in {func.__name__}: {e}")
    return wrapper


@with_mongo_connection
def log_search(collection, search_type: str, params: dict, results_count: int) -> bool:
    """
    Сохраняет лог поискового запроса в MongoDB.

    :param collection: Коллекция MongoDB (передаётся декоратором).
    :param search_type: Тип поиска ('keyword' или 'genre&years').
    :param params: Параметры поиска.
    :param results_count: Кол-во найденных результатов.
    :return: True при успехе, иначе False.
    """
    try:
        collection.insert_one({
            "timestamp": datetime.now().isoformat(),
            "search_type": search_type,
            "params": params,
            "results_count": results_count
        })
        return True
    except PyMongoError as e:
        print(f"MongoDB logging error: {e}")
        return False
