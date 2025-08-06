from mysql_connector import search_by_keyword, search_by_genre_and_years, get_all_genres, get_min_max_years
from log_writer import safe_log
from log_stats import show_statistics
from formatter import print_movies


def main() -> None:
    """Главная функция, обеспечивающая пользовательский интерфейс для поиска фильмов и просмотра статистики."""
    while True:
        print("\n1 - Search by keyword")
        print("2 - Search by genre and years")
        print("3 - Show statistic")
        print("0 - Exit")
        choice = input("Choose option: ")

        if choice == '1':
            while True:
                keyword = input("Enter keyword: ").strip()
                if not keyword:
                    print("❗ Keyword cannot be empty. Please enter a keyword for search.")
                    continue
                if keyword.isdigit():
                    print("ℹ️ Note: You've entered only numbers. Searching for movies with numbers in the title.")
                break

            offset = 0
            while True:
                movies = search_by_keyword(keyword, offset)
                if (movies is None or movies == []) and offset == 0:
                    retry = input("Failed to load results. Try again? (yes/no): ").strip().lower()
                    if retry == 'yes':
                        continue
                    else:
                        break

                if not movies:
                    print("No more results found.")
                    break

                safe_log("keyword", {"keyword": keyword}, len(movies))
                print_movies(movies)

                next_page = input("\nShow next 10 movies? (1 - yes, 2 - back to menu): ")
                if next_page == '1':
                    offset += 10
                else:
                    break

        elif choice == '2':
            while True:
                genres_data = get_all_genres()
                min_year, max_year = get_min_max_years()

                if not genres_data or min_year is None or max_year is None:
                    retry = input("Failed to load genres or years. Try again? (yes/no): ").strip().lower()
                    if retry == 'yes':
                        continue
                    else:
                        break

                print("\nAvailable genres:")
                for genre in genres_data:
                    print(f"{genre['category_id']}. {genre['name']}")
                print(f"\nAvailable year range: {min_year} - {max_year}")
                break

            # Ввод жанра по номеру
            while True:
                try:
                    genre_id = int(input("Enter genre number: "))
                    selected_genre = next((g['name'] for g in genres_data if g['category_id'] == genre_id), None)
                    if not selected_genre:
                        print("❗ Invalid genre number. Please select a number from the list.")
                        continue
                    break
                except ValueError:
                    print("❗ Genre must be a number.")

            # Выбор режима: один год или диапазон
            print("\n1 - By single year")
            print("2 - By a range (from and/or to)")

            while True:
                year_mode = input("Choose option (1 or 2): ").strip()
                if year_mode not in ['1', '2']:
                    print("❗ Please enter 1 or 2.")
                    continue

                if year_mode == '1':
                    while True:
                        try:
                            single_year = int(input("Enter year: "))
                            if not (min_year <= single_year <= max_year):
                                print(f"❗ Year must be between {min_year} and {max_year}.")
                                continue
                            year_from = year_to = single_year
                            break
                        except ValueError:
                            print("❗ Please enter a valid number for the year.")
                    break

                elif year_mode == '2':
                    while True:
                        try:
                            raw_from = input(f"From year (press Enter to use {min_year}): ").strip()
                            year_from = min_year if raw_from == '' else int(raw_from)
                            if not (min_year <= year_from <= max_year):
                                print(f"❗ Year must be between {min_year} and {max_year}. Please try again.")
                                continue

                            raw_to = input(f"To year   (press Enter to use {max_year}): ").strip()
                            year_to = max_year if raw_to == '' else int(raw_to)
                            if not (min_year <= year_to <= max_year):
                                print(f"❗ Year must be between {min_year} and {max_year}. Please try again.")
                                continue

                            if year_from > year_to:
                                print("❗ 'From year' cannot be after 'To year'. Please enter valid range.")
                                continue

                            break
                        except ValueError:
                            print("❗ Please enter a valid number for years.")
                    break

            offset = 0
            while True:
                movies = search_by_genre_and_years(selected_genre, year_from, year_to, offset)
                if (movies is None or movies == []) and offset == 0:
                    retry = input("Failed to load results. Try again? (yes/no): ").strip().lower()
                    if retry == 'yes':
                        continue
                    else:
                        break

                if not movies:
                    print("No more results found.")
                    break

                safe_log("genre&years", {
                    "genre": selected_genre,
                    "year_from": year_from,
                    "year_to": year_to
                }, len(movies))

                print_movies(movies)

                next_page = input("\nShow next 10 movies? (1 - yes, 2 - back to menu): ")
                if next_page == '1':
                    offset += 10
                else:
                    break

        elif choice == "3":
            try:
                show_statistics()
            except Exception as e:
                print(f"Failed to load statistics: {e}")

        elif choice == '0':
            break
        else:
            print("Invalid option. Please enter 1, 2, 3 or 0.")


if __name__ == "__main__":
    main()
