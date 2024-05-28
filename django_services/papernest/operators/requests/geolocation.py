from typing import Tuple
import requests


def get_coordinates(query: str, limit: int = 1) -> Tuple:
    payload: dict[str, str] = {"q": query, "limit": str(limit)}
    r = requests.get("https://api-adresse.data.gouv.fr/search", params=payload)
    coordinates = r.json()["features"][0]["geometry"]["coordinates"]
    # lat, lng
    return coordinates[1], coordinates[0]
