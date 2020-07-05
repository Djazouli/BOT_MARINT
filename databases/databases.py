from tinydb import TinyDB
import os
import pickle

db_messages = None
db_quotes = None
db_ranking = TinyDB(os.path.join("databases", "ranking.json"))
markov_path = os.path.join("databases", "markov.pk")

def get_quotes_db():
    global db_quotes
    if db_quotes is None:
        db_quotes = TinyDB(os.path.join("databases", "quotes.json"))
    return db_quotes

def get_messages_db():
    global db_messages
    if db_messages is None:
        db_messages = TinyDB(os.path.join("databases", "quotes.json"))
    return db_messages

def get_ranking_db():
    """
    Ranking db is a list of item: {id, name, current_streak, best_streak, played, won}
    :return:
    """
    return db_ranking

def load_markov_chains():
    try:
        with open(markov_path, "rb") as f:
            return pickle.load(f)
    except Exception:
        return None

def save_markov_chains(markov_chains):
    with open(markov_path, "wb+") as f:
        pickle.dump(markov_chains, f)
    return