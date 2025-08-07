from datetime import datetime
from pymongo.errors import PyMongoError
from log_writer import with_mongo_connection


def show_statistics() -> None:
    """
    Запрашивает у пользователя тип статистики и выводит результат:
    1 — последние 5 уникальных запросов;
    2 — топ-5 популярных запросов по количеству.
    """
    print("\nWhich statistics would you like to see?")
    print("1 — Last 5 unique requests")
    print("2 — Top 5 popular requests")

    choice = input("Enter number (1 or 2): ").strip()

    if choice == "1":
        results = get_recent_requests()
        if not results:
            print("❗ Unable to retrieve statistics.")
            return

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

    elif choice == "2":
        results = get_popular_requests()
        if not results:
            print("❗ Unable to retrieve statistics.")
            return

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

    else:
        print("Invalid input. Returning to menu.")


@with_mongo_connection
def get_recent_requests(collection) -> list[dict]:
    """
    Возвращает последние 5 уникальных запросов.

    :param collection: Коллекция MongoDB (передаётся декоратором).
    :return: Список уникальных запросов.
    """
    try:
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


@with_mongo_connection
def get_popular_requests(collection) -> list[dict]:
    """
    Возвращает 5 самых популярных запросов.

    :param collection: Коллекция MongoDB (передаётся декоратором).
    :return: Список популярных запросов с числом вызовов.
    """
    try:
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
