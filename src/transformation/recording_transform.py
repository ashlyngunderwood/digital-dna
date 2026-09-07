import pandas as pd

from src.validation.recording_validation import select_best_match

def recordings_to_dataframe(api_data):
    recordings = api_data.get("recordings", [])

    rows = []

    for recording in recordings:
        artist = (
            recording.get("artist-credit", [{}])[0]
            .get("artist", {})
            .get("name")
        )

        rows.append({
            "recording_id": recording.get("id"),
            "title": recording.get("title"),
            "artist": artist,
            "score": recording.get("score"),
            "first_release_date": recording.get("first-release-date"),
            "disambiguation": recording.get("disambiguation")
        })

    return pd.DataFrame(rows)

def process_recording_matches(api_data, requested_title):
    recordings_df = recordings_to_dataframe(api_data)

    if recordings_df.empty:
        return None

    best_match = select_best_match(
        recordings_df,
        requested_title
    )

    return best_match