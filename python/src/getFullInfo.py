from anime_parsers_ru import KodikParserAsync, ShikimoriParserAsync


KODIK_TOKEN = "56a768d08f43091901c44b54fe970049"
async def get_full_info(shikimori_id: str):
    kodik_parser = KodikParserAsync(token=KODIK_TOKEN)
    shiki = ShikimoriParserAsync()


    try:
        kodik_results = await kodik_parser.search_by_id(
            id=shikimori_id,
            id_type="shikimori",
            limit=None,
        )

        url = await shiki.link_by_id(shikimori_id)
        shikimori_results = await shiki.additional_anime_info(url)

        related_items = []
        for item in shikimori_results["related"]:
            related_shikimori_id = shiki.id_by_link(item["url"])
            related_item = {
                "shikimori_id": related_shikimori_id,
                "posterUrl": item["picture"],
                "title": item["name"],
                "type": item["type"],
                "date": item["date"],
                "relation": item["relation"]
            }
            related_items.append(related_item)


        return {"kodik_results": kodik_results, "related": related_items}
    finally:
        await kodik_parser.close_async_session()
        await shiki.close_async_session()
