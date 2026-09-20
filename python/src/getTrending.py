from anime_parsers_ru import ShikimoriParserAsync, KodikParserAsync

async def getTrending(limit=1, page=1):
    parser = ShikimoriParserAsync()
    animes = await parser.get_anime_list(page_limit=limit, start_page=page, sort_by="rating")
    await parser.close_async_session()
    return animes


KODIK_TOKEN = "56a768d08f43091901c44b54fe970049"
async def get_trending_kodik(limit=20):
    parser = KodikParserAsync(token=KODIK_TOKEN)
    animes = await parser.get_list(limit_per_page=limit * 3, only_anime=True, include_material_data=True, )
    await parser.close_async_session()
    return animes[0]
   
