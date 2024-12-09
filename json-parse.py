#!/usr/bin/env python3

from argparse import ArgumentParser
from typing import TypedDict, Sequence
from mtgcsv import CardExport, write_cards

import json


class CardIdentifier(TypedDict):
    multiverseId: str


class CardInfo(TypedDict):
    name: str
    identifiers: CardIdentifier
    count: int


class CommanderDeckData(TypedDict):
    commander: list[CardInfo]
    mainBoard: list[CardInfo]


class DeckInfo(TypedDict):
    data: CommanderDeckData


def to_export(card: CardInfo) -> CardExport:
    return CardExport(card["name"], card["identifiers"]["multiverseId"], card["count"])


def parse_card_exports(in_file: str) -> Sequence[CardExport]:
    card_exports = list[CardExport]()

    with open(in_file, "r") as f:
        info: DeckInfo = json.load(f)
        deck_data = info["data"]
        card_exports.extend(to_export(c) for c in deck_data["commander"])
        card_exports.extend(to_export(c) for c in deck_data["mainBoard"])

    return card_exports


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("deck_json")
    parser.add_argument("--output", dest="output_file", default="output.csv")
    args = parser.parse_args()

    cards = parse_card_exports(args.deck_json)
    write_cards(cards, args.output_file)
