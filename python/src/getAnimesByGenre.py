from anime_parsers_ru import ShikimoriParserAsync

async def get_animes_by_genre(genres: list[str], start_page = 1, page_limit= 1):
    parser = ShikimoriParserAsync()
    
    try:
        results = await parser.get_anime_list(genres=genres, page_limit=page_limit, start_page=start_page, sort_by="popularity")
        anime_list = []
        for item in results:
            anime = {
                "shikimori_id": item.get("shikimori_id"),
                "title": item.get("title"),
                "originalTitle": item.get("original_title"),
                "studio": item.get("studio", "Unknown"),
                "posterUrl": item.get("poster", ""),
            }
            anime_list.append(anime)

        return anime_list

    finally:
        await parser.close_async_session()