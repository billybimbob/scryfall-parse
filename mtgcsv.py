from typing import NamedTuple
from collections.abc import Sequence
import csv


class ExportCardInfo(NamedTuple):
    name: str
    multiverse_id: str
    quantity: int


class ExportPriceInfo(NamedTuple):
    name: str
    multiverse_id: int
    copies: int
    price: float


def write_card_info(cards: Sequence[ExportCardInfo], out_file: str) -> None:
    with open(out_file, "w", newline="") as f:
        csv_file = csv.writer(f, delimiter=",")
        csv_file.writerow(["Name", "MultiverseID", "Quantity"])
        csv_file.writerows(cards)


def write_price_info(cards: Sequence[ExportPriceInfo], out_file: str) -> None:
    with open(out_file, "w", newline="") as f:
        csv_file = csv.writer(f, delimiter=",")
        csv_file.writerow(["Name", "MultiverseID", "Quantity", "Price"])
        csv_file.writerows(cards)
