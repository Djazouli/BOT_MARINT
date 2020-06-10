import random
import re
from tinydb import TinyDB, Query
from databases.databases import save_markov_chains, load_markov_chains

class MarkovChainer(object):
    def __init__(self, order):
        self.order = order
        self.beginnings = []
        self.freq = {}

    # pass a string with a terminator to the function to add it to the markov lists.
    def add_sentence(self, string, terminator="."):
        data = "".join(string)
        words = data.split()
        buf = []
        if len(words) > self.order:
            words.append(terminator)
            self.beginnings.append(words[0:self.order])
        else:
            pass

        for word in words:
            buf.append(word)
            if len(buf) == self.order + 1:
                mykey = (buf[0], buf[-2])
                if mykey in self.freq:
                    self.freq[mykey].append(buf[-1])
                else:
                    self.freq[mykey] = [buf[-1]]
                buf.pop(0)
            else:
                continue
        return

    def add_text(self, text):
        text = re.sub(r'\n\s*\n/m', ".", text)
        seps = '([.!?;:])'
        pieces = re.split(seps, text)
        sentence = ""
        for piece in pieces:
            if piece != "":
                if re.search(seps, piece):
                    self.add_sentence(sentence, piece)
                    sentence = ""
                else:
                    sentence = piece

    # Generate the goofy sentences that become your tweet.
    def generate_sentence(self):
        res = random.choice(self.beginnings)
        res = res[:]
        if len(res) == self.order:
            nw = True
            while nw is not None:
                restup = (res[-2], res[-1])
                try:
                    nw = self.next_word_for(restup)
                    if nw is not None:
                        res.append(nw)
                    else:
                        continue
                except Exception:
                    nw = False
                if len(res) > 50:
                    print(f"Broke on {res}")
                    return self.generate_sentence()
            new_res = res[0:-1]
            sentence = " ".join(new_res)
            sentence += ("" if res[-1] in ".!?;:" else " "+res[-1])

        else:
            sentence = None
        return sentence

    def next_word_for(self, words):
        try:
            arr = self.freq[words]
            next_words = random.choice(arr)
            return next_words
        except Exception:
            return None


def filter_status(text):
    text = re.sub(r'\b(RT|MT) .+', '', text)  # take out anything after RT or MT
    text = re.sub(r'(\#|@|(h\/t)|(http))\S+', '', text)  # Take out URLs, hashtags, hts, etc.
    text = re.sub('\s+', ' ', text)  # collaspse consecutive whitespace to single spaces.
    text = re.sub(r'\"|\(|\)', '', text)  # take out quotes.
    text = re.sub(r'\s+\(?(via|says)\s@\w+\)?', '', text)  # remove attribution
    text = re.sub(r'<[^>]*>','', text) #strip out html tags from mastodon posts
    text = re.sub(r'\xe9', 'e', text)  # take out accented e
    text = re.sub(r'[<>]', '', text)
    return text

def feed_marchov_chains(markov_chain):
    db = TinyDB("db_message.json")
    message = Query()
    messages = db.search(message.author.id == "142438297845628928")
    source_statuses = [filter_status(message.get("content")) for message in messages]
    for status in source_statuses:
        #if not re.search('([\.\!\?\"\']$)', status):
            #status += "."
        markov_chain.add_sentence(status, ".")
    print(f"Markov chain order {markov_chain.order}")
    for x in range(0, 10):
        ebook_status = markov_chain.generate_sentence()
        print(ebook_status)

def generate_markov_chains():
    markov_chains = load_markov_chains()
    if markov_chains is not None:
        return markov_chains
    markov_chains = {} #user_name: markov_chain
    id_matching = {}
    data_per_user = {} #user_id: list of string (messages)
    db = TinyDB("databases/db_message.json")
    messages = db.all()

    for message in messages:
        author_id = message.get("author").get("id")
        user_message = data_per_user.get(author_id, [])
        user_message.append(filter_status(message.get("content")))
        data_per_user[author_id] = user_message
        if not author_id in id_matching.keys():
            id_matching[author_id] = message.get("author").get("username")

    for user_id, user_data in data_per_user.items():
        user_name = id_matching[user_id]
        if len(user_data) < 1000:
            print(f"Not enough data for {user_name}")
            continue
        markov_chain = MarkovChainer(2)
        for message in user_data:
            markov_chain.add_sentence(message)
        markov_chains[user_name] = markov_chain
    save_markov_chains(markov_chains)


    return markov_chains