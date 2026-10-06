from services.football_team_mapper import (
    FootballTeamMapper,
)


def test_map_api_football_team_id():
    assert (
        FootballTeamMapper.get_internal_id(
            "api_football",
            529,
        )
        == 2
    )

    assert (
        FootballTeamMapper.get_internal_id(
            "api_football",
            541,
        )
        == 1
    )


def test_map_team_by_name():
    assert (
        FootballTeamMapper.get_internal_id(
            "varzesh3",
            None,
            "Barcelona",
        )
        == 2
    )


def test_unknown_team_returns_none():
    assert (
        FootballTeamMapper.get_internal_id(
            "api_football",
            999999,
        )
        is None
    )


def test_map_varzesh3_team_name():
    assert (
        FootballTeamMapper.get_internal_id(
            "varzesh3",
            None,
            "بارسلونا",
        )
        == 2
    )

    assert (
        FootballTeamMapper.get_internal_id(
            "varzesh3",
            None,
            "رئال مادرید",
        )
        == 1
    )
