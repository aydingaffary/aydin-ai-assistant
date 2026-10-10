
from services.release_service import ReleaseService


class FakeResponse:
    def raise_for_status(self):
        pass

    def json(self):
        return {
            "Response": "True",
            "Title": "Test Movie",
            "Year": "2026",
            "Genre": "Drama",
            "Director": "Test Director",
            "Actors": "Actor One, Actor Two",
            "Plot": "A test movie.",
            "imdbRating": "8.0",
            "imdbVotes": "100",
            "Poster": "https://example.com/poster.jpg",
            "imdbID": "tt1234567",
            "Type": "movie",
        }


def test_get_movie(monkeypatch):
    def fake_get(*args, **kwargs):
        assert kwargs["params"]["t"] == "Test Movie"
        return FakeResponse()

    monkeypatch.setattr(
        "services.release_service.requests.get",
        fake_get,
    )
    monkeypatch.setattr(
        "services.release_service.OMDB_API_KEY",
        "test-api-key",
    )

    service = ReleaseService()
    movie = service.get_movie("Test Movie")

    assert movie is not None
    assert movie["title"] == "Test Movie"
    assert movie["year"] == "2026"
    assert movie["imdb_rating"] == "8.0"
    assert movie["imdb_id"] == "tt1234567"
    assert movie["type"] == "movie"


def test_get_movie_returns_none_without_api_key(monkeypatch):
    monkeypatch.setattr(
        "services.release_service.OMDB_API_KEY",
        "",
    )

    service = ReleaseService()

    assert service.get_movie("Test Movie") is None


def test_get_movie_returns_none_when_not_found(monkeypatch):
    class NotFoundResponse:
        def raise_for_status(self):
            pass

        def json(self):
            return {"Response": "False", "Error": "Movie not found!"}

    monkeypatch.setattr(
        "services.release_service.OMDB_API_KEY",
        "test-api-key",
    )
    monkeypatch.setattr(
        "services.release_service.requests.get",
        lambda *args, **kwargs: NotFoundResponse(),
    )

    service = ReleaseService()

    assert service.get_movie("Unknown Movie") is None
