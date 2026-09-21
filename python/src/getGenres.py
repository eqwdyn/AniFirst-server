from anime_parsers_ru import ShikimoriParserAsync, KodikSearch


async def get_shikimori_genres(lang: str = "ru"):
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