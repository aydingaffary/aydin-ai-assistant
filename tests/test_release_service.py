from datetime import date

from services.release_service import ReleaseService


class FakeResponse:
    def raise_for_status(self):
        pass

    def json(self):
        return {
            "results": [
                {
                    "id": 123,
                    "title": "Test Movie",
                    "release_date": "2026-10-07",
                }
            ]
        }


def test_get_releases(monkeypatch):
    def fake_get(*args, **kwargs):
        return FakeResponse()

    monkeypatch.setattr(
        "services.release_service.requests.get",
        fake_get,
    )

    service = ReleaseService()

    releases = service.get_releases(
        date(2026, 10, 6),
        7,
    )

    assert len(releases) == 1
    assert releases[0]["title"] == "Test Movie"
    assert releases[0]["type"] == "movie"