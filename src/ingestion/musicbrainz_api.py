import time
import requests

BASE_URL = "https://musicbrainz.org/ws/2/recording/"

HEADERS = {
	"User-Agent": "DigitalDNA/1.0 (personal data analytics project)"
}


def get_with_retry(url, params, headers, retries=3, wait_seconds=3):
    for attempt in range(retries):
        try:
            response = requests.get(
                url,
                params=params,
                headers=headers,
                timeout=15
            )

            if response.status_code == 200:
                return response

            print(
                f"Attempt {attempt + 1} failed "
                f"with status code {response.status_code}"
            )

        except requests.exceptions.RequestException as error:
            print(
                f"Attempt {attempt + 1} failed "
                f"with error: {error}"
            )

        time.sleep(wait_seconds)

    raise RuntimeError("MusicBrainz request failed after all retry attempts.")

def search_recording(title, artist, limit=20):
    params = {
        "query": f'recording:"{title}" AND artist:"{artist}"',
        "fmt": "json",
        "limit": limit
    }

    response = get_with_retry(
        BASE_URL,
        params,
        HEADERS
    )

    response.raise_for_status()

    return response.json()