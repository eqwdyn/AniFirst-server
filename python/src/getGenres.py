from anime_parsers_ru import ShikimoriParserAsync, KodikSearch


async def get_shikimori_genres():
    """
    Возвращает список доступных жанров Shikimori.

    Аргументы:
        lang: "ru" — русские названия, "en" — английские
    """
    parser = ShikimoriParserAsync()
    try:
        eng_genres_raw = parser.genres_list
        eng_genres = [i.split("-")[1] for i in eng_genres_raw]
        ru_genres = parser.genres_list_ru

        if len(eng_genres) != len(ru_genres):
            raise ValueError(
                "Списки жанров имеют разную длину — данные несогласованы")

        return dict(zip(eng_genres, ru_genres))
    finally:
        await parser.close_async_session()
