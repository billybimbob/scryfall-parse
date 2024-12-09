from typing import NamedTuple
from collections.abc import Sequence
import csv


class CardExport(NamedTuple):
    name: str
    multiverse_id: str
    quantity: int


class PriceExport(NamedTuple):
    name: str
    multiverse_id: int
    copies: int
    price: float


def write_cards(cards: Sequence[CardExport], out_file: str) -> None:
    with open(out_file, "w", newline="") as f:
        csv_file = csv.writer(f, delimiter=",")
        csv_file.writerow(["Name", "MultiverseID", "Quantity"])
        csv_file.writerows(cards)


def write_prices(prices: Sequence[PriceExport], out_file: str) -> None:
    with open(out_file, "w", newline="") as f:
        csv_file = csv.writer(f, delimiter=",")
        csv_file.writerow(["Name", "MultiverseID", "Quantity", "Price"])
        csv_file.writerows(prices)
