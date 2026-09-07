EXCLUDED_TERMS = [
    "live",
    "dj-mix",
    "lyric video",
    "commentary"
]


def normalize_disambiguation(text):
    return (
        (text or "")
        .lower()
        .replace("‐", "-")
    )


def get_rejection_reason(text):
    cleaned_text = normalize_disambiguation(text)

    for term in EXCLUDED_TERMS:
        if term in cleaned_text:
            return f"Excluded variant: {term}"

    return None


def is_preferred_version(text):
    return get_rejection_reason(text) is None

def get_match_priority(title, requested_title, disambiguation):
    cleaned_title = (title or "").lower().strip()
    cleaned_requested_title = requested_title.lower().strip()
    cleaned_disambiguation = normalize_disambiguation(disambiguation)

    # Reject known unwanted variants
    if get_rejection_reason(disambiguation) is not None:
        return 0

    # Exact title + no variant information = strongest candidate
    if (
        cleaned_title == cleaned_requested_title
        and cleaned_disambiguation == ""
    ):
        return 3

    # Exact title + acceptable alternate version
    if cleaned_title == cleaned_requested_title:
        return 2

    # Artist matched, but recording title is a different version
    return 1


def select_best_match(df, requested_title):
    scored_df = df.copy()

    scored_df["match_priority"] = scored_df.apply(
        lambda row: get_match_priority(
            row["title"],
            requested_title,
            row["disambiguation"]
        ),
        axis=1
    )

    scored_df = scored_df.sort_values(
        by="match_priority",
        ascending=False
    )

    return scored_df.iloc[0]