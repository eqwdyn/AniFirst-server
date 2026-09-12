from anime_parsers_ru import KodikParser


def getEmbedUrl(token: str, kodik_id: int):
    parser = KodikParser(token=token)

    embed_url = parser.get_embed_link(
        id=kodik_id,
        id_type="kodik",
        https=True
    )

    return embed_url
