import requests

from requests.exceptions import HTTPError, Timeout, ConnectionError


def fetch_coordinates(apikey, address):
    try:
        base_url = "https://geocode-maps.yandex.ru/1.x"
        response = requests.get(base_url, params={
            "geocode": address,
            "apikey": apikey,
            "format": "json",
        })
        response.raise_for_status()
        found_places = response.json()['response']['GeoObjectCollection']['featureMember']

        if not found_places:
            return {'lon': None, 'lat': None}

        most_relevant = found_places[0]
        lon, lat = most_relevant['GeoObject']['Point']['pos'].split(" ")
        return {'lon': lon, 'lat': lat}
    except (HTTPError, Timeout, ConnectionError):
        return {'lon': None, 'lat': None}
