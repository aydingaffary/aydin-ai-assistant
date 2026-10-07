"""Daily challenge service."""

import json
import random

from datetime import datetime, timedelta
from pathlib import Path


class ChallengeService:

    def __init__(self):

        self.file = Path("data/challenges.json")

        self.users_file = Path("data/challenge_users.json")

    def get_question(self):

        with open(self.file, "r", encoding="utf-8") as f:

            questions = json.load(f)

        return random.choice(questions)

    def load_users(self):

        if not self.users_file.exists():

            return []

        with open(self.users_file, "r", encoding="utf-8") as f:

            return json.load(f)

    def save_users(self, users):

        with open(self.users_file, "w", encoding="utf-8") as f:

            json.dump(
                users,
                f,
                ensure_ascii=False,
                indent=2,
            )

    def get_user(self, user_id):

        users = self.load_users()

        for user in users:

            if user["user_id"] == user_id:

                return user

        new_user = {
            "user_id": user_id,
            "username": None,
            "score": 0,
            "best_score": 0,
            "total_questions": 0,
            "correct_answers": 0,
            "wrong_answers": 0,
            "daily_streak": 0,
            "correct_streak": 0,
            "last_visit": None,
        }

        users.append(new_user)

        self.save_users(users)

        return new_user

    def update_visit(self, user_id):

        users = self.load_users()

        today = datetime.now().date()

        result = None

        for user in users:

            if user["user_id"] == user_id:

                last = user.get("last_visit")

                if last:

                    last_date = datetime.strptime(last, "%Y-%m-%d").date()

                    if last_date == today:

                        pass

                    elif last_date == today - timedelta(days=1):

                        user["daily_streak"] += 1

                    else:

                        user["daily_streak"] = 1

                else:

                    user["daily_streak"] = 1

                user["last_visit"] = str(today)

                result = user

        self.save_users(users)

        if result is None:

            return self.get_user(user_id)

        return result

    def correct_answer(self, user_id):

        users = self.load_users()

        for user in users:

            if user["user_id"] == user_id:

                user["score"] += 10

                user["correct_streak"] += 1

                user["total_questions"] = user.get("total_questions", 0) + 1

                user["correct_answers"] = user.get("correct_answers", 0) + 1

                if user["score"] > user.get("best_score", 0):

                    user["best_score"] = user["score"]

                self.save_users(users)

                return user

    def wrong_answer(self, user_id):

        users = self.load_users()

        for user in users:

            if user["user_id"] == user_id:

                user["score"] = max(0, user["score"] - 5)

                user["correct_streak"] = 0

                user["total_questions"] = user.get("total_questions", 0) + 1

                user["wrong_answers"] = user.get("wrong_answers", 0) + 1

                self.save_users(users)

                return user

    def leaderboard(self, limit=10):

        users = self.load_users()

        users.sort(key=lambda x: x.get("score", 0), reverse=True)

        return users[:limit]

    def has_username(self, user_id):

        users = self.load_users()

        for user in users:

            if user["user_id"] == user_id:

                return bool(user.get("username"))

        return False

    def save_username(self, user_id, username):

        users = self.load_users()

        for user in users:

            if user["user_id"] == user_id:

                user["username"] = username

                self.save_users(users)

                return user

        new_user = {
            "user_id": user_id,
            "username": username,
            "score": 0,
            "best_score": 0,
            "total_questions": 0,
            "correct_answers": 0,
            "wrong_answers": 0,
            "daily_streak": 0,
            "correct_streak": 0,
            "last_visit": None,
        }

        users.append(new_user)

        self.save_users(users)

        return new_user

    def get_rank(self, user_id):

        users = self.load_users()

        users.sort(key=lambda x: x.get("score", 0), reverse=True)

        for index, user in enumerate(users):

            if user["user_id"] == user_id:

                return index + 1

        return None

    def get_medal(self, score):

        if score >= 500:

            return "🥇 طلایی"

        if score >= 200:

            return "🥈 نقره‌ای"

        return "🥉 برنزی"
