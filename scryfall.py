from dataclasses import dataclass
from typing import TypedDict, Protocol
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


class CardIdentifier(Protocol):
    def to_dict(self) -> dict[str, str | int]: ...


@dataclass
class NameSet(CardIdentifier):
    name: str
    set_code: str

    def to_dict(self) -> dict[str, str | int]:
        return {"name": self.name, "set": self.set_code}


@dataclass
class SetCollectorNumber(CardIdentifier):
    set_code: str
    collector_number: str

    def to_dict(self) -> dict[str, str | int]:
        return {
            "collector_number": self.collector_number,
            "set": self.set_code,
        }


@dataclass
class MultiverseId(CardIdentifier):
    multiverse_id: int

    def to_dict(self) -> dict[str, str | int]:
        return {"multiverse_id": self.multiverse_id}


def fetch_scryfall(card_info: Sequence[CardIdentifier]) -> Sequence[ScryfallCard]:
    SCRYFALL_URL = "https://api.scryfall.com/cards/collection"
    CHUNK_SIZE = 75

    cards = list[ScryfallCard]()

    headers = {"Content-Type": "application/json"}
    chunks = (
        card_info[i : i + CHUNK_SIZE] for i in range(0, len(card_info), CHUNK_SIZE)
    )

    for chunk in chunks:
        card_ids_payload = {"identifiers": [ci.to_dict() for ci in chunk]}
        data = json.dumps(card_ids_payload).encode("utf-8")

        request = Request(SCRYFALL_URL, data, headers)

        with urlopen(request) as response:
            body = response.read()
            result: ScryfallResult = json.loads(body)
            cards.extend(result["data"])

    return cards
