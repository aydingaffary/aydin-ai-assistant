from datetime import date

from services.imdb_service import IMDbService


def test_get_releases():
    service = IMDbService()

    releases = service.get_releases(
        start_date=date(2026, 10, 6),
        days=7,
    )

    assert isinstance(releases, list)

    for release in releases:
        assert "title" in release
        assert "url" in release
        assert "release_date" in release
        assert "type" in release

        assert release["type"] in {"movie", "tv"}
        assert date(2026, 10, 6) <= release["release_date"] <= date(2026, 10, 12)
