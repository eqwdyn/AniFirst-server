from anime_parsers_ru import ShikimoriParserAsync

token="56a768d08f43091901c44b54fe970049"

async def getNewReleases(limit=1):
    parser = ShikimoriParserAsync()
    animes = await parser.get_anime_list(page_limit=limit,status=["ongoing"], sort_by="aired_on ")
    await parser.close_async_session()
    return animes
