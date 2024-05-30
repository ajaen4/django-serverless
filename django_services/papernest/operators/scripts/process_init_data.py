from utils import process_init_file
import csv


def process_init_data() -> None:
    init_data = process_init_file("data/operators_cvg.csv")
    with open("data/operators_cvg_processed.csv", "w", newline="") as f:
        writer = csv.DictWriter(f, init_data[0].keys())
        writer.writeheader()
        for row in init_data:
            writer.writerow(row)


if __name__ == "__main__":
    process_init_data()
