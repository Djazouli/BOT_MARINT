from databases.databases import get_ranking_db
from tinydb import Query

class User():
    def __init__(self, author):
        self.name = author.name
        self.id = author.id
        ranking_db = get_ranking_db()
        user = Query()
        user = ranking_db.search(user.discord_id == author.id)
        if not user:
            ranking_db.insert({
                "discord_id": author.id,
                "current_streak": 0,
                "best_streak": 0,
                "played": 0,
                "won": 0,
                "name": author.name,
            })
            user = Query()
            user = ranking_db.search(user.discord_id == author.id)
        assert len(user) == 1
        user = user[0]
        self.db_id = user.doc_id
        self.current_streak = user.get("current_streak")
        self.best_streak = user.get("best_streak")
        self.current_guess = None
        self.current_sentence = None

    def set_current_streak(self, n):
        self.current_streak = n
        if n > self.best_streak:
            self.best_streak = n
        ranking_db = get_ranking_db()
        ranking_db.update({"current_streak": n, "best_streak": self.best_streak}, doc_ids=[self.db_id])

    def increment_played(self) -> int:
        # lol those two functions...
        ranking_db = get_ranking_db()
        user = ranking_db.get(doc_id=self.db_id)
        played = user.get("played", 0)
        ranking_db.update({"played": played + 1}, doc_ids=[self.db_id])
        return played + 1

    def increment_won(self) -> int:
        ranking_db = get_ranking_db()
        user = ranking_db.get(doc_id=self.db_id)
        won = user.get("won", 0)
        ranking_db.update({"won": won + 1}, doc_ids=[self.db_id])
        return won + 1