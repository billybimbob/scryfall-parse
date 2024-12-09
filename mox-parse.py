#!/usr/bin/env python3

from typing import NamedTuple, TypedDict
from collections.abc import Iterable, Sequence
from argparse import ArgumentParser
from urllib.request import urlopen, Request
from mtgcsv import ExportCardInfo, write_card_info

import re
import json


class MoxCardInfo(NamedTuple):
    set_code: str
    name: str
    collector_number: str | None
    quantity: int


class ScryfallCard(TypedDict):
    name: str
    multiverse_ids: list[str]  # should just be size one
    collector_number: str
    set: str


class ScryfallResult(TypedDict):
    data: list[ScryfallCard]


def get_identifier(info: MoxCardInfo) -> dict[str, str]:
    return (
        {"name": info.name, "set": info.set_code}
        if info.collector_number is None
        else {
            "collector_number": info.collector_number,
            "set": info.set_code,
        }
    )


def read_mox_info(in_file: str) -> Sequence[MoxCardInfo]:
    mox_info = list[MoxCardInfo]()

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

                mox_info.append(MoxCardInfo(set_code, name, collector_number, quantity))

                continue

            match = re.search(r"(?P<quantity>\d+) (?P<name>.+?) \((?P<set>.+?)\)", line)

            if match:
                set_code = match.group("set")
                name = match.group("name")
                quantity = int(match.group("quantity"))

                mox_info.append(MoxCardInfo(set_code, name, None, quantity))

    return mox_info


def fetch_scryfall_data(mox_info: Iterable[MoxCardInfo]) -> ScryfallResult:
    SCRYFALL_URL = "https://api.scryfall.com/cards/collection"

    headers = {"Content-Type": "application/json"}

    card_ids_payload = {"identifiers": [get_identifier(mi) for mi in mox_info]}

    data = json.dumps(card_ids_payload).encode("utf-8")
    request = Request(SCRYFALL_URL, data, headers)

    with urlopen(request) as response:
        body = response.read()
        return json.loads(body)


def get_export_info(mox_info: Sequence[MoxCardInfo]) -> Sequence[ExportCardInfo]:
    CHUNK_SIZE = 75

    export_info = list[ExportCardInfo]()

    chunks = (mox_info[i : i + CHUNK_SIZE] for i in range(0, len(mox_info), CHUNK_SIZE))

    quantity_map = {
        (mi.set_code, mi.name, mi.collector_number): mi.quantity for mi in mox_info
    }

    for chunk in chunks:
        result = fetch_scryfall_data(chunk)

        for card in result["data"]:
            card_name = card["name"]
            multiverse_ids = card["multiverse_ids"]

            if not multiverse_ids:
                print("cannot parse", card_name, "missing multiverse id")
                continue

            multiverse_id = multiverse_ids[0]
            set_code = card["set"].upper()
            collector_number = card["collector_number"]

            quantity = quantity_map.get(
                (set_code, card_name, None)
            ) or quantity_map.get((set_code, card_name, collector_number), 0)

            export_info.append(ExportCardInfo(card_name, multiverse_id, quantity))

    return export_info


if __name__ == "__main__":
    parser = ArgumentParser()
    parser.add_argument("mox_file")
    parser.add_argument("-o", "--output", dest="output_file", default="output.csv")

    args = parser.parse_args()

    mox_info = read_mox_info(args.mox_file)
    export_info = get_export_info(mox_info)

    write_card_info(export_info, args.output_file)
