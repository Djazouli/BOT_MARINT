from tinydb import TinyDB
import os#
import pickle

db_messages = TinyDB(os.path.join("databases", "db_message.json"))
db_quotes = TinyDB(os.path.join("databases", "quotes.json"))
markov_path = os.path.join("databases", "markov.pk")

def get_quotes_db():
    return db_quotes

def get_messages_db():
    return db_messages

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