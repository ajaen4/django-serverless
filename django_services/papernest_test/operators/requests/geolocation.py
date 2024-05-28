import requests


def get_coordinates(query: str, limit: int = 1) -> list[float]:
    payload: dict[str, str] = {"q": query, "limit": str(limit)}
    r = requests.get("https://api-adresse.data.gouv.fr/search", params=payload)
    return r.json()["features"][0]["geometry"]["coordinates"]
