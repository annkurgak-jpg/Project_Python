from datetime import datetime
from pymongo import MongoClient
from pymongo.errors import PyMongoError
from config import MONGODB_URI, MONGODB_DB, MONGODB_COLLECTION


def safe_log(search_type: str, params: dict, results_count: int) -> bool:
    """
    Безопасно сохраняет информацию о поисковом запросе в MongoDB.

    Args:
        search_type (str): Тип поиска ('keyword' или 'genre_years').
        params (dict): Параметры запроса (например, ключевое слово или жанр и годы).
        results_count (int): Количество найденных фильмов.

    Returns:
        bool: True — если лог успешно записан, иначе False.
    """
    try:
        with MongoClient(MONGODB_URI) as client:
            db = client[MONGODB_DB]
            collection = db[MONGODB_COLLECTION]

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
