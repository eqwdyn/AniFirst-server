from anime_parsers_ru import ShikimoriParser


def getAnimesByRating(rating: int = 8, limit: int = 10):
    # query = KodikList(token=token).shikimori_rating(rating).limit(limit * 3)
    # data = query.execute()

    # seen = set()
    # unique = []

    # for item in data.results:
    #     key = item.shikimori_id if item.shikimori_id else item.title

    #     if key not in seen:
    #         seen.add(key)
    #         unique.append(item)

    #     if len(unique) >= limit:
    #         break

    # return unique
    animes = ShikimoriParser().get_anime_list(
        page_limit=limit, sort_by="rating", rating_from=rating)
    return animes
