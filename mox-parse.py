#!/usr/bin/env python3

from typing import NamedTuple
from collections.abc import Sequence
from argparse import ArgumentParser
import re

from mtgcsv import CardExport, write_cards
from scryfall import CardIdentifier, SetCollectorNumber, NameSet, fetch_scryfall


class MoxfieldCard(NamedTuple):
    set_code: str
    name: str
    collector_number: str | None
    quantity: int


def to_identifier(card: MoxfieldCard) -> CardIdentifier:
    if card.collector_number is None:
        return NameSet(card.name, card.set_code)
    else:
        return SetCollectorNumber(card.set_code, card.collector_number)


def read_moxfield_cards(in_file: str) -> Sequence[MoxfieldCard]:
    moxfield_cards = list[MoxfieldCard]()

    with open(in_file, "r") as f:
        for line in f:
            match = re.search(
                r"(?P<quantity>\d+) (?P<name>.+?) \((?P<set>.+?)\) (?P<collector>.+)",
                line,
            )

            if match:
                set_code = match.group("set")
                name = match.group("name")

                collector_number = match.group("collector")
                quantity = int(match.group("quantity"))

                moxfield_cards.append(
                    MoxfieldCard(set_code, name, collector_number, quantity)
                )

                continue

            match = re.search(r"(?P<quantity>\d+) (?P<name>.+?) \((?P<set>.+?)\)", line)

            if match:
                set_code = match.group("set")
                name = match.group("name")
                quantity = int(match.group("quantity"))

                moxfield_cards.append(MoxfieldCard(set_code, name, None, quantity))

    return moxfield_cards


def get_card_exports(moxfield_cards: Sequence[MoxfieldCard]) -> Sequence[CardExport]:
    card_exports = list[CardExport]()

    card_identifiers = [to_identifier(card) for card in moxfield_cards]
    fetched_cards = fetch_scryfall(card_identifiers)

    quantity_map = {
        (mi.set_code, mi.name, mi.collector_number): mi.quantity
        for mi in moxfield_cards
    }

    for card in fetched_cards:
        card_name = card["name"]
        multiverse_ids = card["multiverse_ids"]

        if not multiverse_ids:
            print("cannot parse", card_name, "missing multiverse id")
            continue

        multiverse_id = multiverse_ids[0]
        set_code = card["set"].upper()
        collector_number = card["collector_number"]

        quantity = (
            quantity_map.get((set_code, card_name, collector_number))
            or quantity_map.get((set_code, card_name, None))
            or 0
        )

        card_exports.append(CardExport(card_name, multiverse_id, quantity))

    return card_exports


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("mox_file")
    parser.add_argument("-o", "--output", dest="output_file", default="output.csv")
    args = parser.parse_args()

    moxfield_cards = read_moxfield_cards(args.mox_file)
    card_exports = get_card_exports(moxfield_cards)

    write_cards(card_exports, args.output_file)
