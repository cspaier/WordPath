import re
import time
import json


class NearestWords:

    def __init__(self):
        self.preloaded = json.load(open("preload.json", "r"))

    # return a list of all words wich have 1 letter different
    def fetch_nearest_words(self, word, word_list):

        similarWords = []

        # index for all letters in word
        for i in range(len(word)):
            # create a regex object:
            # replace the letter at the I position by a .
            # in regex, . means all letters

            r = re.compile(f"{word[:i]}.{word[i+1:]}")

            similarWords += [
                line for line in word_list if r.match(line) and line != word
            ]

        self.preloaded = similarWords

        return similarWords

    def get_nearest_words(self, word, banned_words):

        return [word for word in self.preloaded[word] if word not in banned_words]

    def load(self, words):
        print("Loading nearest words ...")
        starting = time.time()
        word_data = {
            loading_word: self.fetch_nearest_words(loading_word, words)
            for loading_word in words
        }

        with open("preload.json", "w") as file:
            json.dump(word_data, file)

        print(
            f"{len(word_data)} nearest words loaded in {str(round(time.time() - starting, 3))} seconds"
        )

        print("Now starting the server")
