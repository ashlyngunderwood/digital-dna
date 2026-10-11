from src.validation.recording_validation import get_match_priority

def test_artist_mismatch_receives_zero_priority():
    priority = get_match_priority(
        title="Espresso",
        requested_title="Espresso",
        artist="Wrong Artist",
        requested_artist="Sabrina Carpenter",
        disambiguation=""
    )

    assert priority == 0


def test_exact_title_and_artist_receives_highest_priority():
    priority = get_match_priority(
        title="Espresso",
        requested_title="Espresso",
        artist="Sabrina Carpenter",
        requested_artist="Sabrina Carpenter",
        disambiguation=""
    )

    assert priority == 3