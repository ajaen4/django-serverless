import pyproj
from typing import Generator, IO


class CoordTransformer:
    def __init__(self) -> None:
        self.lambert = pyproj.Proj(
            "+proj=lcc +lat_1=49 +lat_2=44 +lat_0=46.5 +lon_0=3 +x_0=700000 +y_0=6600000 +ellps=GRS80 +towgs84=0,0,0,0,0,0,0 +units=m +no_defs"
        )
        self.wgs84 = pyproj.Proj(
            "+proj=longlat +ellps=WGS84 +datum=WGS84 +no_defs"
        )

    def transform(self, x: int, y: int) -> tuple[float, float]:
        long, lat = pyproj.transform(self.lambert, self.wgs84, x, y)
        return lat, long


def process_init_file(path: str) -> list[dict]:
    init_data = list()
    with open(path, "r") as file:
        file.readline()
        transformer = CoordTransformer()
        for line in file:
            fields = line.strip().split(";")
            try:
                x = int(fields[1])
                y = int(fields[2])
            except ValueError:
                continue
            init_data.append(operator(fields, transformer.transform(x, y)))
    return init_data


def operator(fields: list, coordinates: tuple) -> dict:
    is_2g = fields[3] == "1"
    is_3g = fields[4] == "1"
    is_4g = fields[5] == "1"
    return {
        "operator_id": fields[0],
        "latitude": coordinates[0],
        "longitude": coordinates[1],
        "g2": is_2g,
        "g3": is_3g,
        "g4": is_4g,
    }


def skip_comments(file: IO) -> Generator:
    for line in file:
        if not line.strip().startswith("#"):
            yield line
