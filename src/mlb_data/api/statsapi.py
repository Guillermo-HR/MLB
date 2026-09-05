import requests

BASE_URLS = {
    "1": "https://statsapi.mlb.com/api/v1/",
    "1.1": "https://statsapi.mlb.com/api/v1.1/",
}

def get_data(url_v, endpoint, params=None, timeout=None):
        if url_v not in BASE_URLS:
            raise ValueError(f"Unsupported StatsAPI version: {url_v}")

        url = f"{BASE_URLS[url_v]}{endpoint}"

        response = requests.get(
            url,
            params=params,
            timeout=timeout
        )

        response.raise_for_status()

        return response.json()