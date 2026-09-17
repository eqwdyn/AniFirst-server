import asyncio
from anime_parsers_ru import KodikParserAsync


KODIK_TOKEN = "56a768d08f43091901c44b54fe970049"


async def get_hero_anime() -> dict | None:
    """
    Находит лучшее аниме для hero-блока сайта.
    Берёт онгоинги из Kodik, сортирует по среднему рейтингу
    и возвращает самый высокооценённый с постером.
    """
    parser = KodikParserAsync(KODIK_TOKEN)

    try:
        results = await parser.get_list(
            limit_per_page=50,
            pages_to_parse=2,
            include_material_data=True,
            anime_status="ongoing",
            only_anime=True,
        )

        # get_list возвращает кортеж — берём первый элемент
        if isinstance(results, tuple):
            results = results[0]

        if not results:
            return None

        # print(results)

        def get_avg_rating(item: dict) -> float:
            md = item.get("material_data", {}) or {}
            ratings = []
            for r in [md.get("shikimori_rating"), md.get("kinopoisk_rating"), md.get("imdb_rating")]:
                if r is not None and r > 0:
                    ratings.append(r)
            return sum(ratings) / len(ratings) if ratings else 0

        # Сортируем по рейтингу — лучшие наверху
        results.sort(key=get_avg_rating, reverse=True)

        for item in results:
            md = item.get("material_data", {}) or {}
            poster = md.get("anime_poster_url") or md.get("poster_url")
            shikimori_id = item.get("shikimori_id")

            # Пропускаем без постера или без shikimori_id
            if not poster or not shikimori_id:
                continue

            avg = get_avg_rating(item)
            if avg == 0:
                continue

            md = item.get("material_data")

            return item
            # return {
            #     "title": md.get("title"),
            #     "description": md.get("description"),
            #     "tags": item.get("anime_genres"),
            #     "posterUrl": md.get("anime_poster_url"),
            #     "shikimori_id": item.get("shikimori_id"),
            # }
            

        return None
    
    finally:
        await parser.close_async_session()
