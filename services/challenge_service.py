"""Daily challenge service."""

import json
import random
from pathlib import Path


class ChallengeService:

    def __init__(self):
        self.file = Path("data/challenges.json")


    def get_question(self):

        with open(
            self.file,
            "r",
            encoding="utf-8"
        ) as f:
            questions = json.load(f)

        return random.choice(questions)