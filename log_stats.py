from datetime import datetime
from pymongo import MongoClient
from pymongo.errors import PyMongoError
from config import MONGODB_URI, MONGODB_DB, MONGODB_COLLECTION


def show_statistics() -> None:
    """
    Запрашивает у пользователя тип статистики и выводит результат.

    1 — последние 5 уникальных запросов;
    2 — топ-5 популярных запросов по количеству.
    """
    print("\nWhich statistics would you like to see?")
    print("1 — Last 5 unique requests")
    print("2 — Top 5 popular requests")

    choice = input("Enter number (1 or 2): ").strip()

    if choice == "1":
        try:
            results = get_recent_requests()
            print("\n📌 Last 5 unique requests:")
            for r in results:
                ts = datetime.fromisoformat(r['timestamp']).strftime("%Y-%m-%d %H:%M:%S")
                search_type = r.get("search_type", "unknown")
                params = r["_id"]

                if search_type == "keyword":
                    keyword = params.get("keyword", "?")
                    print(f"📅 Date: {ts} | 🔍 Type: {search_type:<12} | 🔑 Keyword: '{keyword}'")
                else:
                    genre = params.get("genre", "?")
                    y_from = params.get("year_from", "?")
                    y_to = params.get("year_to", "?")
                    print(f"📅 Date: {ts} | 🔍 Type: {search_type:<12} | 🎬 Genre: {genre} ({y_from}–{y_to})")

        except (KeyError, PyMongoError) as e:
            print(f"Error retrieving recent requests: {e}")

    elif choice == "2":
        try:
            results = get_popular_requests()
            print("\n⭐ Top 5 popular requests:")
            for r in results:
                search_type = r.get("search_type", "unknown")
                params = r["_id"]
                count = r.get("count", "?")

                if search_type == "keyword":
                    keyword = params.get("keyword", "?")
                    print(f"🔍 Type: {search_type:<12} | 🔑 Keyword: '{keyword}' → {count} requests")
                else:
                    genre = params.get("genre", "?")
                    y_from = params.get("year_from", "?")
                    y_to = params.get("year_to", "?")
                    print(f"🔍 Type: {search_type:<12} | 🎬 Genre: {genre} ({y_from}–{y_to}) → {count} requests")

        except (KeyError, PyMongoError) as e:
            print(f"Error retrieving popular requests: {e}")
    else:
        print("Invalid input. Returning to menu.")


def get_recent_requests() -> list[dict]:
    """
    Возвращает последние 5 уникальных поисковых запросов из MongoDB.

    Returns:
        list[dict]: Список уникальных записей по параметрам запроса.
    """
    try:
        with MongoClient(MONGODB_URI) as client:
            collection = client[MONGODB_DB][MONGODB_COLLECTION]

            pipeline = [
                {"$sort": {"timestamp": -1}},
                {"$group": {
                    "_id": "$params",
                    "timestamp": {"$first": "$timestamp"},
                    "search_type": {"$first": "$search_type"}
                }},
                {"$sort": {"timestamp": -1}},
                {"$limit": 5}
            ]
            return list(collection.aggregate(pipeline))

    except PyMongoError as e:
        print(f"Aggregation error (recent): {e}")
        return []


def get_popular_requests() -> list[dict]:
    """
    Возвращает топ-5 наиболее популярных запросов из MongoDB по частоте использования.

    Returns:
        list[dict]: Список запросов и их количества.
    """
    try:
        with MongoClient(MONGODB_URI) as client:
            collection = client[MONGODB_DB][MONGODB_COLLECTION]

            pipeline = [
                {"$group": {
                    "_id": "$params",
                    "count": {"$sum": 1},
                    "search_type": {"$first": "$search_type"}
                }},
                {"$sort": {"count": -1}},
                {"$limit": 5}
            ]
            return list(collection.aggregate(pipeline))

    except PyMongoError as e:
        print(f"Aggregation error (popular): {e}")
        return []
