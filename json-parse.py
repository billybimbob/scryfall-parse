#!/usr/bin/env python3

from argparse import ArgumentParser
from typing import TypedDict, Sequence
from mtgcsv import ExportCardInfo, write_card_info

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


def to_export(card: CardInfo) -> ExportCardInfo:
    return ExportCardInfo(
        card["name"], card["identifiers"]["multiverseId"], card["count"]
    )


def parse_export_info(in_file: str) -> Sequence[ExportCardInfo]:
    cards = list[ExportCardInfo]()

    with open(in_file, "r") as f:
        info: DeckInfo = json.load(f)
        deck_data = info["data"]
        cards.extend(to_export(c) for c in deck_data["commander"])
        cards.extend(to_export(c) for c in deck_data["mainBoard"])

    return cards


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("deck_json")
    parser.add_argument("--output", dest="output_file", default="output.csv")
    args = parser.parse_args()

    cards = parse_export_info(args.deck_json)
    write_card_info(cards, args.output_file)
