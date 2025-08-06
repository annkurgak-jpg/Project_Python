from typing import List, Dict, Any

def print_movies(movies: List[Dict[str, Any]]) -> None:
    """
    Форматированный вывод списка фильмов.

    Каждый фильм выводится с заглавным названием и подробной информацией:
    - Жанр
    - Год выпуска
    - Продолжительность
    - Актёры
    - Описание

    Если список пуст, выводится сообщение "No movies found."

    :param movies: Список словарей, каждый из которых содержит информацию о фильме.
    :return: None
    """
    if not movies:
        print("No movies found.")
        return

    for movie in movies:
        try:
            title = movie.get('title', 'UNKNOWN TITLE').upper()
            genre = movie.get('genre', 'Unknown Genre')
            year = movie.get('release_year', 'Unknown Year')
            duration = movie.get('length', 'Unknown Duration')
            actors = movie.get('actors', 'No actors listed').title()
            description = movie.get('description', 'No description provided')

            print(f"\n🎬 {title}")
            print(f"📚 Genre: {genre}")
            print(f"📅 Release year: {year}")
            print(f"⏱️ Duration: {duration} min")
            print(f"👥 Actors: {actors}")
            print(f"📝 Description: {description[:300]}{'...' if len(description) > 300 else ''}")

        except Exception as e:
            print(f"Error displaying movie: {e}")