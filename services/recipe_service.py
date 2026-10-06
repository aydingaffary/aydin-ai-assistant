import json
import random
from pathlib import Path


class RecipeService:
    """Recipe suggestion service."""

    def __init__(self):
        self.file_path = Path("data/recipes.json")

    def _load_recipes(self):
        with open(
            self.file_path,
            "r",
            encoding="utf-8",
        ) as file:
            return json.load(file)

    def get_recipe(self, exclude=None):
        recipes = self._load_recipes()

        if exclude:
            recipes = [r for r in recipes if r["name"] != exclude]

        return random.choice(recipes)
