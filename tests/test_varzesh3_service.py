from services.varzesh3_service import Varzesh3Provider


def test_parse_scheduled_match():
    html = """
    <div>
        <time>22:15</time>

        <a href="/football/match/497731/test">
            <div>
                <img alt="کرواسی">
                <span>کرواسی</span>
            </div>

            <div>
                <span></span>
                <span>-</span>
                <span></span>
            </div>

            <div>
                <img alt="اسپانیا">
                <span>اسپانیا</span>
            </div>
        </a>
    </div>
    """

    from bs4 import BeautifulSoup

    soup = BeautifulSoup(html, "html.parser")
    link = soup.find("a")

    provider = Varzesh3Provider()

    result = provider._parse_match_link(link)

    assert result["status"] == "scheduled"
    assert result["home_team"] == "کرواسی"
    assert result["away_team"] == "اسپانیا"
    assert result["home_score"] is None
    assert result["away_score"] is None


def test_parse_finished_match():
    html = """
    <div>
        <time>01:30</time>

        <span>نتیجه نهایی</span>

        <a href="/football/match/498043/test">
            <div>
                <img alt="استودیانتس">
                <span>استودیانتس</span>
            </div>

            <div>
                <span>3</span>
                <span>-</span>
                <span>0</span>
            </div>

            <div>
                <img alt="جیمناسیا مندوزا">
                <span>جیمناسیا مندوزا</span>
            </div>
        </a>
    </div>
    """

    from bs4 import BeautifulSoup

    soup = BeautifulSoup(html, "html.parser")
    link = soup.find("a")

    provider = Varzesh3Provider()

    result = provider._parse_match_link(link)

    assert result["status"] == "finished"
    assert result["home_team"] == "استودیانتس"
    assert result["away_team"] == "جیمناسیا مندوزا"
    assert result["home_score"] == 3
    assert result["away_score"] == 0
def test_parse_goal_events():
    html = """
    <div>
        <div style="--event: penalty">
            <span>83'</span>

            <div>
                <img alt="گل پنالتی">

                <span>
                    <span>
                        <span>1</span>
                        <span>-</span>
                        <span>0</span>
                    </span>
                </span>

                <span>ستری</span>
                <span>-</span>
                <span>گل پنالتی</span>
            </div>
        </div>

        <div style="--event: goal">
            <span>90'</span>

            <div>
                <img alt="گل به خودی">

                <span>
                    <span>
                        <span>2</span>
                        <span>-</span>
                        <span>0</span>
                    </span>
                </span>

                <span>Perez F.</span>
            </div>
        </div>
    </div>
    """

    from bs4 import BeautifulSoup

    soup = BeautifulSoup(
        html,
        "html.parser",
    )

    provider = Varzesh3Provider()

    events = provider._parse_events(soup)

    assert len(events) == 2

    assert events[0]["minute"] == "83"
    assert events[0]["type"] == "penalty_goal"
    assert events[0]["player"] == "ستری"

    assert events[1]["minute"] == "90"
    assert events[1]["type"] == "own_goal"
    assert events[1]["player"] == "Perez F."


def test_parse_red_card_event():
    html = """
    <div>
        <div style="--event: red-card">
            <span>72'</span>

            <div>
                <img alt="کارت قرمز">
                <span>Player Name</span>
            </div>
        </div>
    </div>
    """

    from bs4 import BeautifulSoup

    soup = BeautifulSoup(
        html,
        "html.parser",
    )

    provider = Varzesh3Provider()

    events = provider._parse_events(soup)

    assert len(events) == 1

    assert events[0] == {
        "minute": "72",
        "type": "red_card",
        "player": "Player Name",
    }