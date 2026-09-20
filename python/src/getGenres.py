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


# Пример использования
async def main():
    # Shikimori
    shiki_ru = await get_shikimori_genres("ru")
    shiki_en = await get_shikimori_genres("en")
    print("Shikimori (RU):", shiki_ru[:5], "...")
    print("Shikimori (EN):", shiki_en[:5], "...")

    # Kodik (синхронно — жанры хранятся в контейнерах, без запросов к API)
    kodik = get_kodik_genres()
    print("Kodik genres:", kodik["genres"])
    print("Kodik anime_genres:", kodik["anime_genres"])


if __name__ == "__main__":
    asyncio.run(main())
