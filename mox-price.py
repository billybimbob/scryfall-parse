#!/usr/bin/env python3

from typing import Iterable, Mapping, NamedTuple, Sequence, TypedDict, Collection
from argparse import ArgumentParser

import csv
import requests


class MtgViewerInput(NamedTuple):
    name: str
    multiverse_id: int
    copies: int


class MtgViewerOutput(NamedTuple):
    name: str
    multiverse_id: int
    copies: int
    price: float


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


def read_mtg_viewer_input(in_file: str) -> Sequence[MtgViewerInput]:
    input_data = list[MtgViewerInput]()

    with open(in_file, 'r', newline='') as f:
        reader = csv.reader(f, delimiter=',', quotechar='"')

        for i, row in enumerate(reader):
            if i == 0:
                continue

            name, multiverse_id, copies = row
            input_data.append(MtgViewerInput(
                name, int(multiverse_id), int(copies)))

    return input_data


def fetch_scryfall_prices(multiverse_ids: Iterable[int]) -> Mapping[int, float]:
    card_ids_payload = {
        'identifiers': [{'multiverse_id': id} for id in multiverse_ids]
    }

    with requests.post('https://api.scryfall.com/cards/collection', json=card_ids_payload) as response:
        result: ScryfallResult = response.json()

        price_map = {int(card['multiverse_ids'][0]): float(
            card['prices']['usd']) for card in result['data']}

        return price_map


def get_mtg_viewer_output(input_data: Sequence[MtgViewerInput], price_threshold: float) -> Collection[MtgViewerOutput]:
    CHUNK_SIZE = 75

    output_info = list[MtgViewerOutput]()
    chunks = (input_data[i:i+CHUNK_SIZE]
              for i in range(0, len(input_data), CHUNK_SIZE))

    for chunk in chunks:
        price_map = fetch_scryfall_prices(data.multiverse_id for data in chunk)

        for input_value in chunk:
            price = price_map.get(input_value.multiverse_id, 0)

            if price <= price_threshold:
                output_info.append(MtgViewerOutput(input_value.name, input_value.multiverse_id,
                                                   input_value.copies, price))
            else:
                print(input_value.name, 'is higher than price threshold', price)

    return output_info


def write_mtg_viewer_output(out_file: str, cards: Collection[MtgViewerOutput]) -> None:

    with open(out_file, 'w', newline='') as f:
        csv_file = csv.writer(f, delimiter=',')
        csv_file.writerow(
            ['Name', 'MultiverseId', 'Copies', 'Price'])
        csv_file.writerows(cards)


if __name__ == '__main__':
    parser = ArgumentParser()

    parser.add_argument('input_file')

    parser.add_argument('-o', '--output',
                        dest='output_file', default='output.csv')

    parser.add_argument('-p', '--max-price',
                        dest='max_price', type=float, default=0.8)

    args = parser.parse_args()

    mox_info = read_mtg_viewer_input(args.input_file)
    export_info = get_mtg_viewer_output(mox_info, args.max_price)

    write_mtg_viewer_output(args.output_file, export_info)
