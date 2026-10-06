"""Football provider interface."""

from abc import ABC, abstractmethod


class FootballProvider(ABC):
    """Base interface for football data providers."""

    @abstractmethod
    def get_live_matches(self) -> list[dict]:
        """Return live football matches."""

        raise NotImplementedError
