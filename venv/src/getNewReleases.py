from anime_parsers_ru import ShikimoriParser
# from anime_parsers_ru import KodikList


def getNewReleases(limit=10):
    animes = ShikimoriParser().get_anime_list(
        page_limit=limit, status="ongoing", sort_by='rating')

    # query = KodikList(token=token).anime_status(
    #     "ongoing").order("desc").limit(limit)
    # data = query.execute(return_json=json)
    return animes
