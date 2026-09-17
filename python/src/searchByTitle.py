import asyncio
from anime_parsers_ru import KodikParserAsync


KODIK_TOKEN = "56a768d08f43091901c44b54fe970049"
async def search_by_title(title: str, limit: int = 10) -> list[dict]:
    """
    Поиск аниме по названию через Kodik.
    Возвращает список словарей, соответствующих IAnimeSearch.
    """
    parser = KodikParserAsync(KODIK_TOKEN)

    try:
        results = await parser.search(title=title, limit=limit)

        anime_list = []
        for item in results:
            md = item.get("material_data", {})

            ratings = []
            for r in [md.get("shikimori_rating"), md.get("kinopoisk_rating"), md.get("imdb_rating")]:
                if r is not None and r > 0:
                    ratings.append(r)
            avg_rating = round(sum(ratings) / len(ratings), 1) if ratings else 0

            anime = {
                "kodik_id": item.get("id"),
                "shikimori_id": item.get("shikimori_id"),
                "title": item.get("title"),
                "rating": avg_rating,
                "status": md.get("anime_status", "unknown"),
                "studio": " & ".join(md.get("anime_studios", [])) if md.get("anime_studios") else "Unknown",
                "posterUrl": md.get("anime_poster_url") or md.get("poster_url") or "",
            }
            anime_list.append(anime)

        return anime_list

    finally:
        await parser.close_async_session()
