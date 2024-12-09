#!/usr/bin/env python3

from argparse import ArgumentParser
from typing import NamedTuple
from collections.abc import Sequence
import csv

from scryfall import MultiverseId, fetch_scryfall
from mtgcsv import PriceExport, write_prices


class MtgCard(NamedTuple):
    name: str
    multiverse_id: int
    copies: int


def read_mtg_cards(in_file: str) -> Sequence[MtgCard]:
    mtg_cards = list[MtgCard]()

    with open(in_file, "r", newline="") as f:
        reader = csv.reader(f, delimiter=",", quotechar='"')

        for i, row in enumerate(reader):
            if i == 0:
                continue

            name, multiverse_id, copies = row
            mtg_cards.append(MtgCard(name, int(multiverse_id), int(copies)))

    return mtg_cards


def get_price_exports(
    mtg_cards: Sequence[MtgCard], price_threshold: float
) -> Sequence[PriceExport]:
    prices = list[PriceExport]()

    multiverse_ids = [MultiverseId(card.multiverse_id) for card in mtg_cards]
    fetched_cards = fetch_scryfall(multiverse_ids)

    price_map = {
        int(card["multiverse_ids"][0]): float(card["prices"]["usd"])
        for card in fetched_cards
    }

    for card in mtg_cards:
        price = price_map.get(card.multiverse_id, 0)

        if price <= price_threshold:
            prices.append(
                PriceExport(card.name, card.multiverse_id, card.copies, price)
            )
        else:
            print(card.name, "is higher than price threshold", price)

    return prices


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("input_file")
    parser.add_argument("-o", "--output", dest="output_file", default="output.csv")
    parser.add_argument("-p", "--max-price", dest="max_price", type=float, default=0.8)
    args = parser.parse_args()

    mtg_cards = read_mtg_cards(args.input_file)
    prices = get_price_exports(mtg_cards, args.max_price)

    write_prices(prices, args.output_file)
