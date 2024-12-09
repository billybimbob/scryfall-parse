from typing import TypedDict, NamedTuple
from collections.abc import Sequence
from urllib.request import urlopen, Request
import json


class ScryfallPrice(TypedDict):
    usd: str


class ScryfallCard(TypedDict):
    name: str
    multiverse_ids: list[str]  # should just be size one
    collector_number: str
    set: str
    prices: ScryfallPrice


class ScryfallResult(TypedDict):
    data: list[ScryfallCard]


class CardInfo(NamedTuple):
    name: str
    set_code: str
    collector_number: str | None
    multiverse_id: str | None


def get_identifier(info: CardInfo) -> dict[str, str]:
    if info.multiverse_id is not None:
        return {"multiverse_id": info.multiverse_id}

    if info.collector_number is not None:
        return {
            "collector_number": info.collector_number,
            "set": info.set_code,
        }

    return {"name": info.name, "set": info.set_code}


def fetch_scryfall_data(card_info: Sequence[CardInfo]) -> Sequence[ScryfallCard]:
    SCRYFALL_URL = "https://api.scryfall.com/cards/collection"
    CHUNK_SIZE = 75

    cards = list[ScryfallCard]()

    headers = {"Content-Type": "application/json"}
    chunks = (
        card_info[i : i + CHUNK_SIZE] for i in range(0, len(card_info), CHUNK_SIZE)
    )

    for chunk in chunks:
        card_ids_payload = {"identifiers": [get_identifier(ci) for ci in chunk]}
        data = json.dumps(card_ids_payload).encode("utf-8")

        request = Request(SCRYFALL_URL, data, headers)

        with urlopen(request) as response:
            body = response.read()
            result: ScryfallResult = json.loads(body)
            cards.extend(result["data"])

    return cards
