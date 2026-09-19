from anime_parsers_ru import ShikimoriParserAsync, KodikParserAsync

token="56a768d08f43091901c44b54fe970049"

async def getNewReleases(limit=1):
    parser = ShikimoriParserAsync()
    animes = await parser.get_anime_list(page_limit=limit,status=["ongoing"], sort_by="aired_on ")
    await parser.close_async_session()
    return animes


KODIK_TOKEN = "56a768d08f43091901c44b54fe970049"
async def get_new_releases_kodik(limit=20):
    parser = KodikParserAsync(token=KODIK_TOKEN)
    animes = await parser.get_list(limit_per_page=limit * 3, only_anime=True, include_material_data=True, anime_status="ongoing" )
    await parser.close_async_session()
    return animes[0]
