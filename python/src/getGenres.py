from anime_parsers_ru import ShikimoriParserAsync, KodikSearch


async def get_shikimori_genres(lang: str = "ru") -> list[str]:
    """
    Возвращает список доступных жанров Shikimori.

    Аргументы:
        lang: "ru" — русские названия, "en" — английские
    """
    parser = ShikimoriParserAsync()
    try:
        genres = parser.genres_list_ru if lang == "ru" else parser.genres_list
        return genres
    finally:
        await parser.close_async_session()


def get_kodik_genres() -> dict[str, list[str]]:
    """
    Возвращает доступные жанры Kodik для фильтрации.

    Kodik разделяет жанры на два типа:
      - genres — основные жанры (кинематографические)
      - anime_genres — аниме-жанры (по классификации Shikimori)

    Возвращает:
        {"genres": [...], "anime_genres": [...]}
    """
    def _extract(container) -> list[str]:
        return [
            getattr(container, attr)
            for attr in dir(container)
            if not attr.startswith("_")
        ]

    return {
        "genres": _extract(KodikSearch.Genres),
        "anime_genres": _extract(KodikSearch.AnimeGenres),
    }
