from typing import NamedTuple
from collections.abc import Collection
import csv

class ExportCardInfo(NamedTuple):
    name: str
    multiverse_id: str
    quantity: int

def write_export_info(cards: Collection[ExportCardInfo], out_file: str) -> None:
    with open(out_file, 'w', newline='') as f:
        csv_file = csv.writer(f, delimiter=',')
        csv_file.writerow(['Name', 'MultiverseID', 'Quantity'])
        csv_file.writerows(cards)
