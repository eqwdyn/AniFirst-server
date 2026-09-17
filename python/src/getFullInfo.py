from anime_parsers_ru import KodikParserAsync


KODIK_TOKEN = "56a768d08f43091901c44b54fe970049"
async def get_full_info(shikimori_id: str):
    kodik_parser = KodikParserAsync(token=KODIK_TOKEN)

    try:
        kodik_results = await kodik_parser.search_by_id(
            id=shikimori_id,
            id_type="shikimori",
            limit=None,
        )
        return kodik_results
    finally:
        await kodik_parser.close_async_session()
