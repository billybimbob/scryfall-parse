from typing import TypedDict, NamedTuple
from collections.abc import Iterable
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
    multiverse_id: str
    set_code: str
    name: str
    collector_number: str | None
    quantity: int


def get_identifier(info: CardInfo) -> dict[str, str]:
    if info.multiverse_id is not None:
        return {"multiverse_id": info.multiverse_id}

    if info.collector_number is not None:
        return {
            "collector_number": info.collector_number,
            "set": info.set_code,
        }

    return {"name": info.name, "set": info.set_code}


def fetch_scryfall_data(mox_info: Iterable[CardInfo]) -> ScryfallResult:
    SCRYFALL_URL = "https://api.scryfall.com/cards/collection"

    headers = {"Content-Type": "application/json"}

    card_ids_payload = {"identifiers": [get_identifier(mi) for mi in mox_info]}

    data = json.dumps(card_ids_payload).encode("utf-8")
    request = Request(SCRYFALL_URL, data, headers)

    with urlopen(request) as response:
        body = response.read()
        return json.loads(body)
