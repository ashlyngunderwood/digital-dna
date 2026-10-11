import json
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]

FIXTURE_PATH = (
    PROJECT_ROOT
    / "data"
    / "sample"
    / "musicbrainz_failure_test.json"
)



def test_failure_fixture_preserves_successful_requests():
    with open(FIXTURE_PATH, "r", encoding="utf-8") as file:
        results = json.load(file)

    assert len(results) == 3

    successful_results = [
        result
        for result in results
        if result["status"] == "success"
    ]

    failed_results = [
        result
        for result in results
        if result["status"] == "failed"
    ]

    assert len(successful_results) == 2
    assert len(failed_results) == 1

    failed_result = failed_results[0]

    assert failed_result["error_type"] == "RuntimeError"
    assert failed_result["error_message"] == "Simulated API failure"
    assert failed_result["api_response"] is None

    for result in successful_results:
        assert result["api_response"] is not None
        assert len(result["api_response"]["recordings"]) > 0

