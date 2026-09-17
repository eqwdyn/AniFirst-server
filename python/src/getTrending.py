from anime_parsers_ru import ShikimoriParserAsync


async def getTrending(limit=1):
    parser = ShikimoriParserAsync()
    animes = await parser.get_anime_list(page_limit=limit, sort_by="rating")
    await parser.close_async_session()
    return animes
