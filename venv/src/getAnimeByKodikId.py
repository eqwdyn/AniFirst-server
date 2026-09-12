from anime_parsers_ru import KodikSearch, ShikimoriParser
import json


def getAnimeByShikimoryId(id: int):
    animes = ShikimoriParser().get_anime_list()
    return animes


def getAnimeByKodikId(token: str, kodik_id: str):
    animes = KodikSearch(token).id(
        id=kodik_id).execute(return_json=True)

    return animes


token = "56a768d08f43091901c44b54fe970049"

animes = getAnimeByShikimoryId(123)
# data = getAnimeByKodikId(token=token, kodik_id="serial-76836")
print(animes)
