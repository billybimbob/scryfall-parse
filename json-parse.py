#!/usr/bin/env python3

from argparse import ArgumentParser
from typing import Collection, NamedTuple, TypedDict
import csv
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


class ExportCardInfo(NamedTuple):
    name: str
    multiverse_id: str
    quantity: int


def to_export(card: CardInfo) -> ExportCardInfo:
    return ExportCardInfo(card['name'], card['identifiers']['multiverseId'], card['count'])


def parse_export_info(in_file: str) -> Collection[ExportCardInfo]:
    cards = list[ExportCardInfo]()

    with open(in_file, 'r') as f:
        info: DeckInfo = json.load(f)
        deck_data = info['data']
        cards.extend(to_export(c) for c in deck_data['commander'])
        cards.extend(to_export(c) for c in deck_data['mainBoard'])

    return cards


def write_export_info(cards: Collection[ExportCardInfo], out_file: str) -> None:
    with open(out_file, 'w', newline='') as f:
        csv_file = csv.writer(f, delimiter=',')
        csv_file.writerow(['Name', 'MultiverseID', 'Quantity'])
        csv_file.writerows(cards)


if __name__ == '__main__':
    parser = ArgumentParser()
    parser.add_argument('deck_json')
    parser.add_argument('--output', dest='output_file', default='output.csv')
    args = parser.parse_args()

    cards = parse_export_info(args.deck_json)
    write_export_info(cards, args.output_file)
